---
name: architecture-design
description: Design a software architecture from requirements and record it as an ADR. Use when the user has requirements (user stories, a system description, an SRS) and wants architectural proposals, a comparison of several architectures, a chosen architecture discussed in depth, or an Architecture Decision Record. Also use for "propose an architecture", "compare architectures", "which architecture fits", "write an ADR", or the AI4SE week 5 style assignment.
---

# Architecture design and ADR

This skill turns requirements into a chosen architecture and an ADR through a
guided discussion, not a one-shot answer. It was distilled from a full session
on a ticketing and news system. The lessons in `references/lessons.md` are the
mistakes the assistant made in that session and the corrections the user gave.
Read them before proposing anything.

## Working rules

These hold for the whole session unless the user changes them.

1. **One topic at a time.** Present one question or one comparison, then stop and
   wait. Do not answer five things at once. Expect many short rounds.
2. **Do not run ahead.** Finish the phase the user is in. Move to the next phase
   (for example from discussion to the ADR) only when the user says so. If the
   assignment has numbered tasks, treat each as a phase.
3. **Keep notes from the start.** Create `NOTES.md` next to the deliverables at
   the first message and update it after every settled point. Notes are a
   condensed record of decisions and reasons, not a transcript. Headings state
   the point ("A queue defers the problem, so a single writer owns seats"), not
   the topic ("Queues").
4. **Never edit the user's own skills or tooling.** Suggest changes in chat.
5. **When the user disagrees, check the premise first.** The user usually has
   context you lack. Restate what they said, say what changes, and update the
   drivers list. Do not defend a default.
6. **Say when you defaulted.** If you recommended something because it is the
   common choice rather than because the requirements asked for it, say so and
   offer a real comparison.

## Phase 1: Read the requirements and name the drivers

1. Read every requirements file the user points at. Quote story numbers when you
   refer to them.
2. Sort the stories into three groups and show the sorting:
   - **Architectural drivers**: anything with hard correctness rules, contention,
     external systems, background work, data that outlives the user, roles that
     the stories imply but do not name.
   - **Commodity**: auth, profile pages, list views, UI placement. Name them once
     and stop discussing them.
   - **Scope questions**: things the description promises but no story
     exercises. Do not decide these alone. Ask. (Absence of an admin story does
     not mean there is no admin. A platform that "sells tickets" sells tickets
     even when no story buys one.)
3. For each driver ask what varies and where the variation should live.
   Variation goes into data and configuration (a `source_policy` field, a
   `fulfilment_mode` field), not into parallel code paths. Watch for the two
   failure shapes the user will reject: a feature matrix that becomes n²
   code, and sparse software where most code has one caller or none.
4. Separate **assumptions** (facts you take as given about the world or product)
   from **decisions** (choices the design makes). Keep two lists. A sentence like
   "live updates are a property of the system" is a decision, not an assumption.
5. End the phase with a numbered driver list and get the user's agreement
   before proposing anything.

## Phase 2: Propose three or four architectures at a high level

Present them in one table: rows are architectures, columns are the main
subsystems the drivers identified (for example content, purchasing, social),
plus a verdict column. One or two sentences per cell. No component diagrams yet.

Use shapes that genuinely differ, for example:

- A. Modular monolith, one database, a worker mode for background work.
- B. Domain services with their own databases and a message broker.
- C. Event log with purpose-built read models.
- D. Composition of managed services (hosted auth, headless CMS, provider
  checkout, cloud functions).

State which one you lean towards and why, in two sentences. Then stop. The user
will rule some out and pick the subsystem to discuss first.

## Phase 3: Discuss, hardest subsystem first

Go through the subsystems in the order the user picks. For each one, compare
the surviving architectures on that subsystem only. Expect the real design to
be a hybrid: the chosen shape with one part carved out. See
`references/lessons.md` for the specific traps. The ones that cost the most time:

- Horizontal scaling and queues do not fix contention on one hot row. A queue
  defers the spike and adds thousands of waiting connections. The fix is one
  single-threaded writer per contended unit that answers synchronously.
- Every value shown on a page has exactly one source. If it is pushed, nothing
  pulls it on demand. Two sources need reconciliation code that exists only
  because the data was split.
- Do not add caching layers. A stale snapshot with a stated staleness bound,
  corrected by the write path, is acceptable. A cache that needs invalidation
  is not.
- No periodic sweeps on the hot path. Expiry is a query condition on status and
  creation time, not a background job.
- Business policy (grace periods, refunds) is not architecture. Supply the state
  that makes the policy possible and leave the rule to the product.
- Before closing a subsystem, write a **state ownership table**: each piece of
  state, its source of truth, its lifetime. If there are more persistent stores
  than you can justify, something is wrong.
- For the frontend, do not default to a SPA or an SSR metaframework. Compare
  server-rendered HTML with a hypermedia library, islands over a JSON API, and a
  metaframework, against the actual number of stateful places on the site.
- For push versus poll, decide once for the whole system, not per page.
- For infrastructure choices (bus, database notifications, cache), ask what the
  simplest existing component could do and what the dedicated tool adds. Name the
  one deciding reason.
- Defer the language choice unless the user wants it decided. It depends on who
  builds the system. If asked, compare on static guarantees, cost of idle
  connections, and how well a model-assisted developer can review the code.

When the user asks "what are you proposing", restate the whole design as a short
numbered component list and a data-flow summary. Name every component once and
keep those names for the rest of the session.

Close the phase with a full summary: components, state ownership, main flows,
and a numbered list of open decisions with the recommended option and the
deciding factor. Ask whether to move on.

## Phase 4: Write the ADR

Write one record for the whole system when the decisions interlock, and one file
per decision only when the user asks. Use `references/adr-template.md`. Markdown
with Mermaid diagrams is the default. Put the file where the user keeps
deliverables.

Then do a writing pass before showing it, or on request if the user has a
technical-writing skill they prefer:

- Active voice, whole sentences, literal phrasing. No marketing words.
- One name per component, matching the glossary.
- Headings state the point.
- Every assumption is a fact about the world. Every design rule is a choice.
  Move misfiled items.
- Rejected alternatives stay inline, next to the decision they lost to, with the
  one deciding reason.

Expect two or three revision rounds. Typical requests: an overview table of
components, a sequence diagram for the critical flow, a failure-mode table,
splitting a mixed assumption into an assumption and a rule.

## Phase 5: Close

Update `NOTES.md` with the ADR revision history and the final open-decision
list. Tell the user where the notes, the ADR, and the transcript are.
