"""MCP server with one tool that summarizes the graded points in the lab repository.

The lecturer and AI graders put their assessments in `Assessments/*.md` at the top of the
AI4SE_Labs_2026 repository. Each file starts with `# Assessment by <assessor>`, then has one
`# Week NN <name>` section per graded week with an overall `- Awarded: Xb out of Yb` line and
`## Task N` subsections with their own `- Awarded:` lines.
"""

import os
import re
from pathlib import Path

from mcp.server import MCPServer
from pydantic import BaseModel

ENV_DIR = "GRADES_ASSESSMENTS_DIR"

_ASSESSOR = re.compile(r"^#\s+Assessment by\s+(.+?)\s*$")
_WEEK = re.compile(r"^#\s+(Week\s*\d+.*?)\s*$")
_TASK = re.compile(r"^##\s+(Task\s*\S+)\s*$")
_AWARDED = re.compile(
    r"^-\s*Awarded:\s*([\d.]+)\s*b(?:\s*(?:out of|\(max)\s*([\d.]+)\s*b)?", re.IGNORECASE
)


class TaskGrade(BaseModel):
    task: str
    awarded: float
    max: float | None


class WeekGrade(BaseModel):
    week: str
    assessor: str
    source_file: str
    awarded: float
    max: float | None
    tasks: list[TaskGrade]


class GradeSummary(BaseModel):
    assessments_dir: str
    weeks: list[WeekGrade]
    total_awarded_by_assessor: dict[str, float]


def find_assessments_dir() -> Path:
    """Use $GRADES_ASSESSMENTS_DIR, else the nearest `Assessments/` above the cwd or this file."""
    if env := os.environ.get(ENV_DIR):
        return Path(env).resolve()
    for start in (Path.cwd(), Path(__file__).resolve()):
        for parent in (start, *start.parents):
            candidate = parent / "Assessments"
            if candidate.is_dir():
                return candidate
    raise FileNotFoundError(f"No Assessments/ directory found; set {ENV_DIR}")


def _awarded(line: str) -> tuple[float, float | None] | None:
    match = _AWARDED.match(line.strip())
    if match is None:
        return None
    awarded, maximum = match.groups()
    return float(awarded), float(maximum) if maximum is not None else None


def parse_assessment(path: Path) -> list[WeekGrade]:
    assessor = path.stem
    weeks: list[WeekGrade] = []
    task: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if m := _ASSESSOR.match(line):
            assessor = m.group(1)
        elif m := _WEEK.match(line):
            weeks.append(
                WeekGrade(
                    week=m.group(1),
                    assessor=assessor,
                    source_file=path.name,
                    awarded=0.0,
                    max=None,
                    tasks=[],
                )
            )
            task = None
        elif m := _TASK.match(line):
            task = m.group(1)
        elif (points := _awarded(line)) is not None and weeks:
            awarded, maximum = points
            week = weeks[-1]
            if task is None:
                week.awarded, week.max = awarded, maximum
            else:
                week.tasks.append(TaskGrade(task=task, awarded=awarded, max=maximum))
    for week in weeks:
        if week.awarded == 0.0 and week.tasks:
            week.awarded = sum(t.awarded for t in week.tasks)
    return weeks


def summarize(directory: Path, week_filter: str | None = None) -> GradeSummary:
    weeks: list[WeekGrade] = []
    for path in sorted(directory.glob("*.md")):
        weeks.extend(parse_assessment(path))
    if week_filter:
        digits = re.sub(r"\D", "", week_filter)
        weeks = [
            w
            for w in weeks
            if week_filter.lower() in w.week.lower()
            or (digits and re.sub(r"\D", "", w.week).lstrip("0") == digits.lstrip("0"))
        ]
    totals: dict[str, float] = {}
    for w in weeks:
        totals[w.assessor] = totals.get(w.assessor, 0.0) + w.awarded
    return GradeSummary(
        assessments_dir=str(directory), weeks=weeks, total_awarded_by_assessor=totals
    )


mcp = MCPServer("grades")


@mcp.tool()
def summarize_graded_points(week: str | None = None) -> GradeSummary:
    """Summarize the points awarded in the lab's Assessments/ folder.

    Returns, per graded week and assessor (human lecturer or AI grader), the awarded and
    maximum points overall and per task, plus the total awarded per assessor.

    Args:
        week: Optional filter such as "3", "Week 03" or "Prompting". Omit for all weeks.
    """
    return summarize(find_assessments_dir(), week)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
