"""Unit tests for the deterministic issue grouping node."""

import asyncio
from pathlib import Path

from req_refinery.nodes.group_issues import group_issues
from req_refinery.state import Issue, Requirement, initial_state
from req_refinery.trace import Deps, TraceWriter
from tests.fake_llm import FakeLLM


def _req(rid: str, origin: str) -> Requirement:
    return Requirement.model_validate(
        {"id": rid, "name": rid, "description": rid, "source_doc_ids": ["D01"], "origin": origin}
    )


def test_too_broad_on_split_requirement_is_dropped(tmp_path: Path) -> None:
    state = initial_state("in", str(tmp_path), str(tmp_path), None, 5)
    state["requirements"] = [_req("R01", "split"), _req("R02", "merge"), _req("R03", "merge")]
    state["issues"] = [
        Issue(type="too_broad", requirement_ids=["R01"], explanation="x"),
        Issue(type="too_broad", requirement_ids=["R02"], explanation="x"),
        Issue(type="duplicate", requirement_ids=["R01", "R03"], explanation="x"),
    ]
    deps = Deps(llm=FakeLLM(), tracer=TraceWriter(tmp_path / "trace.jsonl"))
    result = asyncio.run(group_issues(state, deps))
    assert result.payload["dropped_granularity_issues"] == 1
    assert len(result.update["issue_groups"]) == 2


def test_all_dropped_finishes_as_accept(tmp_path: Path) -> None:
    state = initial_state("in", str(tmp_path), str(tmp_path), None, 5)
    state["requirements"] = [_req("R01", "split")]
    state["issues"] = [Issue(type="too_broad", requirement_ids=["R01"], explanation="x")]
    deps = Deps(llm=FakeLLM(), tracer=TraceWriter(tmp_path / "trace.jsonl"))
    result = asyncio.run(group_issues(state, deps))
    assert result.update["route"] == "accept"
    assert len(result.update["open_issues"]) == 1


def test_granularity_issues_on_folded_items_are_dropped(tmp_path: Path) -> None:
    state = initial_state("in", str(tmp_path), str(tmp_path), None, 5)
    state["requirements"] = [_req("R01", "folded"), _req("R02", "merge"), _req("R03", "merge")]
    state["issues"] = [
        Issue(type="too_narrow", requirement_ids=["R02", "R01"], explanation="x"),
        Issue(type="too_broad", requirement_ids=["R01"], explanation="x"),
        Issue(type="too_narrow", requirement_ids=["R02", "R03"], explanation="x"),
        Issue(type="duplicate", requirement_ids=["R01", "R03"], explanation="x"),
    ]
    deps = Deps(llm=FakeLLM(), tracer=TraceWriter(tmp_path / "trace.jsonl"))
    result = asyncio.run(group_issues(state, deps))
    assert result.payload["dropped_granularity_issues"] == 2
    assert [i.type for i in result.update["issues"]] == ["too_narrow", "duplicate"]
