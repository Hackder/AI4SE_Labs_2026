"""Swappable constants: model per LLM node, round limit, priority scale."""

from typing import Final

MODELS: Final[dict[str, str]] = {
    "extract": "gpt-5.6-luna",
    "merge_dedup": "gpt-5.6-luna",
    "consolidate": "gpt-6-luna",
    "assign_unassigned": "gpt-5-mini",
    "document_pass": "gpt-5.6-luna",
    "prioritize": "gpt-6-luna",
    "review": "gpt-6-luna",
    "resolve_issue": "gpt-5.6-luna",
}

DEFAULT_MAX_ROUNDS: Final[int] = 5

PRIORITY_SCALE: Final[dict[str, str]] = {
    "High": (
        "Core to the system's purpose or requested by many stakeholders; "
        "the system is not acceptable without it."
    ),
    "Medium": (
        "Clearly valuable and requested, but the system can go live without it "
        "and add it in a later release."
    ),
    "Low": (
        "Nice to have, requested by a single stakeholder or marginal to the core "
        "workflows; implement only if time allows."
    ),
}

# The consolidate prompt (whole corpus + all candidates) must fit the model's context.
# Estimated at 4 characters per token; sharding a larger corpus is future work.
CONSOLIDATE_MAX_PROMPT_TOKENS: Final[int] = 300_000
