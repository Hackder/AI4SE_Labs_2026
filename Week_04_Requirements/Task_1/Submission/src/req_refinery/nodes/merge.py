"""LLM node that merges duplicates, unifies sources and builds the glossary."""

from req_refinery import prompts
from req_refinery.llm import structured_call
from req_refinery.schemas import MergeOutput
from req_refinery.state import GlossaryTerm, GraphState, Replace, Requirement, merge_notes
from req_refinery.trace import Deps, NodeResult


async def merge_dedup(state: GraphState, deps: Deps) -> NodeResult:
    candidates = state["candidates"]
    refs = {f"C{i:03d}": c for i, c in enumerate(candidates, start=1)}
    payload = {
        "candidates": [
            {
                "ref": ref,
                "source_doc_id": c.source_doc_id,
                "name": c.name,
                "description": c.description,
            }
            for ref, c in refs.items()
        ]
    }
    out, calls = await structured_call(
        deps.llm, deps.models["merge_dedup"], prompts.MERGE_DEDUP, payload, MergeOutput
    )
    doc_order = {d.id: i for i, d in enumerate(state["documents"])}
    requirements: list[Requirement] = []
    dropped: list[str] = []
    used: set[str] = set()
    for item in out.requirements:
        known = [r for r in item.candidate_refs if r in refs]
        sources = sorted({refs[r].source_doc_id for r in known}, key=doc_order.__getitem__)
        if not sources or not item.name.strip() or not item.description.strip():
            dropped.append(item.name)
            continue
        used.update(known)
        requirements.append(
            Requirement(
                name=item.name.strip(),
                description=item.description.strip(),
                source_doc_ids=sources,
                origin="merge",
                source_priority_note=merge_notes(*(refs[r].source_priority_note for r in known)),
            )
        )
    unassigned = [ref for ref in refs if ref not in used]
    glossary = [GlossaryTerm(term=g.term, definition=g.definition) for g in out.glossary]
    return NodeResult(
        update={
            "requirements": Replace(requirements),
            "glossary": glossary,
            "system_name": out.system_name.strip() or None,
            "unassigned_candidates": [refs[ref] for ref in unassigned],
        },
        payload={
            "llm_calls": calls,
            "outputs": {"requirements": requirements, "glossary": glossary},
            "dropped_without_valid_refs": dropped,
            "merged_requirements": len(requirements),
            "unassigned_candidate_refs": unassigned,
        },
        round=state["round"],
    )
