"""Per-document pass: which requirements each document supports, and what it adds.

Runs twice. In coverage mode (before prioritize) missed requirements are inserted;
in attribution mode (after the review loop) they are only reported as open issues.
In both modes every requirement's sources become exactly the documents that support it.
"""

from collections.abc import Callable
from typing import Any

from req_refinery import prompts
from req_refinery.llm import structured_call
from req_refinery.schemas import DocumentPassOutput
from req_refinery.state import (
    DocumentPassResult,
    DocumentTask,
    GraphState,
    Issue,
    PassMode,
    Replace,
    Requirement,
    merge_notes,
)
from req_refinery.trace import Deps, NodeImpl, NodeResult


def _check(n: int) -> Callable[[DocumentPassOutput], None]:
    def check(out: DocumentPassOutput) -> None:
        bad = sorted({i for i in out.supports if not 1 <= i <= n})
        if bad:
            raise ValueError(f"supports contains indices outside 1..{n}: {bad}")

    return check


async def document_pass(task: DocumentTask, deps: Deps) -> NodeResult:
    doc = task["document"]
    reqs = task["requirements"]
    payload = {
        "document": {"id": doc.id, "path": doc.path, "text": doc.text},
        "requirements": [
            {"index": i, "name": r.name, "description": r.description}
            for i, r in enumerate(reqs, start=1)
        ],
    }
    out, calls = await structured_call(
        deps.llm,
        deps.models["document_pass"],
        prompts.DOCUMENT_PASS,
        payload,
        DocumentPassOutput,
        check=_check(len(reqs)),
    )
    missed = [
        Requirement(
            name=m.name.strip(),
            description=m.description.strip(),
            source_doc_ids=[doc.id],
            origin="coverage",
            source_priority_note=merge_notes(m.source_priority_note),
        )
        for m in out.missed
        if m.name.strip() and m.description.strip()
    ]
    result = DocumentPassResult(
        doc_id=doc.id, supports=sorted({i - 1 for i in out.supports}), missed=missed
    )
    return NodeResult(
        update={"document_passes": [result]},
        payload={
            "mode": task["mode"],
            "document_id": doc.id,
            "llm_calls": calls,
            "supports": [reqs[i].name for i in result.supports],
            "missed": missed,
        },
        round=task["round"],
    )


def apply_document_pass(mode: PassMode) -> NodeImpl[GraphState]:
    """Deterministic step after the fan-out: rewrite sources, handle missed items."""

    async def apply(state: GraphState, _deps: Deps) -> NodeResult:
        requirements = state["requirements"]
        doc_order = {d.id: i for i, d in enumerate(state["documents"])}
        support: dict[int, set[str]] = {}
        for res in state["document_passes"]:
            for i in res.supports:
                support.setdefault(i, set()).add(res.doc_id)

        updated: list[Requirement] = []
        unverified: list[Issue] = []
        added = removed = before = after = 0
        changes: list[dict[str, Any]] = []
        for i, req in enumerate(requirements):
            old = set(req.source_doc_ids)
            new = support.get(i, set())
            before += len(old)
            if not new:
                updated.append(req)
                after += len(old)
                unverified.append(
                    Issue(
                        type="sources_unverified",
                        requirement_ids=[req.id] if req.id else [],
                        explanation=(
                            f"“{req.name}”: no document reported support; previous "
                            f"sources kept ({', '.join(req.source_doc_ids)})."
                        ),
                    )
                )
                continue
            sources = sorted(new, key=doc_order.__getitem__)
            updated.append(req.model_copy(update={"source_doc_ids": sources}))
            after += len(new)
            added += len(new - old)
            removed += len(old - new)
            if new != old:
                changes.append(
                    {
                        "requirement": req.id or req.name,
                        "added": sorted(new - old),
                        "removed": sorted(old - new),
                    }
                )

        missed = [m for res in state["document_passes"] for m in res.missed]
        stats = {
            "citations_before": before,
            "citations_after": after,
            "citations_added": added,
            "citations_removed": removed,
            "sources_unverified": len(unverified),
            "missed": len(missed),
        }
        update: dict[str, Any] = {"document_passes": Replace[DocumentPassResult]()}
        if mode == "coverage":
            update["requirements"] = Replace([*updated, *missed])
        else:
            possibly_missed = [
                Issue(
                    type="possibly_missed",
                    requirement_ids=[],
                    explanation=f"“{m.name}” ({m.source_doc_ids[0]}): {m.description}",
                )
                for m in missed
            ]
            update |= {
                "requirements": Replace(updated),
                "open_issues": [*state["open_issues"], *unverified, *possibly_missed],
                "attribution_stats": stats,
            }
        return NodeResult(
            update=update,
            payload={
                "mode": mode,
                **stats,
                "changes": changes,
                "unverified_issues": unverified,
                "missed": missed,
            },
            round=state["round"],
        )

    return apply
