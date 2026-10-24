"""Structured-output schemas the LLM nodes ask the models for.

All fields are required (nullable where optional) so they work with strict JSON schema.
"""

from pydantic import BaseModel

from req_refinery.state import Priority, ReviewIssueType, Route


class NamedText(BaseModel):
    name: str
    description: str
    source_priority_note: str | None


class ExtractOutput(BaseModel):
    candidates: list[NamedText]


class MergedRequirement(BaseModel):
    name: str
    description: str
    candidate_refs: list[str]


class GlossaryOut(BaseModel):
    term: str
    definition: str


class MergeOutput(BaseModel):
    system_name: str
    requirements: list[MergedRequirement]
    glossary: list[GlossaryOut]


class CandidateAssignment(BaseModel):
    index: int
    maps_to: int | None
    new: bool


class AssignOutput(BaseModel):
    items: list[CandidateAssignment]


class DocumentPassOutput(BaseModel):
    supports: list[int]
    missed: list[NamedText]


class PriorityItem(BaseModel):
    index: int
    priority: Priority
    justification: str


class PrioritizeOutput(BaseModel):
    items: list[PriorityItem]


class IssueOut(BaseModel):
    type: ReviewIssueType
    requirement_ids: list[str]
    explanation: str


class ReviewOutput(BaseModel):
    issues: list[IssueOut]
    route: Route


class ReplacementOut(BaseModel):
    name: str
    description: str
    source_doc_ids: list[str]
    narrowing_reason: str | None
    source_priority_note: str | None


class BlacklistOut(BaseModel):
    requirement_id: str
    reason: str


class ResolveOutput(BaseModel):
    replacements: list[ReplacementOut]
    blacklist_entries: list[BlacklistOut]


class ConsolidatedRequirement(BaseModel):
    name: str
    description: str
    source_doc_ids: list[str]
    candidate_refs: list[str]
    source_priority_note: str | None


class ConsolidatedBlacklist(BaseModel):
    name: str
    description: str
    source_doc_ids: list[str]
    candidate_refs: list[str]
    source_priority_note: str | None
    reason: str


class OpenQuestionOut(BaseModel):
    question: str
    doc_ids: list[str]


class ConsolidateOutput(BaseModel):
    system_name: str
    requirements: list[ConsolidatedRequirement]
    glossary: list[GlossaryOut]
    blacklist: list[ConsolidatedBlacklist]
    open_questions: list[OpenQuestionOut]
