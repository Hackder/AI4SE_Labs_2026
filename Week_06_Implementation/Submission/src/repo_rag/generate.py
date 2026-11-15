"""Task 5: implement the missing methods with the RAG pipeline and test the result.

One run = one chat model: copy the playground to ``output/runs/<timestamp>_<model>/playground``,
and for every ``missing_code.json`` entry retrieve the top chunks, ask the model for the
method, and patch it into the copy. Then run the unit tests on the committed clone (baseline)
and on the copy, and write ``summary.json``, ``summary.md`` and ``trace.jsonl`` (every LLM
call). The committed clone is never modified.
"""

from __future__ import annotations

import ast
import json
import shutil
import textwrap
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import DB_PATH, REPO_DIR, RUNS_DIR, TEST_DIR
from .llm import ChatModel
from .patcher import find_method, patch_method, start_line
from .retrieve import retrieve
from .store import Hit, VectorStore
from .testrun import TestReport, run_tests

SYSTEM_PROMPT = """\
You implement one missing method in an existing Python repository.
Reply with only the complete method definition (decorators, signature, docstring and body) \
in a single ```python code block, without explanation.
Keep the stub's decorators and signature. Do not add imports or other code: use only names \
already available in the method's module, and follow the conventions of the repository code \
you are shown."""


@dataclass(frozen=True)
class Task:
    file: str  # relative to the clone root
    class_name: str
    method: str
    docstring: str

    @property
    def qualname(self) -> str:
        return f"{self.class_name}.{self.method}"


def load_tasks(path: Path) -> list[Task]:
    entries: list[dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))
    return [Task(e["file"], e["class"], e["method"], e["docstring"]) for e in entries]


def task_text(task: Task, repo_dir: Path) -> str:
    """The task as given to retrieval and the model: target, docstring and the stub (its
    decorators and signature from the file, with the docstring filled in)."""
    source = (repo_dir / task.file).read_text(encoding="utf-8")
    node = find_method(ast.parse(source), task.class_name, task.method)
    lines = source.splitlines(keepends=True)
    signature = textwrap.dedent("".join(lines[start_line(node) - 1 : node.body[0].lineno - 1]))
    docstring = task.docstring.strip()
    stub = f"{signature}    {docstring}\n    pass\n"
    return (
        f"Implement the method `{task.qualname}` in `{task.file}`.\n"
        f"It must: {docstring.strip('"').strip()}\n\n"
        f"Current stub:\n```python\n{stub}```\n"
    )


def build_prompt(text: str, hits: list[Hit]) -> str:
    """Retrieved chunks first, the task (ending with the stub) last."""
    if not hits:
        return f"## Task\n\n{text}"
    context = "\n\n".join(
        f"### {h.chunk.path}:{h.chunk.start_line}-{h.chunk.end_line} ({h.chunk.qualname})\n"
        f"```python\n{h.chunk.text.rstrip()}\n```"
        for h in hits
    )
    return f"Relevant code retrieved from the repository:\n\n{context}\n\n## Task\n\n{text}"


