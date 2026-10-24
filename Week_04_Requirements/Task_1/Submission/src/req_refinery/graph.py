"""LangGraph graph assembly."""

from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send

from req_refinery.nodes.assign_ids import assign_ids
from req_refinery.nodes.assign_unassigned import assign_unassigned
from req_refinery.nodes.consolidate import consolidate
from req_refinery.nodes.document_pass import apply_document_pass, document_pass
from req_refinery.nodes.extract import extract
from req_refinery.nodes.group_issues import group_issues
from req_refinery.nodes.load import load_corpus
from req_refinery.nodes.merge import merge_dedup
from req_refinery.nodes.prioritize import prioritize
from req_refinery.nodes.render import render
from req_refinery.nodes.resolve import apply_resolutions, resolve_issue
from req_refinery.nodes.review import review
from req_refinery.state import DocumentTask, GraphName, GraphState, IssueTask, PassMode
from req_refinery.trace import Deps, NodeImpl, traced


def fan_out_extract(state: GraphState) -> list[Send]:
    return [
        Send(
            "extract",
            DocumentTask(document=d, requirements=[], round=state["round"], mode="coverage"),
        )
        for d in state["documents"]
    ]


def fan_out_document_pass(mode: PassMode) -> Callable[[GraphState], list[Send]]:
    def fan_out(state: GraphState) -> list[Send]:
        return [
            Send(
                f"document_pass[{mode}]",
                DocumentTask(
                    document=d,
                    requirements=state["requirements"],
                    round=state["round"],
                    mode=mode,
                ),
            )
            for d in state["documents"]
        ]

    return fan_out


def route_after_review(state: GraphState) -> str | list[Send]:
    if state["route"] == "targeted" and state["issues"]:
        return "group_issues"
    return fan_out_document_pass("attribution")(state)


def fan_out_resolve(state: GraphState) -> str | list[Send]:
    if not state["issue_groups"]:
        return fan_out_document_pass("attribution")(state)
    by_id = {r.id: r for r in state["requirements"]}
    return [
        Send(
            "resolve_issue",
            IssueTask(
                issues=group.issues,
                requirements=[by_id[i] for i in group.requirement_ids],
                glossary=state["glossary"],
                round=state["round"],
            ),
        )
        for group in state["issue_groups"]
    ]


def build_graph(
    deps: Deps, name: GraphName = "network"
) -> CompiledStateGraph[GraphState, None, GraphState, GraphState]:
    """network: per-document extract, merge_dedup, assign_unassigned, coverage pass.
    hybrid: per-document extract, one whole-corpus consolidate call, assign_unassigned,
    no coverage pass (the consolidator saw every document). Both share the review loop,
    the attribution pass and render."""
    g = StateGraph(GraphState)

    def node(node_name: str, impl: NodeImpl[Any]) -> None:
        _ = g.add_node(node_name, traced(node_name, impl, deps))

    node("load_corpus", load_corpus)
    node("extract", extract)
    node("assign_unassigned", assign_unassigned)
    node("document_pass[attribution]", document_pass)
    node("apply_document_pass[attribution]", apply_document_pass("attribution"))
    node("prioritize", prioritize)
    node("assign_ids", assign_ids)
    node("review", review)
    node("group_issues", group_issues)
    node("resolve_issue", resolve_issue)
    node("apply_resolutions", apply_resolutions)
    node("render", render)

    _ = g.add_edge(START, "load_corpus")
    _ = g.add_conditional_edges("load_corpus", fan_out_extract, ["extract"])
    if name == "network":
        node("merge_dedup", merge_dedup)
        node("document_pass[coverage]", document_pass)
        node("apply_document_pass[coverage]", apply_document_pass("coverage"))
        _ = g.add_edge("extract", "merge_dedup")
        _ = g.add_edge("merge_dedup", "assign_unassigned")
        _ = g.add_conditional_edges(
            "assign_unassigned", fan_out_document_pass("coverage"), ["document_pass[coverage]"]
        )
        _ = g.add_edge("document_pass[coverage]", "apply_document_pass[coverage]")
        _ = g.add_edge("apply_document_pass[coverage]", "prioritize")
    else:
        node("consolidate", consolidate)
        _ = g.add_edge("extract", "consolidate")
        _ = g.add_edge("consolidate", "assign_unassigned")
        _ = g.add_edge("assign_unassigned", "prioritize")
    _ = g.add_edge("prioritize", "assign_ids")
    _ = g.add_edge("assign_ids", "review")
    after_loop = ["document_pass[attribution]"]
    _ = g.add_conditional_edges("review", route_after_review, ["group_issues", *after_loop])
    _ = g.add_conditional_edges("group_issues", fan_out_resolve, ["resolve_issue", *after_loop])
    _ = g.add_edge("resolve_issue", "apply_resolutions")
    _ = g.add_edge("apply_resolutions", "prioritize")
    _ = g.add_edge("document_pass[attribution]", "apply_document_pass[attribution]")
    _ = g.add_edge("apply_document_pass[attribution]", "render")
    _ = g.add_edge("render", END)
    return g.compile()
