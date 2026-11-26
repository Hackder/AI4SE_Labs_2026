// Created by Claude Code (Opus 5.5)
// Build from Submission/: typst compile --root . report/report.typ

#set document(title: "Week 08. Dissecting the coding assistant", author: "Juraj Petras")
#set page(paper: "a4", margin: (x: 2cm, y: 1.8cm), numbering: "1")
#set text(font: "New Computer Modern", size: 10.5pt)
#set smartquote(enabled: false)
#set par(justify: false, leading: 0.6em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 16pt)
#show heading.where(level: 2): it => {
  v(0.6em)
  text(size: 13pt, it)
  v(0.2em)
}
#show link: set text(fill: rgb("#0057a0"))
#show raw: set text(size: 8.5pt)
#show table: set block(breakable: false)
#set table(
  stroke: (x, y) => if y == 0 { (bottom: 0.7pt) } else { (bottom: 0.3pt + luma(200)) },
  inset: (x: 6pt, y: 4pt),
)
#show table.cell.where(y: 0): strong
#set figure(gap: 0.5em)
#show figure.caption: set text(size: 9pt)

#let shot(path, caption, width: 90%) = figure(
  box(stroke: 0.4pt + luma(180), image(path, width: 100%), width: width),
  caption: caption,
)

= Dissecting the coding assistant

Week 08. Juraj Petras

My main assistant is Claude Code (v2.1.332, model Opus 5.5). I used opencode for Task 4, because Claude Code has no switchable profiles. All files are in `Submission/`. I start the assistants in that folder, so they load its configuration.

== Task 1: System prompt

Claude Code does not let you edit its built-in system prompt. The supported way to change it is an output style. An output style is a Markdown file, and Claude Code adds its body to the system prompt. With `keep-coding-instructions: true` the default coding instructions stay in.

I created `.claude/output-styles/course-assistant.md` and turned it on with `"outputStyle": "Course assistant"` in `.claude/settings.json`. The whole file is the change. One of its lines asks Claude to end each finished task with a `Files touched:` line, so the effect shows in later conversations.

#shot("/screenshots/task1_output_style_file.jpg", [The new output style file.])
#shot("/screenshots/task1_output_style_active.jpg", [Claude Code shows "Course assistant" as the current style.])

== Task 2: Slash command

A Markdown file in `.claude/commands/` becomes a slash command with the file's name. I created `.claude/commands/assignment.md`. The command `/assignment <N>` reads the text of task N and summarizes what it asks, the required output and the points. It takes the task number as an argument, may only read files, and runs on the cheaper Haiku model. Claude Code has merged commands into skills, but command files still work.

#shot("/screenshots/task2_command_file.jpg", [Editing the new command.])
#shot("/screenshots/task2_command_listed.jpg", [Claude Code lists `/assignment` as a project command.], width: 75%)

== Task 3: AGENTS.md

Claude Code's version of `AGENTS.md` is `CLAUDE.md`. The built-in `/init` command creates it. Claude Code reads the whole folder and writes a summary of the project, its files and its commands. It sends this file to the model as context next to my messages, not as part of the system prompt. Recent versions of Claude Code also read `AGENTS.md`, but only when there is no `CLAUDE.md`. Codex and opencode create `AGENTS.md` with their own `/init`.

I ran `/init` once in `Submission/`. It created `CLAUDE.md`, and I did not need a second run.

== Task 4: Profile

Claude Code has no profiles that you can switch between. The closest option is a custom agent that runs the main session (`claude --agent <name>`). You choose it at start, and it has no temperature setting.

opencode has this feature. Its agents are profiles with their own system prompt, model and permissions, and you can switch between them in the app. I created one with `opencode agent create` and then edited it. The file is `.opencode/agents/ai4se-submission-reviewer.md`. It is a read-only reviewer, so it may not run shell commands, edit files or use the web.

#shot("/screenshots/task4_opencode_agent_edit.jpg", [Editing the new opencode agent.])
#shot(
  "/screenshots/task4_opencode_agent_picker.jpg",
  [The new agent next to the default Build agent in opencode.],
  width: 75%,
)

== Task 5: Skill

Claude Code skills live in `.claude/skills/<name>/SKILL.md`. The `description` field tells Claude when to use the skill. Extra files can sit next to `SKILL.md`, and Claude reads them only when needed.

I created `.claude/skills/file-screenshots/`. Its `SKILL.md` moves new screenshots into `screenshots/` and renames them. The file `naming.md` holds the naming rule. When I wrote "screenshots are there", Claude loaded the skill by itself.

#shot("/screenshots/task5_skill_loaded.jpg", [Claude loads the skill without being asked by name.])

== Task 6: Subagents

Claude Code supports subagents out of the box. In a chat I asked it to use a Haiku subagent to summarize the agent configuration in the folder. Opus started an Explore subagent on Haiku 5.5. It ran in the background for about 20 seconds and sent back a summary, which Opus turned into two tables. The conversation is in `transcripts/task6.txt`.

Claude Code also has limits for this. A subagent can have a turn limit and a restricted tool list. At most 20 subagents run at once by default, and they can nest up to 3 levels.

#shot("/screenshots/task6_subagent_conversation.jpg", [Opus hands the work to a Haiku subagent.])

== Task 7: MCP server

Claude Code loads MCP servers listed in `.mcp.json` in the project folder. It asks for approval before it uses a new one.

I wrote a small server in Python 3.14. It is a uv workspace. The root `pyproject.toml` holds the dev tools (ruff, basedpyright in strict mode), and the member package `mcp_server/` (`grades-mcp`) holds the server. It uses the `mcp` 2.x library. The server has one tool, `summarize_graded_points`. It reads the lecturer's and AI gradersufiles in the repository's `Assessments/` folder and adds up the awarded points per week, task and grader. `.mcp.json` starts it with `uv run grades-mcp`.

