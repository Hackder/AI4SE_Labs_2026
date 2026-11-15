"""End-to-end mock run: real playground copy, fake embedder, scripted chat model."""

import json
import re
import shutil
from pathlib import Path

from repo_rag.chunker import chunk_repository
from repo_rag.config import MISSING_CODE_PATH, REPO_DIR
from repo_rag.embedder import FakeEmbedder
from repo_rag.generate import compare_runs, load_tasks, run_generation
from repo_rag.llm import Completion, FakeChat
from repo_rag.retrieve import build_index

REPLIES = {
    # fenced, unindented, with prose around it
    "OrderStatus.is_terminal": (
        "Here is the implementation:\n\n```python\n@property\n"
        "def is_terminal(self) -> bool:\n"
        "    return self in (OrderStatus.SHIPPED, OrderStatus.CANCELLED)\n```\nDone."
    ),
    # the whole class
    "Money.__bool__": (
        "```python\nclass Money:\n    def __bool__(self) -> bool:\n"
        "        return self._cents != 0\n```"
    ),
    # indented, no fence
    "EventBus.__contains__": (
        "    def __contains__(self, event_type: object) -> bool:\n"
        "        return bool(self._handlers.get(event_type))\n"
    ),
    "Customer.can_afford": "I cannot implement this.",
}


class ScriptedChat:
    """Canned replies per target; ``OrderLog.by_status`` fails, the rest act like FakeChat."""

    model = "scripted"

    def complete(self, system: str, user: str) -> Completion:
        match = re.search(r"Implement the method `([\w.]+)`", user)
        assert match is not None
        target = match.group(1)
        if target == "OrderLog.by_status":
            raise RuntimeError("API down")
        if target in REPLIES:
            return Completion(REPLIES[target], {"prompt": 100, "completion": 10, "total": 110})
        return FakeChat().complete(system, user)


def _snapshot(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): p.read_text() for p in sorted(root.rglob("*")) if p.is_file()}


def test_mock_run(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    shutil.copytree(REPO_DIR, repo)
    before = _snapshot(repo)
    db = tmp_path / "index.db"
    build_index(chunk_repository(repo), FakeEmbedder(64), db)
    tasks = load_tasks(MISSING_CODE_PATH)

    run_dir = run_generation(tasks, ScriptedChat(), repo, db, tmp_path / "runs")

    assert _snapshot(repo) == before  # the source clone is never modified
    summary = json.loads((run_dir / "summary.json").read_text())
    by_target = {e["target"]: e for e in summary["targets"]}
    assert summary["patch_status"] == {"ok": 7, "extracted": 1, "patch_failed": 1, "llm_error": 1}
    assert by_target["Money.__bool__"]["status"] == "extracted"
    assert by_target["Customer.can_afford"]["raw_response"] == "I cannot implement this."
    assert summary["usage"] == {"prompt": 400, "completion": 40, "total": 440}

    tests = summary["tests"]
    assert tests["baseline"]["total"] == 481 and tests["baseline"]["passed"] == 429
    assert tests["patched"]["total"] == 481
    for target in REPLIES.keys() - {"Customer.can_afford"}:
        result = by_target[target]["tests"]
        assert result["called_by"] > 0 and result["failing"] == [], target
    assert "tests.test_enums.OrderStatusTests.test_shipped_is_terminal" in tests["fixed"]
    failing = by_target["Customer.can_afford"]["tests"]["failing"]
    assert failing and "Customer.can_afford" in tests["failing"][failing[0]]["targets"]

    patched = (run_dir / "playground" / "playground/playground/models.py").read_text()
    assert "return self._cents != 0" in patched
    assert len((run_dir / "trace.jsonl").read_text().splitlines()) == len(tasks)
    assert (run_dir / "summary.md").exists()
    assert run_dir.name in compare_runs(tmp_path / "runs")
