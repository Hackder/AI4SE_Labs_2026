"""Targeted repair: one LLM call per issue group, then a deterministic apply step."""

import re

from req_refinery import prompts
from req_refinery.llm import structured_call
from req_refinery.schemas import ResolveOutput
from req_refinery.state import (
    BlacklistEntry,
    GraphState,
    Issue,
    IssueTask,
    Origin,
    Replace,
    Requirement,
    Resolution,
    merge_notes,
    validate_requirements,
)
from req_refinery.trace import Deps, NodeResult

MAX_SPLIT = 4


def origin_for(issues: list[Issue]) -> Origin:
    """Origin tag of the replacements produced for one issue group."""
    broad = any(i.type == "too_broad" for i in issues)
    narrow = any(i.type == "too_narrow" for i in issues)
    if broad and narrow:
        return "granularity"
    if broad:
        return "split"
    if narrow:
        return "folded"
    return "resolved"


def replacement_limit(issues: list[Issue], involved: list[Requirement]) -> int | None:
    """At most MAX_SPLIT replacements per too_broad requirement, one per other one."""
    broad_ids = {rid for i in issues if i.type == "too_broad" for rid in i.requirement_ids}
    if not broad_ids:
        return None
    others = [r for r in involved if r.id not in broad_ids]
    return MAX_SPLIT * len(broad_ids) + len(others)


async def resolve_issue(task: IssueTask, deps: Deps) -> NodeResult:
    issues = task["issues"]
    involved = task["requirements"]
    payload = {
        "issues": [i.model_dump() for i in issues],
        "requirements": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "source_doc_ids": r.source_doc_ids,
                "source_priority_note": r.source_priority_note,
                "priority": r.priority,
            }
            for r in involved
        ],
        "glossary": [g.model_dump() for g in task["glossary"]],
    }
    limit = replacement_limit(issues, involved)

    def split_cap(out: ResolveOutput) -> str | None:
        if limit is None or len(out.replacements) <= limit:
            return None
        return (
            f"{len(out.replacements)} replacements exceed the limit of {limit}: a too_broad "
            f"requirement may be split into at most {MAX_SPLIT} requirements"
        )

    out, calls = await structured_call(
        deps.llm,
        deps.models["resolve_issue"],
        prompts.RESOLVE_ISSUE,
        payload,
        ResolveOutput,
        soft_check=split_cap,
    )
    truncated = 0
    if limit is not None and len(out.replacements) > limit:
        truncated = len(out.replacements) - limit
        out = out.model_copy(update={"replacements": out.replacements[:limit]})
    union: list[str] = []
    for r in involved:
        union.extend(d for d in r.source_doc_ids if d not in union)
    replacements: list[Requirement] = []
    # Notes travel only with their content: the resolver sets each replacement's note.
    # The one deterministic fallback is a pure merge (duplicate / too_narrow group with a
    # single replacement), where every involved item went into that replacement.
    pure_merge = len(out.replacements) == 1 and all(
        i.type in {"duplicate", "too_narrow"} for i in issues
    )
    merged_notes = merge_notes(*(r.source_priority_note for r in involved)) if pure_merge else None
    for rep in out.replacements:
        narrowed = [d for d in rep.source_doc_ids if d in union]
        keep_narrowed = bool(rep.narrowing_reason and rep.narrowing_reason.strip() and narrowed)
        if not rep.name.strip() or not rep.description.strip():
            continue
        replacements.append(
            Requirement(
                name=rep.name.strip(),
                description=rep.description.strip(),
                source_doc_ids=narrowed if keep_narrowed else list(union),
                source_priority_note=merge_notes(rep.source_priority_note) or merged_notes,
            )
        )
    by_id = {r.id: r for r in involved}
    blacklist: list[BlacklistEntry] = []
    for entry in out.blacklist_entries:
        original = by_id.get(entry.requirement_id)
        if original is None:
            continue
        blacklist.append(
            BlacklistEntry(
                requirement=original.model_copy(update={"id": None}), reason=entry.reason
            )
        )
    resolution = Resolution(issues=issues, replacements=replacements, blacklist_entries=blacklist)
    return NodeResult(
        update={"resolutions": [resolution]},
        payload={
            "llm_calls": calls,
            "outputs": resolution,
            "replacement_limit": limit,
            "truncated_replacements": truncated,
        },
        round=task["round"],
    )


ID_PATTERN = re.compile(r"\bR\d+\b")


class IdSubstituter:
    """Replaces requirement ids in free text with the quoted requirement name."""

    def __init__(self, names: dict[str, str]) -> None:
        self.names: dict[str, str] = names
        self.substituted: list[dict[str, str]] = []
        self.unresolved: list[str] = []

    def _replace(self, match: re.Match[str]) -> str:
        rid = match.group(0)
        name = self.names.get(rid)
        if name is None:
            self.unresolved.append(rid)
            return rid
        self.substituted.append({"id": rid, "name": name})
        return f"\u201c{name}\u201d"

    def __call__(self, text: str) -> str:
        return ID_PATTERN.sub(self._replace, text)


def _substitute_ids(resolution: Resolution, fix: IdSubstituter) -> Resolution:
    replacements = [
        r.model_copy(update={"name": fix(r.name), "description": fix(r.description)})
        for r in resolution.replacements
    ]
    blacklist = [
        b.model_copy(update={"reason": fix(b.reason)}) for b in resolution.blacklist_entries
    ]
    return resolution.model_copy(
        update={"replacements": replacements, "blacklist_entries": blacklist}
    )


async def apply_resolutions(state: GraphState, _deps: Deps) -> NodeResult:
    fix = IdSubstituter({r.id: r.name for r in state["requirements"] if r.id is not None})
    resolutions = [_substitute_ids(res, fix) for res in state["resolutions"]]
    removed = {i for res in resolutions for issue in res.issues for i in issue.requirement_ids}
    kept = [r for r in state["requirements"] if r.id not in removed]
    added = [
        r.model_copy(update={"origin": origin_for(res.issues)})
        for res in resolutions
        for r in res.replacements
    ]
    new_blacklist = [b for res in resolutions for b in res.blacklist_entries]
    doc_ids = {d.id for d in state["documents"]}
    requirements = validate_requirements([*kept, *added], doc_ids)
    return NodeResult(
        update={
            "requirements": Replace(requirements),
            "blacklist": [*state["blacklist"], *new_blacklist],
            "issues": [],
            "issue_groups": [],
            "resolutions": Replace[Resolution](),
        },
        payload={
            "inputs": {"resolutions": state["resolutions"]},
            "id_substitutions": fix.substituted,
            "unresolved_ids": fix.unresolved,
            "outputs": {
                "removed_ids": sorted(removed),
                "added": added,
                "blacklisted": new_blacklist,
                "requirement_count": len(requirements),
            },
        },
        round=state["round"],
    )
