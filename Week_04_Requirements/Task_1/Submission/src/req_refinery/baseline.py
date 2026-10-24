"""Single-call baseline: one gpt-5.6-luna completion over the whole corpus.

Run: uv run python -m req_refinery.baseline --input <dir> --output <dir>
"""

import argparse
import asyncio
import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import openai
from dotenv import load_dotenv

from req_refinery.config import PRIORITY_SCALE
from req_refinery.prompts import REQUIREMENT_DEFINITION

MODEL: Final[str] = "gpt-5.6-luna"
MAX_OUTPUT_TOKENS: Final[int] = 128_000
TIMEOUT_S: Final[float] = 1800.0
TRANSPORT_ATTEMPTS: Final[int] = 4
BACKOFF_S: Final[tuple[float, ...]] = (5.0, 15.0, 30.0)

OUTPUT_CRITERIA: Final[str] = """\
- OS1. Single structured document
- OS2. Unique identification of each requirement
- OS3. No (semantically) duplicate requirements
- OS4. Tracing - for each requirement, from which input documents was it derived?
- OS5. Each requirement should have a short descriptive name and a paragraph-long explanation
- OS6. Each requirement should have assigned its priority; priority scale should be explained \
in the document
- OS7. Consistency across requirements - consistent language and vocabulary, no semantically \
contradictive/conflicting requirements
- OS8. Completeness - Make sure not to ignore requirements from the input documents
- OS9. Blacklist - if an identified requirement is discarded because it is confliting, or \
nonsensical, it should also be recorded in separate section with explanation why it was \
discarded"""

FORMAT_TEMPLATE: Final[str] = """\
# Software Requirements Specification

This document specifies the requirements for <system name>, derived from <N> input \
documents. It contains <R> requirements and <B> blacklisted (discarded) items. Requirement \
numbers are unique within this document.

## Input documents

1. D01 — <path of D01>
2. D02 — <path of D02>
...

## Priority scale

{priority_lines}

## Glossary

| Term | Definition |
| --- | --- |
| <term> | <definition> |

## Requirements: High priority

### R001  <Short descriptive name>

**Priority:** High. <One or two sentences justifying the priority.>

<One paragraph explaining the requirement: what, for whom, under what condition.>

**Sources:** D04 (<path of D04>), D10 (<path of D10>)

### R002  <Short descriptive name>

...

## Requirements: Medium priority

(same entry format; write "None." if there are none)

## Requirements: Low priority

(same entry format; write "None." if there are none)

## Blacklist

### B01  <Short descriptive name of the discarded requirement>

**Priority:** <High|Medium|Low>. <Justification.>

<One paragraph explaining the discarded requirement.>

**Sources:** D10 (<path of D10>)

**Reason:** <Why it was discarded: which requirement it conflicts with, or why it is \
nonsensical.>

(write "None." if nothing was discarded)

## Open issues

- **<issue type>** (R012, R034): <explanation of an unresolved problem>

(omit this section entirely if there are no open issues)

## Coverage

| Document | Path | Requirements | Blacklist |
| --- | --- | --- | --- |
| D01 | <path of D01> | R042, R043 | B01 |
... one row per input document ...
"""

SYSTEM_PROMPT: Final[str] = """\
You are a requirements engineer. You receive a corpus of documents (e-mail threads, \
interviews, meeting minutes, surveys, draft specifications, reference material) about one \
software system and produce a single consolidated software requirements specification."""


@dataclass(frozen=True)
class Document:
    id: str
    path: str
    text: str


@dataclass
class Completion:
    text: str
    finish_reason: str | None
    usage: dict[str, int]
    transport_retries: int


