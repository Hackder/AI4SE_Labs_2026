"""Run the playground's unittest suite in a subprocess and record, per test, the outcome and
which target methods it called (via ``sys.setprofile``), so failures map to target methods.

``run_tests`` is the API; ``python -m repo_rag.testrun OUT TARGETS`` is the subprocess side.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import FrameType
from typing import Literal

type Outcome = Literal["passed", "failed", "error", "skipped"]


@dataclass(frozen=True)
class TestRecord:
    outcome: Outcome
    targets: list[str]  # qualnames of the target methods the test called
    message: str = ""  # last traceback line for failures and errors


@dataclass(frozen=True)
class TestReport:
    tests: dict[str, TestRecord]

    def count(self, outcome: Outcome) -> int:
        return sum(t.outcome == outcome for t in self.tests.values())

    def counts(self) -> dict[str, int]:
        return {
            "total": len(self.tests),
            "passed": self.count("passed"),
            "failed": self.count("failed"),
            "errors": self.count("error"),
            "skipped": self.count("skipped"),
        }


def run_tests(
    project_dir: Path, targets: list[tuple[Path, str]], timeout_s: float = 300.0
) -> TestReport:
    """Discover and run the tests under ``project_dir`` (the directory holding the package and
    ``tests/``). ``targets`` are (source file, ``Class.method``) pairs to watch for calls.
    No bytecode is written, so running on the committed clone leaves it untouched."""
    fd, name = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    out = Path(name)
    spec = json.dumps([[str(path.resolve()), qualname] for path, qualname in targets])
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        subprocess.run(
            [sys.executable, "-m", "repo_rag.testrun", str(out), spec],
            cwd=project_dir,
            env=env,
            timeout=timeout_s,
            capture_output=True,
            check=True,
        )
        data = json.loads(out.read_text(encoding="utf-8"))
    except subprocess.TimeoutExpired:
        return TestReport({"<suite>": TestRecord("error", [], f"timed out after {timeout_s}s")})
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.decode(errors="replace").strip().splitlines()[-1:]
        return TestReport({"<suite>": TestRecord("error", [], "".join(message))})
    finally:
        out.unlink(missing_ok=True)
    return TestReport({test_id: TestRecord(**record) for test_id, record in data.items()})


class _RecordingResult(unittest.TestResult):
    """Classifies each test by what it appended to failures/errors/skipped."""

    def __init__(self, targets: set[tuple[str, str]]) -> None:
        super().__init__()
        self.records: dict[str, dict[str, object]] = {}
        self._qualnames = {qualname for _, qualname in targets}
        self._targets = targets
        self._called: set[str] = set()
        self._sizes = (0, 0, 0)

    def _profile(self, frame: FrameType, event: str, arg: object) -> None:
        del arg
        code = frame.f_code
        if event != "call" or code.co_qualname not in self._qualnames:
            return
        if (os.path.realpath(code.co_filename), code.co_qualname) in self._targets:
            self._called.add(code.co_qualname)

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self._called = set()
        self._sizes = (len(self.failures), len(self.errors), len(self.skipped))
        sys.setprofile(self._profile)

    def stopTest(self, test: unittest.TestCase) -> None:
        sys.setprofile(None)
        failures, errors, skipped = self._sizes
        outcome, message = "passed", ""
        if len(self.errors) > errors:
            outcome, message = "error", self.errors[-1][1]
        elif len(self.failures) > failures:
            outcome, message = "failed", self.failures[-1][1]
        elif len(self.skipped) > skipped:
            outcome = "skipped"
        last_line = message.strip().splitlines()[-1][:300] if message.strip() else ""
        self.records[test.id()] = {
            "outcome": outcome,
            "targets": sorted(self._called),
            "message": last_line,
        }
        super().stopTest(test)


def _main() -> None:
    out, spec = Path(sys.argv[1]), json.loads(sys.argv[2])
    targets = {(path, qualname) for path, qualname in spec}
    suite = unittest.TestLoader().discover(".")
    result = _RecordingResult(targets)
    suite.run(result)
    out.write_text(json.dumps(result.records), encoding="utf-8")


if __name__ == "__main__":
    _main()
