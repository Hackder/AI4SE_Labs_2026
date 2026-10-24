"""LLM reviewer node: validates the list and routes the feedback loop."""

from req_refinery import prompts
from req_refinery.llm import structured_call
from req_refinery.schemas import ReviewOutput
from req_refinery.state import GUARDED_ORIGINS, GraphState, Issue, Route
from req_refinery.trace import Deps, NodeResult

SETTLED_TAG = "[granularity settled]"


async def review(state: GraphState, deps: Deps) -> NodeResult:
    round_no = state["round"] + 1
    max_rounds = state["max_rounds"]
    requirements = state["requirements"]
    payload = {
        "round": round_no,
        "max_rounds": max_rounds,
        "requirements": [
            {
                "id": r.id,
                **({"tag": SETTLED_TAG} if r.origin in GUARDED_ORIGINS else {}),
                "name": r.name,
                "description": r.description,
                "source_doc_ids": r.source_doc_ids,
                "priority": r.priority,
                "priority_justification": r.priority_justification,
            }
            for r in requirements
        ],
        "glossary": [g.model_dump() for g in state["glossary"]],
        "blacklist": [
            {
                "name": b.requirement.name,
                "description": b.requirement.description,
                "reason": b.reason,
            }
            for b in state["blacklist"]
        ],
    }
    out, calls = await structured_call(
        deps.llm, deps.models["review"], prompts.REVIEW, payload, ReviewOutput
    )
    known = {r.id for r in requirements}
    issues: list[Issue] = []
    discarded: list[dict[str, object]] = []
    for item in out.issues:
        ids = list(dict.fromkeys(i for i in item.requirement_ids if i in known))
        if not ids:
            discarded.append({"issue": item.model_dump(), "reason": "no known requirement ids"})
            continue
        issues.append(Issue(type=item.type, requirement_ids=ids, explanation=item.explanation))

    route: Route = out.route
    route_note = None
    if route == "targeted" and not issues:
        route, route_note = "accept", "targeted with no valid issues, treated as accept"
    if round_no >= max_rounds and route != "accept":
        route, route_note = "accept", f"forced accept at round {round_no} of {max_rounds}"

    update: dict[str, object] = {"round": round_no, "route": route}
    if route == "accept":
        update |= {"issues": [], "open_issues": issues}
    else:
        update |= {"issues": issues, "open_issues": []}
    return NodeResult(
        update=update,
        payload={
            "llm_calls": calls,
            "model_route": out.route,
            "route": route,
            "route_override": route_note,
            "issues": issues,
            "discarded_issues": discarded,
        },
        round=round_no,
    )