def variant(n: int, include_tests: bool) -> str:
    """Short name of the retrieval setting: ``default`` (top 5 incl. tests), ``no-tests``,
    ``no-rag`` (no chunks), or ``n<k>`` for another chunk count."""
    if n == 0:
        return "no-rag"
    name = "default" if n == 5 else f"n{n}"
    return name if include_tests else ("no-tests" if n == 5 else f"{name}-no-tests")


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def run_generation(
    tasks: list[Task],
    chat: ChatModel,
    repo_dir: Path = REPO_DIR,
    db_path: Path = DB_PATH,
    runs_dir: Path = RUNS_DIR,
    n: int = 5,
    include_tests: bool = True,
) -> Path:
    """Generate, patch and test one run; returns the run directory."""
    started = _now()
    setting = variant(n, include_tests)
    suffix = "" if setting == "default" else f"_{setting}"
    run_dir = runs_dir / f"{datetime.now():%Y%m%d-%H%M%S}_{chat.model}{suffix}"
    work = run_dir / "playground"
    shutil.copytree(repo_dir, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    store = VectorStore(db_path)
    embedding_model = store.meta()["embedding_model"]
    store.close()

    # Generate and patch, one LLM call per entry, each traced.
    entries: list[dict[str, Any]] = []
    with (run_dir / "trace.jsonl").open("w", encoding="utf-8") as trace:
        for task in tasks:
            text = task_text(task, repo_dir)
            hits = retrieve(text, n, db_path, include_tests=include_tests) if n > 0 else []
            prompt = build_prompt(text, hits)
            record: dict[str, Any] = {
                "started_at": _now(),
                "target": task.qualname,
                "model": chat.model,
                "retrieved": [{"id": h.chunk.id, "score": round(h.score, 4)} for h in hits],
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            }
            entry: dict[str, Any] = {
                "target": task.qualname,
                "file": task.file,
                "retrieved": record["retrieved"],
                "usage": {},
            }
            t0 = time.perf_counter()
            try:
                completion = chat.complete(SYSTEM_PROMPT, prompt)
            except Exception as exc:  # noqa: BLE001 - one failed call must not stop the run
                record["error"] = entry["error"] = f"{type(exc).__name__}: {exc}"
                entry["status"] = "llm_error"
            else:
                record["raw_response"] = entry["raw_response"] = completion.text
                record["usage"] = entry["usage"] = completion.usage
                result = patch_method(
                    work / task.file, task.class_name, task.method, completion.text
                )
                entry |= {"status": result.status, "code": result.code, "error": result.error}
            record["ended_at"] = _now()
            record["duration_ms"] = int((time.perf_counter() - t0) * 1000)
            trace.write(json.dumps(record, ensure_ascii=False) + "\n")
            trace.flush()
            entries.append(entry)

    # Test the committed clone (baseline) and the patched copy.
    def targets(root: Path) -> list[tuple[Path, str]]:
        return [(root / t.file, t.qualname) for t in tasks]

    baseline = run_tests(repo_dir / TEST_DIR, targets(repo_dir))
    patched = run_tests(work / TEST_DIR, targets(work))
    for entry in entries:
        entry["tests"] = _target_tests(patched, entry["target"])

    summary = {
        "model": chat.model,
        "run": run_dir.name,
        "started_at": started,
        "ended_at": _now(),
        "variant": setting,
        "retrieval": {"embedding_model": embedding_model, "n": n, "include_tests": include_tests},
        "patch_status": dict(Counter(e["status"] for e in entries)),
        "usage": dict(sum((Counter(e["usage"]) for e in entries), Counter[str]())),
        "tests": {
            "baseline": baseline.counts(),
            "patched": patched.counts(),
            "delta_passed": patched.count("passed") - baseline.count("passed"),
            "fixed": _changed(baseline, patched, to_passed=True),
            "broken": _changed(baseline, patched, to_passed=False),
            "failing": {
                tid: {"outcome": t.outcome, "targets": t.targets, "message": t.message}
                for tid, t in sorted(patched.tests.items())
                if t.outcome in ("failed", "error")
            },
        },
        "targets": entries,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    (run_dir / "summary.md").write_text(_summary_md(summary), encoding="utf-8")
    return run_dir


def _target_tests(report: TestReport, qualname: str) -> dict[str, Any]:
    """Tests that called the target method, and which of them did not pass."""
    calling = {tid: t for tid, t in report.tests.items() if qualname in t.targets}
    failing = sorted(tid for tid, t in calling.items() if t.outcome in ("failed", "error"))
    return {"called_by": len(calling), "passed": len(calling) - len(failing), "failing": failing}


def _changed(baseline: TestReport, patched: TestReport, to_passed: bool) -> list[str]:
    return sorted(
        tid
        for tid, t in patched.tests.items()
        if tid in baseline.tests
        and (t.outcome == "passed") == to_passed
        and (baseline.tests[tid].outcome == "passed") != to_passed
    )


def _summary_md(s: dict[str, Any]) -> str:
    base, after = s["tests"]["baseline"], s["tests"]["patched"]
    model = f"- Model: `{s['model']}`; variant `{s['variant']}`: top {s['retrieval']['n']} chunks, "
    model += f"embeddings `{s['retrieval']['embedding_model']}`"
    tests = f"- Tests: {after['passed']}/{after['total']} passed (baseline "
    tests += f"{base['passed']}/{base['total']}, delta {s['tests']['delta_passed']:+d}); "
    tests += f"failed {after['failed']}, errors {after['errors']}"
    changed = f"- Fixed vs baseline: {len(s['tests']['fixed'])}, "
    changed += f"broken vs baseline: {len(s['tests']['broken'])}"
    lines = [
        f"# Run {s['run']}",
        "",
        model,
        f"- Patch status: {s['patch_status']}",
        f"- Tokens: {s['usage'] or 'not reported'}",
        tests,
        changed,
        "",
        "| Target | Patch | Tests calling it | Passed | Failing |",
        "|---|---|---|---|---|",
    ]
    for e in s["targets"]:
        t = e["tests"]
        lines.append(
            f"| `{e['target']}` | {e['status']} | {t['called_by']} | {t['passed']} "
            f"| {len(t['failing'])} |"
        )
    if s["tests"]["failing"]:
        lines += ["", "Failing tests, with the target methods each one called:", ""]
        lines += [
            f"- `{tid}` [{', '.join(t['targets']) or 'no target'}]: {t['message']}"
            for tid, t in s["tests"]["failing"].items()
        ]
    return "\n".join(lines) + "\n"


def compare_runs(runs_dir: Path = RUNS_DIR) -> str:
    """Markdown over every ``summary.json`` under ``runs_dir``: one row per run, then a pass
    matrix of target methods x runs (tests calling the method that pass, ``k/N``)."""
    runs = [
        json.loads(p.read_text(encoding="utf-8")) for p in sorted(runs_dir.glob("*/summary.json"))
    ]
    statuses = ("ok", "extracted", "patch_failed", "llm_error")
    lines = [
        "| Run | Model | Variant | Embeddings | " + " | ".join(statuses) + " | Tests passed "
        "| Delta | Targets all-pass | Tokens |",
        "|---|---|---|---|" + "---|" * len(statuses) + "---|---|---|---|",
    ]
    for s in runs:
        after = s["tests"]["patched"]
        all_pass = sum(
            e["tests"]["called_by"] > 0 and not e["tests"]["failing"] for e in s["targets"]
        )
        retrieval = s["retrieval"]
        lines.append(
            f"| {s['run']} | {s['model']} | {variant(retrieval['n'], retrieval['include_tests'])} "
            f"| {retrieval['embedding_model']} | "
            + " | ".join(str(s["patch_status"].get(k, 0)) for k in statuses)
            + f" | {after['passed']}/{after['total']} | {s['tests']['delta_passed']:+d} "
            f"| {all_pass}/{len(s['targets'])} | {s['usage'].get('total', '-')} |"
        )
    if not runs:
        return "\n".join(lines) + "\n"

    # Pass matrix: one column per run, labelled model and variant.
    labels = []
    for s in runs:
        setting = variant(s["retrieval"]["n"], s["retrieval"]["include_tests"])
        labels.append(s["model"] + ("" if setting == "default" else f" ({setting})"))
    lines += ["", "| Method | " + " | ".join(labels) + " |", "|---|" + "---|" * len(runs)]
    tests = [{e["target"]: e["tests"] for e in s["targets"]} for s in runs]
    for target in tests[0]:
        cells = []
        for by_target in tests:
            t = by_target[target]
            mark = "ok" if t["called_by"] and not t["failing"] else "FAIL"
            cells.append(f"{t['passed']}/{t['called_by']} {mark}")
        lines.append(f"| `{target}` | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"