I asked Claude how many points I have so far. It called the tool and answered 5 out of 5.

#shot("/screenshots/task7_mcp_tool_call.jpg", [Claude calls the `grades` tool.])

== Task 8: Rule

Claude Code loads every Markdown file in `.claude/rules/` as a project rule. I created `.claude/rules/file-attribution.md`. It says that every new file must start with a comment naming the agent and model that created it.

To test it, I asked Claude for a small script that counts the screenshots and did not mention the rule. Claude created `count_screenshots.sh`, and its second line, right after the shebang, is `# Created by Claude Code (Opus 5.5)`. The conversation is in `transcripts/task8.txt`.

== Task 9: Configuration files

I made every change at project level, inside `Submission/`. My global configuration did not change. Claude Code keeps each feature in its own file. `settings.json` only turns on the output style.

#figure(
  table(
    columns: (auto, 1fr),
    align: (left, left),
    [Task], [Files],
    [1], [`.claude/settings.json`, `.claude/output-styles/course-assistant.md`],
    [2], [`.claude/commands/assignment.md`],
    [3], [`CLAUDE.md`],
    [4], [`.opencode/agents/ai4se-submission-reviewer.md`],
    [5], [`.claude/skills/file-screenshots/SKILL.md`, `naming.md`],
    [7], [`.mcp.json`, `pyproject.toml`, `mcp_server/`],
    [8], [`.claude/rules/file-attribution.md`],
  ),
  caption: [Configuration files per task.],
)

These files contain no API keys or other secrets. I removed my organization's name from the screenshots and transcripts.

== Task 10 (Bonus): My workflow with LLMs

// In the end, people end up using LLM-based tools very differently.
//
// What does your usual workflow with LLMs look like (regardless of it being your job, school
// assignments, hobby projects, ...)? Do you only use web-based chat interfaces (ChatGPT), coding
// assistant (which one? and how?), do you copy-paste between Copilot to ChatGPT to verify the
// result? Do you explicitly ask coding assistant to spawn subagents? There are no wrong answers
// (relation student-workflow will not ever be discussed by the lecturer).
//
// Explain your typical workflow and include a figure indicating steps, validation loops and
// components that play role in it.


For simple day-to-day questions I tend to use ChatGPT or Gemini or similar app on my phone.

For tracking tasks and managing things that I need to do (mostly for school) I created
a custom application which wraps sandboxed codex. It gives it bunch of tools (on top of the ones
that the harness has) for example snapshotted memory, watchers for URLs etc. It gets events
from my deterministic watches or other parts of the system (like message from me) and
it does with them whatever needs to be done. For example creates a new todo, calendar event,
messages me, sets up a new watcher etc.

For everything else I only use coding agents like Claude Code or Codex. (mostly claude code).
I have a few skills setup for workflows that I like but it varies project by project.

One workflow that I have starts a planning session, where I discuss possible approaches for a task
with the agent. Explore every possibility. It asks questions, gives suggestions and together
we design the feature / system. Then I send the agent as a manager with subagents to
go and implement, review and test it. When it comes back we iterate on the product. With
the current generation of models there is fairly high chance that the final architecture
is going to roughly resemble what I had in mind after the initial discussion so we iterate from there.

For UI for example I have it make a few versions, and then we iterate on them. Pick the best direction
and explore more and more until we land on something good and use that.

I spend quite a bit of time adding things to the projects so that the agents are more efficient.
For example letting them take screenshots easily. Letting them set up the scenario
they need easily. Letting them create scripted run etc.

#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge

#figure(
  text(size: 8.5pt, diagram(
    spacing: (9mm, 8mm),
    node-stroke: 0.6pt,
    node-corner-radius: 3pt,
    node-inset: 5pt,
    edge-stroke: 0.6pt,
    node((0, 0), [*Me*], name: <me>, fill: luma(230)),
    node((-2, 0), [Phone chat\ (ChatGPT, Gemini)], name: <chat>),
    edge(<me>, <chat>, "<->", [quick questions]),
    node((2, 0), [Task app\ (sandboxed Codex)], name: <app>),
    node((2, -1), [Watchers, URL checks], name: <watch>),
    edge(<watch>, <app>, "->", [events]),
    edge(<me>, <app>, "<->", [todos, calendar,\ messages]),
    node((0, 1), [Planning session\ with the agent], name: <plan>),
    edge(<me>, <plan>, "<->", [discuss, answer\ questions]),
    node((0, 2), [Manager agent\ (Claude Code, Codex)], name: <manager>),
    edge(<plan>, <manager>, "->", [design]),
    node((-1, 3), [Implement], name: <impl>),
    node((0, 3), [Review], name: <review>),
    node((1, 3), [Test], name: <test>),
    edge(<manager>, <impl>, "->"),
    edge(<manager>, <review>, "->"),
    edge(<manager>, <test>, "->"),
    node((0, 4), [Result], name: <result>),
    edge(<impl>, <result>, "->"),
    edge(<review>, <result>, "->"),
    edge(<test>, <result>, "->"),
    edge(<result>, (-1.8, 4), (-1.8, 1), <plan>, "->", [iterate], label-pos: 0.5),
    node((0, 5), [UI: several versions,\ pick a direction, refine], name: <ui>),
    edge(<result>, <ui>, "->", [for UI], bend: 35deg),
    edge(<ui>, <result>, "->", [repeat], bend: 35deg),
    node((2, 3), [Project tooling:\ screenshots, scenarios,\ scripted runs], name: <tools>),
    edge(<tools>, <test>, "-->", [helps]),
  )),
  caption: [My typical workflow. Solid arrows are the main steps, dashed arrows are support.],
)
