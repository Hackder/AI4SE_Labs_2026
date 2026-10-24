"""LLM node that assigns High/Medium/Low priorities to unprioritised requirements."""

from collections.abc import Callable

from req_refinery import prompts
from req_refinery.llm import structured_call
from req_refinery.schemas import PrioritizeOutput
from req_refinery.state import GraphState, Replace, Requirement
from req_refinery.trace import Deps, NodeResult


def _index_check(k: int) -> Callable[[PrioritizeOutput], None]:
    def check(out: PrioritizeOutput) -> None:
        indices = [item.index for item in out.items]
        expected = set(range(1, k + 1))
        missing = sorted(expected - set(indices))
        duplicates = sorted({i for i in indices if indices.count(i) > 1})
        unknown = sorted(set(indices) - expected)
        if missing or duplicates or unknown:
            raise ValueError(
                f"expected exactly one entry for each index 1..{k}; "
                f"missing={missing} duplicate={duplicates} unknown={unknown}"
            )

    return check


async def prioritize(state: GraphState, deps: Deps) -> NodeResult:
    requirements = state["requirements"]
    pending = [i for i, r in enumerate(requirements) if r.priority is None]
    if not pending:
        return NodeResult(
            update={},
            payload={"skipped": "every requirement already has a priority"},
            round=state["round"],
        )
    payload = {
        "fixed": [
            {"name": r.name, "description": r.description, "priority": r.priority}
            for r in requirements
            if r.priority is not None
        ],
        "items": [
            {
                "index": n,
                "name": requirements[i].name,
                "description": requirements[i].description,
                "source_doc_ids": requirements[i].source_doc_ids,
                "source_priority_note": requirements[i].source_priority_note,
            }
            for n, i in enumerate(pending, start=1)
        ],
    }
    out, calls = await structured_call(
        deps.llm,
        deps.models["prioritize"],
        prompts.PRIORITIZE,
        payload,
        PrioritizeOutput,
        check=_index_check(len(pending)),
    )
    by_index = {item.index: item for item in out.items}
    updated: list[Requirement] = list(requirements)
    for n, i in enumerate(pending, start=1):
        item = by_index[n]
        updated[i] = requirements[i].model_copy(
            update={"priority": item.priority, "priority_justification": item.justification}
        )
    return NodeResult(
        update={"requirements": Replace(updated)},
        payload={
            "llm_calls": calls,
            "outputs": [
                {"name": updated[i].name, "priority": updated[i].priority} for i in pending
            ],
        },
        round=state["round"],
    )
