"""Unit tests for origin tagging and the too_broad split cap."""

import asyncio
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from req_refinery.config import MODELS
from req_refinery.llm import LLMResponse
from req_refinery.nodes.resolve import MAX_SPLIT, origin_for, resolve_issue
from req_refinery.nodes.review import SETTLED_TAG, review
from req_refinery.schemas import ReplacementOut, ResolveOutput, ReviewOutput
from req_refinery.state import Issue, IssueTask, Requirement, initial_state
from req_refinery.trace import Deps, TraceWriter


def _issue(kind: str) -> Issue:
    return Issue.model_validate({"type": kind, "requirement_ids": ["R01"], "explanation": "x"})


def test_origin_for_mixed_groups() -> None:
    assert origin_for([_issue("too_broad"), _issue("duplicate")]) == "split"
    assert origin_for([_issue("too_narrow"), _issue("conflict")]) == "folded"
    assert origin_for([_issue("too_broad"), _issue("too_narrow")]) == "granularity"
    assert origin_for([_issue("duplicate"), _issue("priority")]) == "resolved"


class OverSplitter:
    """Always splits into ten pieces, ignoring the retry message."""

    def __init__(self) -> None:
        self.calls: int = 0

    async def ainvoke(
        self, model: str, messages: Sequence[BaseMessage], schema: type[BaseModel]
    ) -> LLMResponse:
        del model, messages, schema
        self.calls += 1
        parsed = ResolveOutput(
            replacements=[
                ReplacementOut(
                    name=f"Part {n}",
                    description=f"Part {n}.",
                    source_doc_ids=[],
                    narrowing_reason=None,
                    source_priority_note=None,
                )
                for n in range(10)
            ],
            blacklist_entries=[],
        )
        return LLMResponse(parsed=parsed, raw_text="", usage={})


def test_too_broad_split_is_capped(tmp_path: Path) -> None:
    llm = OverSplitter()
    deps = Deps(llm=llm, tracer=TraceWriter(tmp_path / "t.jsonl"), models=dict(MODELS))
    req = Requirement(id="R01", name="Big", description="Big.", source_doc_ids=["D01"])
    task = IssueTask(issues=[_issue("too_broad")], requirements=[req], glossary=[], round=1)
    result = asyncio.run(resolve_issue(task, deps))
    assert llm.calls == 2
    assert result.payload["truncated_replacements"] == 10 - MAX_SPLIT
    assert len(result.update["resolutions"][0].replacements) == MAX_SPLIT
    assert result.payload["llm_calls"][1]["soft_check_failed"]


class CapturingReviewer:
    """Records the review payload and accepts."""

    def __init__(self) -> None:
        self.payload: dict[str, Any] = {}

    async def ainvoke(
        self, model: str, messages: Sequence[BaseMessage], schema: type[BaseModel]
    ) -> LLMResponse:
        del model, schema
        content = messages[1].content
        assert isinstance(content, str)
        self.payload = json.loads(content)
        return LLMResponse(parsed=ReviewOutput(issues=[], route="accept"), raw_text="", usage={})


def test_review_tags_settled_requirements(tmp_path: Path) -> None:
    llm = CapturingReviewer()
    deps = Deps(llm=llm, tracer=TraceWriter(tmp_path / "t.jsonl"), models=dict(MODELS))
    state = initial_state("in", str(tmp_path), str(tmp_path), None, 5)
    state["requirements"] = [
        Requirement(id=f"R0{n}", name=o, description=o, source_doc_ids=["D01"], origin=o)
        for n, o in enumerate(("split", "folded", "granularity", "merge", "resolved"), 1)
    ]
    _ = asyncio.run(review(state, deps))
    tags = {r["id"]: r.get("tag") for r in llm.payload["requirements"]}
    assert tags == {
        "R01": SETTLED_TAG,
        "R02": SETTLED_TAG,
        "R03": SETTLED_TAG,
        "R04": None,
        "R05": None,
    }


class NoteSplitter:
    """Splits into two pieces and sets no notes itself."""

    async def ainvoke(
        self, model: str, messages: Sequence[BaseMessage], schema: type[BaseModel]
    ) -> LLMResponse:
        del model, messages, schema
        parsed = ResolveOutput(
            replacements=[
                ReplacementOut(
                    name=f"Part {n}",
                    description=f"Part {n}.",
                    source_doc_ids=[],
                    narrowing_reason=None,
                    source_priority_note=None,
                )
                for n in range(2)
            ],
            blacklist_entries=[],
        )
        return LLMResponse(parsed=parsed, raw_text="", usage={})


def test_split_does_not_copy_notes(tmp_path: Path) -> None:
    deps = Deps(llm=NoteSplitter(), tracer=TraceWriter(tmp_path / "t.jsonl"), models=dict(MODELS))
    req = Requirement(
        id="R01",
        name="Big",
        description="Big.",
        source_doc_ids=["D04"],
        source_priority_note="D04 calls saving queries critical",
    )
    task = IssueTask(issues=[_issue("too_broad")], requirements=[req], glossary=[], round=1)
    result = asyncio.run(resolve_issue(task, deps))
    pieces = result.update["resolutions"][0].replacements
    assert [p.source_priority_note for p in pieces] == [None, None]
