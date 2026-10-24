"""Shared LangGraph state and Pydantic models."""

import operator
from collections.abc import Iterable
from typing import Annotated, Any, Literal, TypedDict

from pydantic import BaseModel, Field

type Priority = Literal["High", "Medium", "Low"]
type ReviewIssueType = Literal[
    "duplicate", "conflict", "wording", "nonsense", "priority", "too_broad", "too_narrow"
]
type IssueType = ReviewIssueType | Literal["sources_unverified", "possibly_missed"]
type Route = Literal["accept", "targeted"]
type PassMode = Literal["coverage", "attribution"]
type GraphName = Literal["network", "hybrid"]
type Origin = Literal[
    "consolidate", "merge", "unassigned", "coverage", "split", "folded", "granularity", "resolved"
]
GUARDED_ORIGINS: frozenset[str] = frozenset({"split", "folded", "granularity"})

PRIORITY_RANK: dict[str, int] = {"High": 0, "Medium": 1, "Low": 2}


class Document(BaseModel):
    id: str
    path: str
    text: str


class Candidate(BaseModel):
    name: str
    description: str
    source_doc_id: str
    source_priority_note: str | None = None


class Requirement(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_doc_ids: list[str] = Field(min_length=1)
    priority: Priority | None = None
    priority_justification: str | None = None
    origin: Origin | None = None
    source_priority_note: str | None = None


class GlossaryTerm(BaseModel):
    term: str
    definition: str


class BlacklistEntry(BaseModel):
    requirement: Requirement
    reason: str


class Issue(BaseModel):
    type: IssueType
    requirement_ids: list[str]
    explanation: str


class OpenQuestion(BaseModel):
    question: str
    doc_ids: list[str]


class IssueGroup(BaseModel):
    issues: list[Issue]
    requirement_ids: list[str]


class Resolution(BaseModel):
    issues: list[Issue]
    replacements: list[Requirement]
    blacklist_entries: list[BlacklistEntry]


class DocumentPassResult(BaseModel):
    """Output of document_pass for one document: supported indices (0-based into the
    requirement list as sent) and requirements this document states that were missed."""

    doc_id: str
    supports: list[int]
    missed: list[Requirement]


class TraceRecord(BaseModel):
    node: str
    round: int
    started_at: str
    ended_at: str
    duration_ms: int
    payload: dict[str, Any]


class Replace[T](list[T]):
    """List update that replaces the channel value instead of extending it."""

    def __init__(self, items: Iterable[T] = ()) -> None:
        super().__init__(items)


def extend_or_replace[T](left: list[T], right: list[T]) -> list[T]:
    """Reducer: plain lists are appended (fan-out results), Replace overwrites."""
    if isinstance(right, Replace):
        return list(right)
    return [*left, *right]


class GraphState(TypedDict):
    graph: GraphName
    input_dir: str
    output_dir: str
    run_dir: str
    limit: int | None
    max_rounds: int
    documents: list[Document]
    system_name: str | None
    candidates: Annotated[list[Candidate], extend_or_replace]
    unassigned_candidates: list[Candidate]
    requirements: Annotated[list[Requirement], extend_or_replace]
    glossary: list[GlossaryTerm]
    blacklist: list[BlacklistEntry]
    issues: list[Issue]
    issue_groups: list[IssueGroup]
    resolutions: Annotated[list[Resolution], extend_or_replace]
    route: Route | None
    round: int
    open_issues: list[Issue]
    open_questions: list[OpenQuestion]
    document_passes: Annotated[list[DocumentPassResult], extend_or_replace]
    attribution_stats: dict[str, int]
    trace: Annotated[list[TraceRecord], operator.add]


class DocumentTask(TypedDict):
    """Send payload for the per-document fan-outs (extract, document_pass)."""

    document: Document
    requirements: list[Requirement]
    round: int
    mode: PassMode


class IssueTask(TypedDict):
    """Send payload for resolve_issue: one group of issues sharing requirement ids."""

    issues: list[Issue]
    requirements: list[Requirement]
    glossary: list[GlossaryTerm]
    round: int


def merge_notes(*notes: str | None) -> str | None:
    """Union of source priority notes, in order, without repeats."""
    parts: list[str] = []
    for note in notes:
        for part in (note or "").split(";"):
            part = part.strip().rstrip(".").strip()
            if part and part not in parts:
                parts.append(part)
    return "; ".join(parts) or None


def validate_requirements(requirements: list[Requirement], doc_ids: set[str]) -> list[Requirement]:
    """Re-validate every requirement and check that sources exist."""
    validated: list[Requirement] = []
    for req in requirements:
        checked = Requirement.model_validate(req.model_dump())
        unknown = [d for d in checked.source_doc_ids if d not in doc_ids]
        if unknown:
            raise ValueError(f"requirement {checked.name!r} cites unknown {unknown}")
        validated.append(checked)
    return validated


def initial_state(
    input_dir: str,
    output_dir: str,
    run_dir: str,
    limit: int | None,
    max_rounds: int,
    graph: GraphName = "network",
) -> GraphState:
    return GraphState(
        graph=graph,
        input_dir=input_dir,
        output_dir=output_dir,
        run_dir=run_dir,
        limit=limit,
        max_rounds=max_rounds,
        documents=[],
        system_name=None,
        candidates=[],
        unassigned_candidates=[],
        requirements=[],
        glossary=[],
        blacklist=[],
        issues=[],
        issue_groups=[],
        resolutions=[],
        route=None,
        round=0,
        open_issues=[],
        open_questions=[],
        document_passes=[],
        attribution_stats={},
        trace=[],
    )
