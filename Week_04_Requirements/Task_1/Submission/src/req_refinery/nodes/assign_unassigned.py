"""LLM node that maps candidates left out by merge_dedup onto requirements or adds them."""

import asyncio
from collections.abc import Callable
from typing import Any

from req_refinery import prompts
from req_refinery.llm import structured_call
from req_refinery.schemas import AssignOutput, CandidateAssignment
from req_refinery.state import Candidate, GraphState, Replace, Requirement, merge_notes
from req_refinery.trace import Deps, NodeResult

SINGLE_CALL_LIMIT = 60
CHUNK_SIZE = 30


def _one_line(text: str, limit: int = 160) -> str:
    line = " ".join(text.split())
    return line if len(line) <= limit else line[: limit - 1] + "…"


def _check(k: int, n: int) -> Callable[[AssignOutput], None]:
    def check(out: AssignOutput) -> None:
        indices = [item.index for item in out.items]
        expected = set(range(1, k + 1))
        problems: list[str] = []
        missing = sorted(expected - set(indices))
        duplicates = sorted({i for i in indices if indices.count(i) > 1})
        unknown = sorted(set(indices) - expected)
        if missing or duplicates or unknown:
            problems.append(
                f"expected exactly one item for each candidate index 1..{k}; "
                f"missing={missing} duplicate={duplicates} unknown={unknown}"
            )
        for item in out.items:
            if item.new == (item.maps_to is not None):
                problems.append(f"candidate {item.index}: set exactly one of new or maps_to")
            elif item.maps_to is not None and not 1 <= item.maps_to <= n:
                problems.append(f"candidate {item.index}: maps_to must be in 1..{n}")
        if problems:
            raise ValueError("; ".join(problems))

    return check


async def _assign_chunk(
    chunk: list[Candidate], requirements: list[dict[str, Any]], deps: Deps
) -> tuple[list[CandidateAssignment], list[dict[str, Any]]]:
    payload = {
        "candidates": [
            {
                "index": i,
                "name": c.name,
                "description": c.description,
                "source_doc_id": c.source_doc_id,
            }
            for i, c in enumerate(chunk, start=1)
        ],
        "requirements": requirements,
    }
    out, calls = await structured_call(
        deps.llm,
        deps.models["assign_unassigned"],
        prompts.ASSIGN_UNASSIGNED,
        payload,
        AssignOutput,
        check=_check(len(chunk), len(requirements)),
    )
    return sorted(out.items, key=lambda item: item.index), calls


async def assign_unassigned(state: GraphState, deps: Deps) -> NodeResult:
    candidates = state["unassigned_candidates"]
    requirements = list(state["requirements"])
    if not candidates:
        return NodeResult(
            update={},
            payload={"candidates": 0, "mapped": 0, "new": 0},
            round=state["round"],
        )
    listed = [
        {"index": i, "name": r.name, "description": _one_line(r.description)}
        for i, r in enumerate(requirements, start=1)
    ]
    size = len(candidates) if len(candidates) <= SINGLE_CALL_LIMIT else CHUNK_SIZE
    chunks = [candidates[i : i + size] for i in range(0, len(candidates), size)]
    results = await asyncio.gather(*(_assign_chunk(c, listed, deps) for c in chunks))

    doc_order = {d.id: i for i, d in enumerate(state["documents"])}
    added: list[Requirement] = []
    mapped: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for chunk, (items, chunk_calls) in zip(chunks, results, strict=True):
        calls.extend(chunk_calls)
        for cand, item in zip(chunk, items, strict=True):
            if item.maps_to is None:
                added.append(
                    Requirement(
                        name=cand.name,
                        description=cand.description,
                        source_doc_ids=[cand.source_doc_id],
                        origin="unassigned",
                        source_priority_note=cand.source_priority_note,
                    )
                )
                continue
            target = requirements[item.maps_to - 1]
            sources = sorted(
                {*target.source_doc_ids, cand.source_doc_id}, key=doc_order.__getitem__
            )
            requirements[item.maps_to - 1] = target.model_copy(
                update={
                    "source_doc_ids": sources,
                    "source_priority_note": merge_notes(
                        target.source_priority_note, cand.source_priority_note
                    ),
                }
            )
            mapped.append({"candidate": cand.name, "requirement": target.name})
    return NodeResult(
        update={"requirements": Replace([*requirements, *added]), "unassigned_candidates": []},
        payload={
            "llm_calls": calls,
            "candidates": len(candidates),
            "chunks": len(chunks),
            "mapped": len(mapped),
            "new": len(added),
            "mapped_to": mapped,
            "added": added,
        },
        round=state["round"],
    )
