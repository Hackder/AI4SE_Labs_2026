"""End-to-end run of the graph with the fake LLM on the real corpus."""

import asyncio
import json
import re
from pathlib import Path

from req_refinery.main import run_pipeline
from req_refinery.state import TraceRecord
from tests.fake_llm import FakeLLM

CORPUS = Path(__file__).resolve().parents[2] / "data" / "corpus"
NODES = {
    "load_corpus",
    "extract",
    "merge_dedup",
    "assign_unassigned",
    "document_pass[coverage]",
    "apply_document_pass[coverage]",
    "prioritize",
    "assign_ids",
    "review",
    "group_issues",
    "resolve_issue",
    "apply_resolutions",
    "document_pass[attribution]",
    "apply_document_pass[attribution]",
    "render",
}


def test_graph_end_to_end_with_fake_llm(tmp_path: Path) -> None:
    files = [p for p in CORPUS.rglob("*") if p.is_file()]
    state, run_dir = asyncio.run(run_pipeline(CORPUS, tmp_path, FakeLLM()))

    assert len(state["documents"]) == len(files)

    ids = [r.id for r in state["requirements"]]
    assert all(ids) and len(set(ids)) == len(ids)
    assert all(r.priority in {"High", "Medium", "Low"} for r in state["requirements"])

    assert state["round"] == 2
    assert state["blacklist"]
    assert not re.search(r"\bR\d+\b", state["blacklist"][0].reason)

    md = tmp_path / "network" / "requirements.md"
    js = tmp_path / "network" / "requirements.json"
    assert md.is_file() and js.is_file()
    assert (run_dir / "requirements.md").is_file()
    data = json.loads(js.read_text(encoding="utf-8"))
    assert len(data["requirements"]) == len(state["requirements"])

    records = [
        TraceRecord.model_validate_json(line)
        for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert NODES <= {r.node for r in records}
    placed = next(r for r in records if r.node == "assign_unassigned")
    assert (placed.payload["candidates"], placed.payload["mapped"], placed.payload["new"]) == (
        2,
        1,
        1,
    )
    apply = next(r for r in records if r.node == "apply_resolutions")
    assert len(apply.payload["id_substitutions"]) == 1

    # round 1: two issues overlapping on one requirement form one group (-3 +1),
    # a too_narrow pair forms a second group (-2 +1)
    group = next(r for r in records if r.node == "group_issues")
    assert (group.payload["issues"], group.payload["groups"]) == (3, 2)
    assert group.payload["largest_group_issues"] == 2
    assert sum(1 for r in records if r.node == "resolve_issue") == 2
    before = next(r for r in records if r.node == "assign_ids").payload["outputs"]
    assert apply.payload["outputs"]["requirement_count"] == len(before) - 3 + 1 - 2 + 1
    parent, detail = before[3], before[4]
    absorbed = next(r for r in state["requirements"] if r.name == f"{parent['name']} with detail")
    # the folded requirement keeps both sides' documents (both are mentioned in its text)
    assert set(absorbed.source_doc_ids) == {*parent["source_doc_ids"], *detail["source_doc_ids"]}
    # attribution pass: sources become exactly the supporting documents ...
    for r in state["requirements"]:
        if r.name != "Missed export":
            assert all(d in r.description for d in r.source_doc_ids)
    # ... an item no document supports keeps its sources and is flagged ...
    missed = next(r for r in state["requirements"] if r.name == "Missed export")
    assert missed.source_doc_ids == ["D01"]
    assert missed.origin == "coverage"
    unverified = [i for i in state["open_issues"] if i.type == "sources_unverified"]
    assert [i.requirement_ids for i in unverified] == [[missed.id]]
    # ... and a late missed item is reported, not inserted
    assert not any(r.name == "Late find" for r in state["requirements"])
    late = [i for i in state["open_issues"] if i.type == "possibly_missed"]
    assert len(late) == 1 and "Late find" in late[0].explanation
    stats = state["attribution_stats"]
    assert stats["citations_removed"] >= 1 and stats["sources_unverified"] == 1
    assert data["metadata"]["source_attribution"] == stats
    rendered = md.read_text(encoding="utf-8")
    # the source priority note travels in its own field and is shown with the priority
    noted = [r for r in state["requirements"] if r.source_priority_note]
    assert noted and all("marks this" not in r.description for r in state["requirements"])
    assert f"({noted[0].source_priority_note})" in rendered
    assert any(r["source_priority_note"] for r in data["requirements"])
    assert "sources unverified" in rendered and "possibly missed" in rendered
    names = {r.node for r in records}
    assert {"document_pass[coverage]", "document_pass[attribution]"} <= names
    assert absorbed.origin == "folded"
    assert len(state["blacklist"]) == 1
    names = [r.name for r in state["requirements"]]
    descriptions = [r.description for r in state["requirements"]]
    assert len(set(names)) == len(names)
    assert len(set(descriptions)) == len(descriptions)
    origins = {r.origin for r in state["requirements"]}
    assert {"merge", "unassigned", "coverage", "resolved"} <= origins
    assert all(r["origin"] for r in data["requirements"])
    assert not re.search(r"\borigin\b", md.read_text(encoding="utf-8"))
    assert any((run_dir / "state").iterdir())

    text = md.read_text(encoding="utf-8")
    coverage = text.split("## Coverage", 1)[1].strip().splitlines()[2:]
    assert len(coverage) == len(state["documents"])
    assert len(data["coverage"]) == len(state["documents"])
