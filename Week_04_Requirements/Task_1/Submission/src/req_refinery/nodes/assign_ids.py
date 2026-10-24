"""Deterministic node that sorts requirements and numbers them R01..Rn."""

from req_refinery.state import PRIORITY_RANK, GraphState, Replace, Requirement
from req_refinery.trace import Deps, NodeResult


def _sort_key(req: Requirement) -> tuple[int, str, str]:
    rank = PRIORITY_RANK[req.priority] if req.priority is not None else len(PRIORITY_RANK)
    return (rank, min(req.source_doc_ids), req.name.casefold())


async def assign_ids(state: GraphState, _deps: Deps) -> NodeResult:
    before = state["requirements"]
    ordered = sorted(before, key=_sort_key)
    width = max(2, len(str(len(ordered))))
    numbered = [r.model_copy(update={"id": f"R{i:0{width}d}"}) for i, r in enumerate(ordered, 1)]
    return NodeResult(
        update={"requirements": Replace(numbered)},
        payload={
            "inputs": before,
            "outputs": numbered,
        },
        round=state["round"],
    )
