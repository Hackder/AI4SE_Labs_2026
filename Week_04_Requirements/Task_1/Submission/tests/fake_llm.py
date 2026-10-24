"""Fake LLM: tiny canned structured responses keyed on the requested schema."""

import json
from collections.abc import Callable, Sequence
from typing import Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from req_refinery.llm import LLMResponse
from req_refinery.schemas import (
    AssignOutput,
    BlacklistOut,
    CandidateAssignment,
    ConsolidatedBlacklist,
    ConsolidatedRequirement,
    ConsolidateOutput,
    DocumentPassOutput,
    ExtractOutput,
    GlossaryOut,
    IssueOut,
    MergedRequirement,
    MergeOutput,
    NamedText,
    OpenQuestionOut,
    PrioritizeOutput,
    PriorityItem,
    ReplacementOut,
    ResolveOutput,
    ReviewOutput,
)

_LEVELS = ("High", "Medium", "Low")


def _payload(messages: Sequence[BaseMessage]) -> dict[str, Any]:
    content = messages[1].content
    assert isinstance(content, str)
    data: dict[str, Any] = json.loads(content)
    return data


def _extract(p: dict[str, Any]) -> BaseModel:
    doc = str(p["document"]["id"])
    return ExtractOutput(
        candidates=[
            NamedText(
                name=f"Feature {n} of {doc}",
                description=f"{doc} asks for feature {n}.",
                source_priority_note=f"{doc} marks this High" if doc == "D10" and n == 1 else None,
            )
            for n in (1, 2)
        ]
    )


def _merge(p: dict[str, Any]) -> BaseModel:
    by_doc: dict[str, list[str]] = {}
    for c in p["candidates"][:-2]:  # leave the last two candidates unassigned
        by_doc.setdefault(str(c["source_doc_id"]), []).append(str(c["ref"]))
    return MergeOutput(
        system_name="the fake system",
        requirements=[
            MergedRequirement(
                name=f"Merged needs of {doc}", description=f"All of {doc}.", candidate_refs=refs
            )
            for doc, refs in by_doc.items()
        ],
        glossary=[GlossaryOut(term="Item", definition="A thing in the fake system.")],
    )


def _consolidate(p: dict[str, Any]) -> BaseModel:
    """One requirement per document from its candidates; the first candidate of D03 is
    blacklisted; the last two candidates are left unassigned; one open question."""
    cands: list[dict[str, Any]] = p["candidates"]
    black = next(c for c in cands if c["source_doc_id"] == "D03")
    by_doc: dict[str, list[str]] = {}
    for c in cands[:-2]:
        if c["ref"] != black["ref"]:
            by_doc.setdefault(str(c["source_doc_id"]), []).append(str(c["ref"]))
    return ConsolidateOutput(
        system_name="the fake system",
        requirements=[
            ConsolidatedRequirement(
                name=f"Consolidated needs of {doc}",
                description=f"All of {doc}.",
                source_doc_ids=[doc],
                candidate_refs=refs,
                source_priority_note=None,
            )
            for doc, refs in by_doc.items()
        ],
        glossary=[GlossaryOut(term="Item", definition="A thing in the fake system.")],
        blacklist=[
            ConsolidatedBlacklist(
                name=str(black["name"]),
                description=str(black["description"]),
                source_doc_ids=["D03"],
                candidate_refs=[str(black["ref"])],
                source_priority_note=None,
                reason="Conflicts with the better-supported D04 request (D03 vs D04).",
            )
        ],
        open_questions=[
            OpenQuestionOut(question="Which metric defines capacity?", doc_ids=["D02", "D03"])
        ],
    )


def _assign(p: dict[str, Any]) -> BaseModel:
    # first unassigned candidate maps onto requirement 1, the rest become new
    return AssignOutput(
        items=[
            CandidateAssignment(index=int(c["index"]), maps_to=1 if n == 0 else None, new=n > 0)
            for n, c in enumerate(p["candidates"])
        ]
    )


def _document_pass(p: dict[str, Any]) -> BaseModel:
    """A document supports every requirement whose description mentions its id.
    D01 reports a missed 'Missed export' (which mentions no id, so it is never
    supported); once that exists (attribution pass) D02 reports one more missed item."""
    doc = str(p["document"]["id"])
    reqs: list[dict[str, Any]] = p["requirements"]
    supports = [int(r["index"]) for r in reqs if doc in str(r["description"])]
    names = {str(r["name"]) for r in reqs}
    missed: list[NamedText] = []
    if doc == "D01" and "Missed export" not in names:
        missed.append(
            NamedText(name="Missed export", description="Export data.", source_priority_note=None)
        )
    if doc == "D02" and "Missed export" in names:
        missed.append(
            NamedText(name="Late find", description="Found late.", source_priority_note=None)
        )
    return DocumentPassOutput(supports=supports, missed=missed)


def _prioritize(p: dict[str, Any]) -> BaseModel:
    return PrioritizeOutput(
        items=[
            PriorityItem(index=int(it["index"]), priority=_LEVELS[n % 3], justification="Fake.")
            for n, it in enumerate(p["items"])
        ]
    )


def _review(p: dict[str, Any]) -> BaseModel:
    if int(p["round"]) == 1:
        ids = [str(r["id"]) for r in p["requirements"][:5]]
        issues = [  # overlapping on ids[1]: must be resolved as one group
            IssueOut(type="conflict", requirement_ids=ids[:2], explanation="They disagree."),
            IssueOut(type="duplicate", requirement_ids=ids[1:3], explanation="Same thing."),
            IssueOut(
                type="too_narrow",
                requirement_ids=ids[3:5],
                explanation=f"{ids[4]} is a detail of the parent {ids[3]}.",
            ),
        ]
        return ReviewOutput(issues=issues, route="targeted")
    return ReviewOutput(issues=[], route="accept")


def _resolve(p: dict[str, Any]) -> BaseModel:
    reqs: list[dict[str, Any]] = p["requirements"]
    if all(i["type"] == "too_narrow" for i in p["issues"]):
        parent, detail = reqs[0], reqs[1]
        absorbed = ReplacementOut(
            name=f"{parent['name']} with detail",
            description=f"{parent['description']} {detail['description']}",
            source_doc_ids=[],
            narrowing_reason=None,
            source_priority_note=None,
        )
        return ResolveOutput(replacements=[absorbed], blacklist_entries=[])
    keep, drop = reqs[0], reqs[-1]
    return ResolveOutput(
        replacements=[
            ReplacementOut(
                name=str(keep["name"]),
                description=str(keep["description"]),
                source_doc_ids=[],
                narrowing_reason=None,
                source_priority_note=None,
            )
        ],
        blacklist_entries=[
            BlacklistOut(requirement_id=str(drop["id"]), reason=f"Fewer sources than {keep['id']}.")
        ],
    )


_HANDLERS: dict[type[BaseModel], Callable[[dict[str, Any]], BaseModel]] = {
    ExtractOutput: _extract,
    MergeOutput: _merge,
    ConsolidateOutput: _consolidate,
    AssignOutput: _assign,
    DocumentPassOutput: _document_pass,
    PrioritizeOutput: _prioritize,
    ReviewOutput: _review,
    ResolveOutput: _resolve,
}


class FakeLLM:
    async def ainvoke(
        self, model: str, messages: Sequence[BaseMessage], schema: type[BaseModel]
    ) -> LLMResponse:
        del model
        parsed = _HANDLERS[schema](_payload(messages))
        return LLMResponse(
            parsed=parsed,
            raw_text=parsed.model_dump_json(),
            usage={"prompt": 1, "completion": 1, "total": 2},
        )
