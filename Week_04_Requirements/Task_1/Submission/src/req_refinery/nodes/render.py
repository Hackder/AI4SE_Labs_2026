"""Deterministic node that writes requirements.md and requirements.json."""

import json
import shutil
from pathlib import Path
from typing import Any

from req_refinery.config import PRIORITY_SCALE
from req_refinery.state import BlacklistEntry, Document, GraphState, Requirement
from req_refinery.trace import Deps, NodeResult, now_iso


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _sources(req: Requirement, docs: dict[str, Document]) -> str:
    return ", ".join(f"{d} ({docs[d].path})" for d in req.source_doc_ids)


def _entry(heading: str, req: Requirement, docs: dict[str, Document]) -> list[str]:
    lines = [f"### {heading}  {req.name}", ""]
    if req.priority is not None:
        justification = f" {req.priority_justification}" if req.priority_justification else ""
        if req.source_priority_note:
            justification += f" ({req.source_priority_note})"
        lines += [f"**Priority:** {req.priority}.{justification}", ""]
    lines += [req.description, "", f"**Sources:** {_sources(req, docs)}", ""]
    return lines


def _blacklist_ids(blacklist: list[BlacklistEntry]) -> list[str]:
    width = max(2, len(str(len(blacklist))))
    return [f"B{i:0{width}d}" for i in range(1, len(blacklist) + 1)]


def render_markdown(state: GraphState) -> str:
    docs = {d.id: d for d in state["documents"]}
    reqs = state["requirements"]
    blacklist = state["blacklist"]
    b_ids = _blacklist_ids(blacklist)
    system = state["system_name"] or "the software system described by the input corpus"
    out: list[str] = [
        "# Software Requirements Specification",
        "",
        (
            f"This document specifies the requirements for {system}, derived by an "
            f"agentic refinement network from {len(docs)} input documents. It contains "
            f"{len(reqs)} requirements and {len(blacklist)} blacklisted (discarded) items. "
            "Requirement numbers are assigned in document order, are unique within this "
            "document and are not stable across runs."
        ),
        "",
        "## Input documents",
        "",
    ]
    out += [f"{i}. {d.id} — {d.path}" for i, d in enumerate(docs.values(), start=1)]
    out += ["", "## Priority scale", ""]
    out += [f"- **{k}:** {v}" for k, v in PRIORITY_SCALE.items()]
    out += ["", "## Glossary", "", "| Term | Definition |", "| --- | --- |"]
    out += [f"| {_cell(g.term)} | {_cell(g.definition)} |" for g in state["glossary"]]
    out += [""]
    for level in PRIORITY_SCALE:
        out += [f"## Requirements: {level} priority", ""]
        level_reqs = [r for r in reqs if r.priority == level]
        if not level_reqs:
            out += ["None.", ""]
        for r in level_reqs:
            out += _entry(r.id or "R??", r, docs)
    out += ["## Blacklist", ""]
    if not blacklist:
        out += ["None.", ""]
    for b_id, entry in zip(b_ids, blacklist, strict=True):
        out += _entry(b_id, entry.requirement, docs)
        out += [f"**Reason:** {entry.reason}", ""]
    if state["open_questions"] or state["open_issues"]:
        out += ["## Open issues", ""]
    if state["open_questions"]:
        out += ["### Stakeholder questions", ""]
        out += [
            f"- {q.question}" + (f" ({', '.join(q.doc_ids)})" if q.doc_ids else "")
            for q in state["open_questions"]
        ]
        out += [""]
    if state["open_issues"]:
        if state["open_questions"]:
            out += ["### Review issues", ""]
        out += [
            f"- **{i.type.replace('_', ' ')}**"
            + (f" ({', '.join(i.requirement_ids)})" if i.requirement_ids else "")
            + f": {i.explanation}"
            for i in state["open_issues"]
        ]
        out += [""]
    out += [
        "## Coverage",
        "",
        "| Document | Path | Requirements | Blacklist |",
        "| --- | --- | --- | --- |",
    ]
    for row in coverage_rows(state):
        out.append(
            f"| {row['document']} | {_cell(row['path'])} | "
            f"{', '.join(row['requirements'])} | {', '.join(row['blacklist'])} |"
        )
    return "\n".join(out).rstrip() + "\n"


def coverage_rows(state: GraphState) -> list[dict[str, Any]]:
    b_ids = _blacklist_ids(state["blacklist"])
    rows: list[dict[str, Any]] = []
    for d in state["documents"]:
        rows.append(
            {
                "document": d.id,
                "path": d.path,
                "requirements": [
                    r.id or "" for r in state["requirements"] if d.id in r.source_doc_ids
                ],
                "blacklist": [
                    b_id
                    for b_id, b in zip(b_ids, state["blacklist"], strict=True)
                    if d.id in b.requirement.source_doc_ids
                ],
            }
        )
    return rows


def render_json(state: GraphState, models: dict[str, str]) -> dict[str, Any]:
    b_ids = _blacklist_ids(state["blacklist"])
    return {
        "metadata": {
            "generated_at": now_iso(),
            "graph": state["graph"],
            "system_name": state["system_name"],
            "run_dir": state["run_dir"],
            "source_attribution": state["attribution_stats"],
            "models": models,
            "review_rounds": state["round"],
            "max_rounds": state["max_rounds"],
        },
        "documents": [{"id": d.id, "path": d.path} for d in state["documents"]],
        "priority_scale": PRIORITY_SCALE,
        "glossary": [g.model_dump() for g in state["glossary"]],
        "requirements": [r.model_dump() for r in state["requirements"]],
        "blacklist": [
            {"id": b_id, **b.requirement.model_dump(exclude={"id"}), "reason": b.reason}
            for b_id, b in zip(b_ids, state["blacklist"], strict=True)
        ],
        "open_questions": [q.model_dump() for q in state["open_questions"]],
        "open_issues": [i.model_dump() for i in state["open_issues"]],
        "coverage": coverage_rows(state),
    }


async def render(state: GraphState, deps: Deps) -> NodeResult:
    run_dir = Path(state["run_dir"])
    output_dir = Path(state["output_dir"])
    md_path = run_dir / "requirements.md"
    json_path = run_dir / "requirements.json"
    _ = md_path.write_text(render_markdown(state), encoding="utf-8")
    _ = json_path.write_text(
        json.dumps(render_json(state, deps.models), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    for path in (md_path, json_path):
        _ = shutil.copyfile(path, output_dir / path.name)
    return NodeResult(
        update={},
        payload={
            "inputs": {
                "requirements": len(state["requirements"]),
                "blacklist": len(state["blacklist"]),
                "open_issues": len(state["open_issues"]),
            },
            "outputs": [str(md_path), str(json_path), str(output_dir / "requirements.md")],
        },
        round=state["round"],
    )