def load_documents(root: Path) -> list[Document]:
    """Same ordering and ID convention as nodes/load.py (without the limit option)."""
    if not root.is_dir():
        raise FileNotFoundError(f"input directory not found: {root}")
    files = sorted(
        (p for p in root.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(root).as_posix(),
    )
    texts: list[tuple[str, str]] = []
    for path in files:
        data = path.read_bytes()
        if b"\x00" in data[:8192]:
            continue
        texts.append((path.relative_to(root).as_posix(), data.decode("utf-8", errors="replace")))
    if not texts:
        raise ValueError(f"no text documents found in {root}")
    width = max(2, len(str(len(texts))))
    return [
        Document(id=f"D{i:0{width}d}", path=rel, text=text)
        for i, (rel, text) in enumerate(texts, start=1)
    ]


def build_prompt(documents: list[Document]) -> str:
    priority_lines = "\n".join(f"- **{k}:** {v}" for k, v in PRIORITY_SCALE.items())
    parts = [
        "Produce a software requirements specification from the documents below.",
        "",
        "## Output criteria",
        "",
        "The document must satisfy all of these criteria:",
        "",
        OUTPUT_CRITERIA,
        "",
        "## Requirement granularity",
        "",
        REQUIREMENT_DEFINITION.rstrip(),
        "",
        "## Priority scale",
        "",
        (
            "Assign every requirement exactly one of these priorities and reproduce this scale "
            "verbatim in the document:"
        ),
        "",
        priority_lines,
        "",
        "## Output format",
        "",
        (
            "Write the document in exactly this markdown format. Number requirements R001, R002, "
            "... consecutively across the three priority sections in the order they appear, and "
            "blacklist entries B01, B02, .... Use two spaces between the ID and the name in "
            "headings. Every requirement and blacklist entry lists all documents it was derived "
            "from on its Sources line as ID followed by the path in parentheses. The coverage "
            "table has one row per input document listing every requirement and blacklist entry "
            "that cites it. The glossary defines the key terms used consistently across the "
            "requirements."
        ),
        "",
        "```markdown",
        FORMAT_TEMPLATE.format(priority_lines=priority_lines).rstrip(),
        "```",
        "",
        (
            "Respond with the complete markdown document and nothing else: no preamble, no "
            "closing remarks, no code fence around it."
        ),
        "",
        f"## Input documents ({len(documents)})",
        "",
    ]
    for d in documents:
        parts += [f"=== {d.id} — {d.path} ===", d.text.rstrip(), f"=== end of {d.id} ===", ""]
    return "\n".join(parts).rstrip() + "\n"


async def complete(client: openai.AsyncOpenAI, prompt: str) -> Completion:
    retries = 0
    while True:
        try:
            return await _stream_once(client, prompt, retries)
        except openai.APIConnectionError:
            if retries + 1 >= TRANSPORT_ATTEMPTS:
                raise
            await asyncio.sleep(BACKOFF_S[min(retries, len(BACKOFF_S) - 1)])
            retries += 1


async def _stream_once(client: openai.AsyncOpenAI, prompt: str, retries: int) -> Completion:
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=MAX_OUTPUT_TOKENS,
        stream=True,
        stream_options={"include_usage": True},
    )
    chunks: list[str] = []
    finish_reason: str | None = None
    usage: dict[str, int] = {}
    async for chunk in stream:
        for choice in chunk.choices:
            if choice.delta.content:
                chunks.append(choice.delta.content)
            if choice.finish_reason is not None:
                finish_reason = choice.finish_reason
        if chunk.usage is not None:
            usage = {
                "prompt": chunk.usage.prompt_tokens,
                "completion": chunk.usage.completion_tokens,
                "total": chunk.usage.total_tokens,
            }
            details = chunk.usage.completion_tokens_details
            if details is not None and details.reasoning_tokens is not None:
                usage["reasoning"] = details.reasoning_tokens
    return Completion("".join(chunks), finish_reason, usage, retries)


async def run(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    documents = load_documents(input_dir)
    prompt = build_prompt(documents)
    out_dir = output_dir / "baseline"
    out_dir.mkdir(parents=True, exist_ok=True)
    client = openai.AsyncOpenAI(timeout=TIMEOUT_S)
    started = datetime.now(UTC)
    t0 = time.perf_counter()
    result = await complete(client, prompt)
    wall_s = time.perf_counter() - t0
    finished = datetime.now(UTC)
    _ = (out_dir / "requirements.md").write_text(result.text, encoding="utf-8")
    record: dict[str, Any] = {
        "model": MODEL,
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "wall_time_s": round(wall_s, 3),
        "finish_reason": result.finish_reason,
        "truncated": result.finish_reason == "length",
        "transport_retries": result.transport_retries,
        "usage": result.usage,
        "input_dir": str(input_dir),
        "documents": [{"id": d.id, "path": d.path, "chars": len(d.text)} for d in documents],
        "system_prompt": SYSTEM_PROMPT,
        "prompt": prompt,
        "raw_response": result.text,
    }
    _ = (out_dir / "run.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-call requirements baseline")
    _ = parser.add_argument("--input", type=Path, required=True, help="corpus directory")
    _ = parser.add_argument("--output", type=Path, required=True, help="output directory")
    args = parser.parse_args()
    input_dir: Path = args.input
    output_dir: Path = args.output
    _ = load_dotenv()
    record = asyncio.run(run(input_dir, output_dir))
    usage: dict[str, int] = record["usage"]
    print(
        f"wall {record['wall_time_s']}s, finish_reason {record['finish_reason']}, "
        f"tokens {usage}, wrote {output_dir / 'baseline'}"
    )


if __name__ == "__main__":
    main()
