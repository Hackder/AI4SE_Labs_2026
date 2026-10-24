"""Deterministic node that groups review issues sharing requirement ids."""

from req_refinery.state import GUARDED_ORIGINS, GraphState, Issue, IssueGroup
from req_refinery.trace import Deps, NodeResult

GRANULARITY_TYPES = frozenset({"too_broad", "too_narrow"})


def group_by_shared_ids(issues: list[Issue]) -> list[IssueGroup]:
    """Connected components of issues, where two issues connect if they share an id."""
    parent = list(range(len(issues)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    owner: dict[str, int] = {}
    for i, issue in enumerate(issues):
        for rid in issue.requirement_ids:
            if rid in owner:
                parent[find(i)] = find(owner[rid])
            else:
                owner[rid] = i
    members: dict[int, list[Issue]] = {}
    for i, issue in enumerate(issues):
        members.setdefault(find(i), []).append(issue)
    groups: list[IssueGroup] = []
    for group_issues in members.values():
        ids = list(dict.fromkeys(r for issue in group_issues for r in issue.requirement_ids))
        groups.append(IssueGroup(issues=group_issues, requirement_ids=ids))
    return groups


async def group_issues(state: GraphState, _deps: Deps) -> NodeResult:
    guarded = {r.id for r in state["requirements"] if r.origin in GUARDED_ORIGINS}
    kept: list[Issue] = []
    dropped: list[Issue] = []
    for issue in state["issues"]:
        if issue.type in GRANULARITY_TYPES and guarded.intersection(issue.requirement_ids):
            dropped.append(issue)
        else:
            kept.append(issue)
    groups = group_by_shared_ids(kept)
    update: dict[str, object] = {"issue_groups": groups, "issues": kept}
    if not groups:
        # nothing left to resolve: finish like an accept, keeping the dropped issues open
        update |= {"route": "accept", "open_issues": dropped}
    return NodeResult(
        update=update,
        payload={
            "issues": len(state["issues"]),
            "dropped_granularity_issues": len(dropped),
            "dropped_issues": dropped,
            "groups": len(groups),
            "largest_group_issues": max((len(g.issues) for g in groups), default=0),
            "largest_group_requirements": max((len(g.requirement_ids) for g in groups), default=0),
            "outputs": groups,
        },
        round=state["round"],
    )
