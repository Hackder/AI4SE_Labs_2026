# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- Created by Claude Code (Opus 5.5) -->

## What this directory is

The student's submission for AI4SE Labs 2026, Week 08 ("Dissecting your coding assistant").
The assignment texts live in `../Assignments/Task_N/` (Task 10 is `Task_10_Bonus/`). Most tasks
ask for a config artifact in this folder plus a screenshot or transcript proving it works.
The lab asks the student to do much of the work by hand, so prefer explaining or doing the
specific step requested over completing whole tasks unprompted.

| Task | Artifact in this folder |
|------|-------------------------|
| 1 System prompt | `.claude/output-styles/course-assistant.md`, activated in `.claude/settings.json` |
| 2 Slash command | `.claude/commands/assignment.md` (`/assignment <N>`, runs on Haiku) |
| 3 AGENTS.md | this file |
| 4 Profile/mode | `.opencode/agents/ai4se-submission-reviewer.md` (OpenCode, read-only reviewer) |
| 5 Skill | `.claude/skills/file-screenshots/` |
| 6 Subagents | `transcripts/task6.txt` |
| 7 MCP tool | `mcp_server/` registered in `.mcp.json` as `grades` |
| 8 Rule | `.claude/rules/file-attribution.md`, proof in `transcripts/task8.txt` |

Screenshots go in `screenshots/` named `task<N>_<subject>.jpg` (lowercase, underscores; see
`.claude/skills/file-screenshots/naming.md`). `count_screenshots.sh` prints how many exist.

## Rules that apply here

- Every new file gets an attribution comment on line 1 (or right after a shebang/frontmatter),
  e.g. `# Created by Claude Code (Opus 5.5)`, in the file type's comment syntax.
- The `Course assistant` output style is active: short answers, tables over prose, and every
  task-completing reply ends with `Files touched: <list>`.

## Commands

uv workspace, Python 3.14 only. `exclude-newer` in `pyproject.toml` pins dependencies to
releases at least ~2 weeks old; keep it when adding packages.

```sh
uv sync                        # install workspace + dev tools into .venv
uv run ruff check              # lint (includes import sorting)
uv run ruff format             # format, line length 100
uv run basedpyright            # strict type check of mcp_server/src
uv run grades-mcp              # start the MCP server over stdio
```

There is no test suite. Smoke-test the parser directly:

```sh
uv run python -c "from grades_mcp.server import summarize, find_assessments_dir; print(summarize(find_assessments_dir(), '3'))"
```

## MCP server (`mcp_server/src/grades_mcp/server.py`)

One tool, `summarize_graded_points(week?)`, which parses the lab repo's top-level
`Assessments/*.md` (two levels up: `AI4SE_Labs_2026/Assessments/`). Lookup order: the
`GRADES_ASSESSMENTS_DIR` env var, then the nearest `Assessments/` walking up from the cwd or
from the module file.

Parsing is a line-by-line state machine over this markdown shape:
`# Assessment by <assessor>` → `# Week NN ...` → optional `## Task N` → `- Awarded: Xb out of Yb`.
An `Awarded` line before any `## Task` sets the week total; inside a task it adds a task grade.
If a week has no overall line, its total is the sum of task points. The week filter matches
either a substring of the heading or the week number with leading zeros ignored.

The server uses the `mcp` 2.x API (`from mcp.server import MCPServer`), which differs from
the older `FastMCP` import path found in many examples.
