"""End-to-end run of the hybrid graph with the fake LLM on the real corpus."""

import asyncio
import json
from pathlib import Path

from req_refinery.main import run_pipeline
from req_refinery.state import TraceRecord
from tests.fake_llm import FakeLLM

CORPUS = Path(__file__).resolve().parents[2] / "data" / "corpus"


def test_hybrid_graph_end_to_end_with_fake_llm(tmp_path: Path) -> None:
    state, run_dir = asyncio.run(run_pipeline(CORPUS, tmp_path, FakeLLM(), graph_name="hybrid"))

    assert run_dir.name.endswith("_hybrid")
    assert state["graph"] == "hybrid"
    md = tmp_path / "hybrid" / "requirements.md"
    js = tmp_path / "hybrid" / "requirements.json"
    assert md.is_file() and js.is_file()
    assert not (tmp_path / "requirements.md").exists()

    records = [
        TraceRecord.model_validate_json(line)
        for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    nodes = {r.node for r in records}
    assert {"consolidate", "assign_unassigned", "document_pass[attribution]", "render"} <= nodes
    assert not nodes & {"merge_dedup", "document_pass[coverage]"}
    assert next(r for r in records if r.node == "load_corpus").payload["inputs"]["graph"] == (
        "hybrid"
    )

    cons = next(r for r in records if r.node == "consolidate").payload
    assert (cons["unassigned_candidates"], cons["blacklist_out"], cons["open_questions"]) == (
        2,
        1,
        1,
    )
    assert "skipped" in cons["coverage_pass"]
    placed = next(r for r in records if r.node == "assign_unassigned").payload
    assert placed["candidates"] == 2

    ids = [r.id for r in state["requirements"]]
    assert all(ids) and len(set(ids)) == len(ids)
    assert any(b.requirement.origin == "consolidate" for b in state["blacklist"])

    text = md.read_text(encoding="utf-8")
    open_issues = text.split("## Open issues", 1)[1]
    assert open_issues.index("### Stakeholder questions") < open_issues.index("## Coverage")
    assert "Which metric defines capacity? (D02, D03)" in open_issues
    data = json.loads(js.read_text(encoding="utf-8"))
    assert data["metadata"]["graph"] == "hybrid"
    assert data["open_questions"] == [
        {"question": "Which metric defines capacity?", "doc_ids": ["D02", "D03"]}
    ]
