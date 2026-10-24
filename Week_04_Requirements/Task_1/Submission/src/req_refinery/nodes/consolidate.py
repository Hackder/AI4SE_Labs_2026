"""Hybrid graph: one whole-corpus consolidation call replacing merge_dedup.

The model sees every document in full plus every extracted candidate, and returns the
requirement list, glossary, blacklist and the open questions the sources leave open.
Candidates it neither folds nor blacklists are handed to assign_unassigned.
"""

import json
from typing import Any

from req_refinery import prompts
from req_refinery.config import CONSOLIDATE_MAX_PROMPT_TOKENS
from req_refinery.llm import LLMCallError, structured_call
from req_refinery.schemas import ConsolidateOutput
from req_refinery.state import (
    BlacklistEntry,
    Candidate,
    GlossaryTerm,
    GraphState,
    OpenQuestion,
    Replace,
    Requirement,
    merge_notes,
)
from req_refinery.trace import Deps, NodeResult

CHARS_PER_TOKEN = 4


class ContextTooLargeError(RuntimeError):
    """The corpus does not fit one consolidation call; sharding is not implemented."""


def _sources(
    stated: list[str], refs: list[str], cands: dict[str, Candidate], order: dict[str, int]
) -> list[str]:
    """Documents the model named (known ids only); else the union of the candidates'."""
    known = {d for d in stated if d in order}
    if not known:
        known = {cands[r].source_doc_id for r in refs if r in cands}
    return sorted(known, key=order.__getitem__)


def _note(stated: str | None, refs: list[str], cands: dict[str, Candidate]) -> str | None:
    """The consolidator's note if it wrote one, else the union of the candidates' notes."""
    return merge_notes(stated) or merge_notes(*(cands[r].source_priority_note for r in refs))


async def consolidate(state: GraphState, deps: Deps) -> NodeResult:
    cands = {f"C{i:03d}": c for i, c in enumerate(state["candidates"], start=1)}
    payload: dict[str, Any] = {
        "documents": [{"id": d.id, "path": d.path, "text": d.text} for d in state["documents"]],
        "candidates": [
            {
                "ref": ref,
                "source_doc_id": c.source_doc_id,
                "name": c.name,
                "description": c.description,
            }
            for ref, c in cands.items()
        ],
    }
    est_tokens = (len(prompts.CONSOLIDATE) + len(json.dumps(payload))) // CHARS_PER_TOKEN
    if est_tokens > CONSOLIDATE_MAX_PROMPT_TOKENS:
        raise ContextTooLargeError(
            f"consolidate prompt is ~{est_tokens} tokens, above the limit of "
            f"{CONSOLIDATE_MAX_PROMPT_TOKENS}; the corpus is too large for one whole-corpus "
            "call (sharding is not implemented). Use --graph network for this corpus."
        )
    try:
        out, calls = await structured_call(
            deps.llm, deps.models["consolidate"], prompts.CONSOLIDATE, payload, ConsolidateOutput
        )
    except LLMCallError as exc:
        if "context" in str(exc).lower() and "length" in str(exc).lower():
            raise ContextTooLargeError(
                f"consolidate prompt (~{est_tokens} tokens) exceeds the model context: {exc}"
            ) from exc
        raise

    order = {d.id: i for i, d in enumerate(state["documents"])}
    used: set[str] = set()
    dropped: list[str] = []
    requirements: list[Requirement] = []
    for item in out.requirements:
        refs = [r for r in item.candidate_refs if r in cands]
        sources = _sources(item.source_doc_ids, refs, cands, order)
        if not sources or not item.name.strip() or not item.description.strip():
            dropped.append(item.name)
            continue
        used.update(refs)
        requirements.append(
            Requirement(
                name=item.name.strip(),
                description=item.description.strip(),
                source_doc_ids=sources,
                origin="consolidate",
                source_priority_note=_note(item.source_priority_note, refs, cands),
            )
        )
    blacklist: list[BlacklistEntry] = []
    for item in out.blacklist:
        refs = [r for r in item.candidate_refs if r in cands]
        sources = _sources(item.source_doc_ids, refs, cands, order)
        if not sources or not item.name.strip() or not item.description.strip():
            dropped.append(item.name)
            continue
        used.update(refs)
        blacklist.append(
            BlacklistEntry(
                requirement=Requirement(
                    name=item.name.strip(),
                    description=item.description.strip(),
                    source_doc_ids=sources,
                    origin="consolidate",
                    source_priority_note=_note(item.source_priority_note, refs, cands),
                ),
                reason=item.reason.strip(),
            )
        )
    questions = [
        OpenQuestion(
            question=q.question.strip(),
            doc_ids=sorted({d for d in q.doc_ids if d in order}, key=order.__getitem__),
        )
        for q in out.open_questions
        if q.question.strip()
    ]
    unassigned = [ref for ref in cands if ref not in used]
    glossary = [GlossaryTerm(term=g.term, definition=g.definition) for g in out.glossary]
    return NodeResult(
        update={
            "requirements": Replace(requirements),
            "blacklist": [*state["blacklist"], *blacklist],
            "glossary": glossary,
            "open_questions": questions,
            "system_name": out.system_name.strip() or None,
            "unassigned_candidates": [cands[r] for r in unassigned],
        },
        payload={
            "llm_calls": calls,
            "estimated_prompt_tokens": est_tokens,
            "candidates_in": len(cands),
            "requirements_out": len(requirements),
            "blacklist_out": len(blacklist),
            "open_questions": len(questions),
            "unassigned_candidates": len(unassigned),
            "unassigned_candidate_refs": unassigned,
            "dropped_without_sources": dropped,
            "coverage_pass": (
                "skipped in the hybrid graph: the consolidator saw the full corpus; "
                "document_pass runs only in attribution mode after the review loop"
            ),
            "outputs": {
                "requirements": requirements,
                "blacklist": blacklist,
                "glossary": glossary,
                "open_questions": questions,
            },
        },
        round=state["round"],
    )
