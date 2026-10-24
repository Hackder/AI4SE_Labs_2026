// Co-written by Claude Fable 5.1 and Claude Opus 5.5
#import "@preview/fletcher:0.5.8" as fletcher: diagram, edge, node
// Build from Submission/: typst compile --root . report/report.typ
// Every number comes from the run outputs, read and processed at compile time in data.typ.
#import "data.typ": grades, history, outputs, round-marks, summary, timeline-rows, unassigned

// Opus 5.5 grades (reviewer_grades.json) are copied by hand from the final comparison
// table of the Opus 5.5 grading report. Its columns map to run dirs, by the run dirs and
// requirement counts named in the Opus 5.5 messages:
//   Run 7 = 20261024_165734, Run 8 = 20261024_172523, Run 9 = 20261024_174514,
//   Run 10 = 20261024_183024, Baseline = output/baseline (51 requirements),
//   Hybrid 1 = 20261024_184705_hybrid, Hybrid 2 = 20261024_191559_hybrid,
//   Hybrid 3 = 20261024_194017_hybrid, Delivered = 20261024_202345_hybrid.
// The final network run 20261024_203609_network was graded later in a separate report.

#let hyb = outputs.hybrid
#let net = outputs.network
#let base = outputs.baseline
#let dev-runs = history.filter(r => r.run != "baseline")
#let base-row = history.find(r => r.run == "baseline")
#let hist(id) = dev-runs.find(r => r.run == id)
#let rn(id, size: 8.5pt) = {
  show raw: set text(size: size)
  raw(id)
}
#let grade-of(id) = {
  let g = grades.find(x => x.run == id)
  if g == none { none } else { g.grade }
}
#let final-grade = grade-of("20261024_202345_hybrid")
#let base-grade = grade-of("baseline")

// ---------- Formatting helpers ----------
#let thousands(n) = {
  let s = str(n)
  let out = ""
  for (i, c) in s.clusters().enumerate() {
    if i > 0 and calc.rem(s.len() - i, 3) == 0 { out += "," }
    out += c
  }
  out
}
#let pct(x) = str(calc.round(x * 100)) + "%"
#let secs(x) = str(calc.round(float(x))) + " s"
#let ktok(n) = str(calc.round(n / 1000)) + "k"
#let sum-tokens(t) = t.values().sum(default: 0)
#let row-tokens(r) = {
  let keys = r.keys().filter(k => k.starts-with("tokens_total_"))
  keys.map(k => if r.at(k) == "" { 0 } else { int(r.at(k)) }).sum()
}
#let node-row(graph, name) = summary.find(r => r.graph == graph and r.node == name)
#let gstr(g) = if g == none [–] else [#g]

// ---------- Page style (same as Week 03) ----------
#set document(title: "Week 04, Task 1. Agentic network for requirements refinement", author: "Juraj Petras")
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
#show heading.where(level: 3): set text(size: 11pt)
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

// ---------- Colours ----------
#let llm-fill = rgb("#dbe9f6")
#let llm-stroke = rgb("#0072B2")
#let det-fill = rgb("#fbe8cc")
#let det-stroke = rgb("#C77700")
#let loop-col = rgb("#D62728")
#let model-col = (
  "gpt-6-luna": rgb("#0072B2"),
  "gpt-5.6-luna": rgb("#E69F00"),
  "gpt-5-mini": rgb("#009E73"),
  "": luma(90),
)

// ---------- Diagram helpers ----------
#let llm(pos, name, label, ..args) = node(
  pos,
  raw(name),
  fill: llm-fill,
  stroke: 0.7pt + llm-stroke,
  corner-radius: 3pt,
  inset: 5pt,
  name: label,
  ..args,
)
#let det(pos, name, label, ..args) = node(
  pos,
  raw(name),
  fill: det-fill,
  stroke: 0.7pt + det-stroke,
  corner-radius: 3pt,
  inset: 5pt,
  name: label,
  ..args,
)
#let el(body) = text(size: 7.5pt, body)
#let lp(body) = text(size: 7.5pt, fill: loop-col, body)
#let legend = align(center, text(size: 8.5pt)[
  #box(width: 1.1em, height: 0.8em, fill: llm-fill, stroke: 0.7pt + llm-stroke, radius: 2pt) LLM node
  #h(1.5em)
  #box(width: 1.1em, height: 0.8em, fill: det-fill, stroke: 0.7pt + det-stroke, radius: 2pt) Deterministic node
])

= Agentic network for requirements refinement

Week 04, Task 1. Juraj Petras

== Introduction

The input is 20 plain-text files about the reports module of PINES, a library consortium running Evergreen, all from 2009. They are an early SRS draft, meeting minutes, two interviews, e-mail threads, a staff survey and a reference description of the old system.

The network is a LangGraph graph in `src/req_refinery/` with two versions. I built `network` first. It extracts candidates per document, merges duplicates by their text in `merge_dedup` and checks coverage per document, so no call ever sees the whole corpus. A review loop then refines the list for up to 5 rounds. Its best run before the hybrid got #grade-of("20261024_183024")/10 from Claude Opus 5.5, which graded all the documents.

I then compared it with a baseline, `src/req_refinery/baseline.py`, that sends all 20 documents to `gpt-5.6-luna` in one call with the output criteria, the requirement definition, the priority scale and a document template. It got #base-grade/10. It missed many items, but it had far fewer duplicates than the network, because one call could compare everything at once.

The `hybrid` version combines the two. It keeps the per-document `extract` as a checklist and replaces `merge_dedup` and the coverage pass with one `consolidate` call that, like the baseline, sees all 20 documents. Its document, `output/hybrid/requirements.md`, has #hyb.requirements requirements, #hyb.blacklist blacklisted items and #hyb.questions stakeholder questions, and Claude Opus 5.5 rated it #final-grade/10.

== The network

#figure(
  kind: image,
  stack(spacing: 0.5cm, diagram(
    spacing: (14mm, 6mm),
    edge-stroke: 0.7pt,
    mark-scale: 80%,
    det((0, 0), "load_corpus", <load>),
    llm((0, 1), "extract", <extract>, extrude: (0, 2.5)),
    llm((0, 2), "consolidate", <cons>),
    llm((0, 3), "assign_unassigned", <unas>),
    llm((0, 4), "prioritize", <prio>),
    det((0, 5), "assign_ids", <ids>),
    llm((0, 6), "review", <review>),
    llm((0, 7.3), "document_pass[attribution]", <attr>, extrude: (0, 2.5)),
    det((0, 8.3), "apply_document_pass[attribution]", <aattr>),
    det((0, 9.3), "render", <render>),
    det((1.4, 6), "group_issues", <group>),
    llm((1.4, 5), "resolve_issue", <resolve>, extrude: (0, 2.5)),
    det((1.4, 4), "apply_resolutions", <apply>),

    edge(<load.south>, <extract.north>, "-|>", el[Send per document], label-side: left),
    edge(<extract.south>, <cons.north>, "-|>"),
    edge(<cons.south>, <unas.north>, "-|>"),
    edge(<unas.south>, <prio.north>, "-|>"),
    edge(<prio.south>, <ids.north>, "-|>"),
    edge(<ids.south>, <review.north>, "-|>"),
    edge(<review.south>, <attr.north>, "-|>", el[accept, or round 5], label-side: left),
    edge(<attr.south>, <aattr.north>, "-|>"),
    edge(<aattr.south>, <render.north>, "-|>"),

    edge(<review.east>, <group.west>, "-|>", stroke: 0.9pt + loop-col, lp[targeted]),
    edge(<group.north>, <resolve.south>, "-|>", stroke: 0.9pt + loop-col, lp[Send per group], label-side: right),
    edge(<resolve.north>, <apply.south>, "-|>", stroke: 0.9pt + loop-col),
    edge(<apply.west>, <prio.east>, "-|>", stroke: 0.9pt + loop-col, lp[next round], label-side: right),
    edge(<group.south>, (1.4, 7.3), <attr.east>, "-|>", el[no groups left], label-side: left),
  ), legend),
  caption: [The `hybrid` graph, the default. Red edges are the review loop, which runs when `review` returns the route `targeted`. Nodes with a double border run once per document or once per issue group, in parallel through LangGraph `Send`.],
) <fig-hybrid>

#let ua = unassigned.hybrid
#let node-info = (
  ("load_corpus", [Reads every text file under the input dir and numbers them D01 to Dn.]),
  ("extract", [One call per document. Returns the candidate requirements of that document.]),
  ("consolidate", [One call with all documents in full and all candidates as a checklist. Returns requirements with sources, a glossary, a blacklist and stakeholder questions.]),
  ("merge_dedup", [Only in `network`. Merges duplicate candidates from their text alone.]),
  ("assign_unassigned", [`consolidate` and `merge_dedup` should fold each candidate into a requirement or into the blacklist, but they can skip a few. This node gets the skipped ones. If an existing requirement already says the same thing, it adds the candidate's document to that requirement's sources. Otherwise it adds the candidate as a new requirement. In the final hybrid run #ua.leftover of #ua.extracted candidates were skipped, #ua.mapped was mapped and #ua.new were added.]),
  ("document_pass[coverage]", [Only in `network`. Per document, finds which requirements it supports and what is missing.]),
  ("prioritize", [Gives High, Medium or Low with a one-sentence reason to items without a priority.]),
  ("assign_ids", [Sorts by priority, source and name, then numbers R001 to Rn.]),
  ("review", [Checks the whole list and returns typed issues and the route.]),
  ("group_issues", [Joins issues that share a requirement into groups and drops granularity issues on settled items.]),
  ("resolve_issue", [One call per group. Returns replacement requirements and blacklist entries.]),
  ("apply_resolutions", [Deletes the involved requirements, inserts the replacements and validates the list.]),
  ("document_pass[attribution]", [Runs after the loop. Per document, finds which requirements it supports.]),
  ("apply_document_pass[attribution]", [Rewrites the sources of every requirement. Statements that no requirement covers become `possibly missed` open issues.]),
  ("render", [Writes `requirements.md` and `requirements.json`.]),
)
#let model-of(name) = {
  let r = node-row("hybrid", name)
  if r == none { r = node-row("network", name) }
  if r.model == "" [–] else { raw(r.model) }
}
#let kind-of(name) = {
  let r = node-row("hybrid", name)
  if r == none { r = node-row("network", name) }
  if r.kind == "llm" [LLM] else [code]
}

#table(
  columns: (auto, auto, auto, 1fr),
  table.header[Node][Type][Model][What it does],
  ..node-info.map(((n, d)) => (raw(n), kind-of(n), model-of(n), text(size: 9.5pt, d))).flatten(),
)

=== How it works

*Shared state.* All nodes read and write one `GraphState`, a `TypedDict` with the documents, candidates, requirements, glossary, blacklist, issues and round number. Parallel calls append to their lists through a reducer. A node that wants to overwrite a list wraps it in `Replace`. Every requirement is a Pydantic model, and the code validates it again after each change. The check also confirms that its sources are real document IDs.

*Fan-outs.* LangGraph `Send` starts `extract`, `resolve_issue` and both `document_pass` modes, one call per document or per issue group. LangGraph waits for all of them before the next node, so the next deterministic node sees all results at once. At most 8 API calls run at the same time.

*The review loop.* `review` runs on `gpt-6-luna`. It sees the whole list with glossary and blacklist and returns issues of seven types: `duplicate`, `conflict`, `wording`, `nonsense`, `priority`, `too_broad` and `too_narrow`. With the route `targeted` the issues go to `group_issues`. That node joins issues that share a requirement into one group, so two issues about the same requirement never produce two rewrites of it. Each group gets one `resolve_issue` call. `apply_resolutions` then deletes every involved requirement and inserts the replacements. This delete-and-insert step is the only way the loop changes the list. Replacements have no priority yet, so the loop goes back through `prioritize` and `assign_ids` before the next review.

*IDs.* `assign_ids` numbers the whole list again on every pass. The loop splits and merges items all the time, and a split item has no obvious old ID to keep, so IDs are plain sequence numbers. The resolver has to refer to other requirements by name, and `apply_resolutions` replaces any leftover `R` number in its text with the requirement's name.

*Origin tags.* Every requirement records where it came from, for example `consolidate`, `unassigned`, `split` or `folded`. In early runs the reviewer split an item in one round and asked to merge the pieces again in the next. Now the reviewer sees items from a split or a fold with the tag `[granularity settled]`, and `group_issues` drops any `too_broad` or `too_narrow` issue on them. The other issue types still apply.

*Round cap.* The loop runs at most 5 rounds. If the reviewer still says `targeted` in round 5, the code forces the route to `accept` and writes the remaining issues to the open issues section of the document.

*Attribution pass.* After the loop, `document_pass[attribution]` reads every document again against the final list and returns the requirements that document supports. The deterministic step then sets the sources of every requirement to exactly those documents. Anything a document states that no requirement covers becomes a `possibly missed` open issue. In the final hybrid run this step added #hyb.attribution.citations_added source citations and removed #hyb.attribution.citations_removed.

*Blacklist.* A blacklist entry holds the full discarded requirement and a one-paragraph reason that names the sources on each side. Entries come from `consolidate`, for nonsensical or conflicting candidates, and from `resolve_issue`, for `conflict` and `nonsense` issues. The document lists them as B01 to Bn after the requirements.

=== The `network` variant

#figure(
  kind: image,
  stack(spacing: 0.5cm, diagram(
    spacing: (14mm, 5.5mm),
    edge-stroke: 0.7pt,
    mark-scale: 80%,
    det((0, 0), "load_corpus", <n-load>),
    llm((0, 1), "extract", <n-extract>, extrude: (0, 2.5)),
    llm((0, 2), "merge_dedup", <n-merge>),
    llm((0, 3), "assign_unassigned", <n-unas>),
    llm((0, 4), "document_pass[coverage]", <n-cov>, extrude: (0, 2.5)),
    det((0, 5), "apply_document_pass[coverage]", <n-acov>),
    llm((0, 6), "prioritize", <n-prio>),
    det((0, 7), "assign_ids", <n-ids>),
    llm((0, 8), "review", <n-review>),
    llm((0, 9.3), "document_pass[attribution]", <n-attr>, extrude: (0, 2.5)),
    det((0, 10.3), "apply_document_pass[attribution]", <n-aattr>),
    det((0, 11.3), "render", <n-render>),
    det((1.4, 8), "group_issues", <n-group>),
    llm((1.4, 7), "resolve_issue", <n-resolve>, extrude: (0, 2.5)),
    det((1.4, 6), "apply_resolutions", <n-apply>),

    edge(<n-load.south>, <n-extract.north>, "-|>", el[Send per document], label-side: left),
    edge(<n-extract.south>, <n-merge.north>, "-|>"),
    edge(<n-merge.south>, <n-unas.north>, "-|>"),
    edge(<n-unas.south>, <n-cov.north>, "-|>", el[Send per document], label-side: left),
    edge(<n-cov.south>, <n-acov.north>, "-|>"),
    edge(<n-acov.south>, <n-prio.north>, "-|>"),
    edge(<n-prio.south>, <n-ids.north>, "-|>"),
    edge(<n-ids.south>, <n-review.north>, "-|>"),
    edge(<n-review.south>, <n-attr.north>, "-|>", el[accept, or round 5], label-side: left),
    edge(<n-attr.south>, <n-aattr.north>, "-|>"),
    edge(<n-aattr.south>, <n-render.north>, "-|>"),

    edge(<n-review.east>, <n-group.west>, "-|>", stroke: 0.9pt + loop-col, lp[targeted]),
    edge(<n-group.north>, <n-resolve.south>, "-|>", stroke: 0.9pt + loop-col, lp[Send per group], label-side: right),
    edge(<n-resolve.north>, <n-apply.south>, "-|>", stroke: 0.9pt + loop-col),
    edge(<n-apply.west>, <n-prio.east>, "-|>", stroke: 0.9pt + loop-col, lp[next round], label-side: right),
    edge(<n-group.south>, (1.4, 9.3), <n-attr.east>, "-|>", el[no groups left], label-side: left),
  ), legend),
  caption: [The `network` graph, selected with `--graph network`. From `prioritize` on it has the same review loop and tail as @fig-hybrid.],
) <fig-network>

The `network` graph was my first design. No call in it sees the whole corpus. `merge_dedup` merges the candidates from their text alone, and a per-document `document_pass[coverage]` then finds what each document supports and what is still missing. The `hybrid` graph replaces those two nodes with one `consolidate` call that gets all 20 documents in full plus every candidate. With the full text it judges duplicates, sources and conflicts better, and it is the only node that writes stakeholder questions. That one call used #thousands(node-row("hybrid", "consolidate").tokens) tokens. For a corpus over about 300k tokens the node stops with an error that says to use `--graph network`.

== Models used

#let model-why = (
  ("extract", [20 parallel calls that have to follow the granularity rules. On `gpt-5-mini` the items were too fine-grained.]),
  ("consolidate", [The hardest judgement, made once, so it gets the strongest model.]),
  ("assign_unassigned", [Maps a few leftover items onto a numbered list.]),
  ("document_pass", [Reads one long document against the whole list, 20 calls per pass.]),
  ("prioritize", [On `gpt-5.4-nano` items that a source calls critical ended up at Low.]),
  ("review", [Judges the whole list at once. The loop is only as good as this call.]),
  ("resolve_issue", [Many small rewrite calls.]),
)
#table(
  columns: (auto, auto, 1fr),
  table.header[Node][Model][Why],
  ..model-why
    .map(((n, w)) => {
      let key = if n == "document_pass" { "document_pass[attribution]" } else { n }
      (raw(n), model-of(key), text(size: 9.5pt, w))
    })
    .flatten(),
)

#let models = ("gpt-6-luna", "gpt-5.6-luna", "gpt-5-mini")
#table(
  columns: (auto, 1fr, 1fr),
  align: (left, right, right),
  table.header[Model][Tokens, hybrid run][Tokens, network run],
  ..models.map(m => (raw(m), thousands(hyb.tokens.at(m)), thousands(net.tokens.at(m)))).flatten(),
  [*Total*], strong(thousands(sum-tokens(hyb.tokens))), strong(thousands(sum-tokens(net.tokens))),
)

The network uses three models, `gpt-6-luna`, `gpt-5.6-luna` and `gpt-5-mini`. At first `prioritize` ran on `gpt-4.1-nano`. In `20261024_162519` that model returned 404 because it was deprecated, so I switched to `gpt-5.4-nano`. In `20261024_172523` I moved `prioritize` to `gpt-6-luna` and `extract` from `gpt-5-mini` to `gpt-5.6-luna`, because those two nodes produced the weakest parts of the output.

== Trace and timing

Every run writes a folder `output/runs/<timestamp>_<graph>/` with these files.
- `trace.jsonl` has one record per node execution, LLM or deterministic, with node name, round, start, end and duration. LLM records also hold every call with the messages sent, the raw response, the parsed output, the token usage and any retry.
- `state/NN_<node>.json` has the full graph state after each LangGraph step.
- `requirements.md` and `requirements.json` are the document of that run.

The two timelines below come straight from the traces of the final runs. Each node has a row and each execution a bar. Parallel calls stack as thin bars in the same row. Their bars include the time a call waits for one of the 8 API slots, so for them the span of the whole row is the useful number.

#let timeline(graph) = {
  let rows = timeline-rows.filter(r => r.graph == graph)
  let lanes = summary.filter(r => r.graph == graph).map(r => r.node)
  let marks = round-marks.filter(r => r.graph == graph)
  let wall = calc.max(hyb.wall_s, net.wall_s)
  let xmax = calc.ceil(wall / 100) * 100
  let label-w = 4.6cm
  let plot-w = 12.3cm
  let top = 0.45cm
  let axis-h = 0.75cm
  let x(t) = plot-w * (t / xmax)
  let subs(n) = rows.find(r => r.node == n).subs
  let lane-h(n) = if subs(n) > 1 { 0.95cm } else { 0.36cm }
  let ys = (top,)
  for n in lanes { ys.push(ys.last() + lane-h(n)) }
  let body-h = ys.last() - top
  set text(size: 7pt)
  box(width: label-w + plot-w, height: ys.last() + axis-h, {
    for (i, n) in lanes.enumerate() {
      let y = ys.at(i)
      if calc.rem(i, 2) == 0 {
        place(dx: label-w, dy: y, rect(width: plot-w, height: lane-h(n), fill: luma(246), stroke: none))
      }
      place(dx: 0pt, dy: y, box(width: label-w - 5pt, height: lane-h(n), align(right + horizon, raw(n))))
      let bh = (lane-h(n) - 2pt) / subs(n)
      for r in rows.filter(r => r.node == n) {
        let w = calc.max(x(r.end_s - r.start_s), 0.8pt)
        place(
          dx: label-w + x(r.start_s),
          dy: y + 1pt + bh * r.sub,
          rect(width: w, height: calc.max(bh * 0.8, 0.6pt), fill: model-col.at(r.model), stroke: none),
        )
      }
    }
    for m in marks {
      place(dx: label-w + x(m.start_s), dy: top - 0.1cm, line(
        angle: 90deg,
        length: body-h + 0.1cm,
        stroke: (paint: luma(110), thickness: 0.5pt, dash: "dashed"),
      ))
      place(dx: label-w + x(m.start_s) + 1.5pt, dy: 0pt, text(fill: luma(60), m.label))
    }
    place(dx: label-w, dy: ys.last(), line(length: plot-w, stroke: 0.5pt))
    for t in range(0, xmax + 1, step: 100) {
      place(dx: label-w + x(t), dy: ys.last(), line(angle: 90deg, length: 3pt, stroke: 0.5pt))
      place(dx: label-w + x(t) - 0.5cm, dy: ys.last() + 4pt, box(width: 1cm, align(center, str(t))))
    }
    place(dx: label-w + plot-w / 2 - 2cm, dy: ys.last() + 0.4cm, box(width: 4cm, align(center)[seconds since run start]))
  })
}
#let model-legend = align(center, text(size: 8.5pt)[
  #for m in models [#box(width: 1.1em, height: 0.7em, fill: model-col.at(m)) #raw(m) #h(1.2em)]
  #box(width: 1.1em, height: 0.7em, fill: model-col.at("")) deterministic
  #h(1.2em) #box(width: 1.4em, height: 0.7em, align(horizon, line(length: 100%, stroke: (paint: luma(110), thickness: 0.5pt, dash: "dashed")))) start of review round or attribution pass
])

#figure(
  kind: image,
  stack(spacing: 0.35cm, timeline("hybrid"), model-legend),
  caption: [Timeline of the final `hybrid` run, #secs(hyb.wall_s) wall time. The lines r1 to r5 mark the start of each review round at `prioritize`, and attr. marks the start of the attribution pass.],
) <fig-tl-hybrid>

#figure(
  kind: image,
  timeline("network"),
  caption: [Timeline of the final `network` run, #secs(net.wall_s) wall time, with the same time axis and colours as @fig-tl-hybrid.],
)

#let all-nodes = summary.map(r => r.node).dedup()
#let cell(graph, n, f) = {
  let r = node-row(graph, n)
  if r == none [] else { f(r) }
}
#table(
  columns: (auto, auto, auto, auto, auto, auto, auto, auto, auto),
  align: (left,) + (right,) * 8,
  stroke: (x, y) => if y == 0 { none } else if y == 1 { (bottom: 0.7pt) } else { (bottom: 0.3pt + luma(200)) },
  inset: (x: 4.5pt, y: 3.5pt),
  table.header(
    [],
    table.cell(colspan: 4, align: center, stroke: (bottom: 0.3pt))[hybrid],
    table.cell(colspan: 4, align: center, stroke: (bottom: 0.3pt))[network],
    ..([Node], [Calls], [Time], [Share], [Tokens], [Calls], [Time], [Share], [Tokens]).map(strong),
  ),
  ..all-nodes
    .map(n => (
      text(size: 8pt, raw(n)),
      ..("hybrid", "network")
        .map(g => (
          cell(g, n, r => str(r.invocations)),
          cell(g, n, r => if r.busy_s < 0.1 [< 0.1 s] else { secs(r.busy_s) }),
          cell(g, n, r => pct(r.share)),
          cell(g, n, r => if r.tokens == 0 [–] else { ktok(r.tokens) }),
        ))
        .flatten(),
    ))
    .flatten(),
)
#text(size: 0.85em)[_Calls_ counts node executions. _Time_ is the wall time during which at least one call of the node was running. _Share_ is that time over the wall time of the run.]

#let rv = node-row("hybrid", "review")
#let at = node-row("hybrid", "document_pass[attribution]")
#let det-ms = {
  let det-rows = timeline-rows.filter(r => r.kind == "det" and r.graph == "hybrid")
  det-rows.map(r => (r.end_s - r.start_s) * 1000).sum()
}
- `review` is the slow part. Its #rv.invocations calls take #pct(rv.share) of the hybrid run, about #secs(rv.busy_s / rv.invocations) each. The loop is sequential, so five rounds mean five of these waits.
- The fan-outs take little time. 20 `extract` calls finish in #secs(node-row("hybrid", "extract").busy_s). The attribution pass uses the most tokens, #ktok(at.tokens), because each of its 20 calls gets the whole requirement list.
- All deterministic nodes of the hybrid run take #calc.round(det-ms) ms together.

== Spec coverage

#let g-final = grades.find(x => x.run == "20261024_202345_hybrid")
#let hyb-nodes(kind) = summary.filter(r => r.graph == "hybrid" and r.kind == kind)
#show table: set block(breakable: true)
#table(
  columns: (auto, 1.25fr, 1.2fr),
  table.header[Spec][What addresses it][Result in the hybrid document],
  [ANS1], [LLM nodes #hyb-nodes("llm").map(r => raw(r.node)).join(", ").], [#hyb-nodes("llm").len() LLM nodes in the hybrid graph.],
  [ANS2], [Deterministic nodes #hyb-nodes("det").map(r => raw(r.node)).join(", ").], [#hyb-nodes("det").len() deterministic nodes.],
  [ANS3], [The review loop runs `review`, `group_issues`, `resolve_issue`, `apply_resolutions`, `prioritize`, `assign_ids` and then `review` again. Every structured call is also retried once with its validation error.], [Used in every run. The final run used all #hyb.rounds rounds, and the loop rarely ends on its own.],
  [ANS4], [`gpt-6-luna`, `gpt-5.6-luna` and `gpt-5-mini`.], [Met.],
  [ANS5], [LangGraph `StateGraph` with `Send` fan-outs and conditional edges.], [Met.],
  [OS1], [`render` writes one `requirements.md` and the same content as JSON.], [One document with scale, glossary, requirements, blacklist, open issues and a coverage table.],
  [OS2], [`assign_ids` numbers R001 to Rn, and the blacklist uses B01 to Bn.], [Unique within the document. The numbers change between runs, and the document says so.],
  [OS3], [`consolidate`, the mapping in `assign_unassigned`, the review issue type `duplicate` and the resolver merge.], [Partly met. Opus 5.5 still counted about #g-final.merge_items items that need merging, and 2 duplicate pairs are open issues.],
  [OS4], [Source document IDs on every requirement, set again per document by the attribution pass, and a per-document coverage table.], [#g-final.wrong_sources of 25 sampled requirements had a wrong source.],
  [OS5], [A prompt rule asks for a name of 3 to 8 words and a one-paragraph description. The schema rejects empty text.], [Every requirement has both. Some descriptions are a single sentence.],
  [OS6], [`prioritize` with the scale from `config.py`, which the document prints at the top. Explicit priority markers in the sources force High.], [#hyb.high High, #hyb.medium Medium and #hyb.low Low, each with a reason.],
  [OS7], [The glossary from `consolidate`, the review issue types `wording` and `conflict`, and conflicts moved to the blacklist.], [Wording is mostly consistent. The text uses "library system", which the glossary lacks, and 2 blacklisted items also appear as possibly missed.],
  [OS8], [Per-document `extract`, the candidate checklist in `consolidate`, `assign_unassigned` and the `possibly missed` issues of the attribution pass.], [#g-final.missing12 of the 12 items Opus 5.5 checked are missing. About 4 of the #hyb.possibly_missed `possibly missed` items are real. Scheduled purge and deletion reasons are missing, and no `possibly missed` issue flags them.],
  [OS9], [A blacklist section with the full item and a reason.], [#hyb.blacklist entries. B01 on batch efficiency and B06 on rapid distribution are questionable, and B04 and B05 are the same item.],
)

#show table: set block(breakable: false)
== How the design evolved

I ran the full graph 20 times while building it. The table lists every run from `run_history.csv`. "Own" means the reviewer accepted before the round cap. The grades come from Opus 5.5, as described under results, and "–" marks a run it did not grade.

#let change = (
  "20261022_233515": [`restructure` node],
  "20261023_105641": [connection error],
  "20261023_110956": [connection error],
  "20261023_111902": [granularity explosion],
  "20261023_114626": [`group_issues`],
  "20261023_121042": [`assign_unassigned`],
  "20261023_122842": [prompt fixes],
  "20261024_162519": [nano model 404],
  "20261024_163032": [`gpt-5.4-nano`],
  "20261024_165734": [granularity guard],
  "20261024_172523": [model swap],
  "20261024_174514": [`verify_sources`],
  "20261024_183024": [`document_pass`],
  "20261024_184705_hybrid": [first hybrid],
  "20261024_191559_hybrid": [pointer ban],
  "20261024_194017_hybrid": [priority notes],
  "20261024_195350_hybrid": [prompt tidy-up],
  "20261024_200309_network": [network re-run],
  "20261024_202345_hybrid": [*final hybrid*],
  "20261024_203609_network": [final network],
)
#let hist-cell(v) = if v == "" [–] else [#v]
#{
  set text(size: 8.5pt)
  show raw: set text(size: 7pt)
  table(
    columns: (auto, auto, 1fr, auto, auto, auto, auto, auto, auto, auto, auto),
    align: (left, left, left, right, right, right, right, center, right, right, center),
    inset: (x: 3.5pt, y: 3pt),
    table.header[Run][Graph][Change][Reqs][Blacklist][Open][Rounds][Own][Time][Tokens][Grade],
    ..dev-runs
      .map(r => {
        let failed = r.completed == "False"
        (
          rn(r.run, size: 7pt),
          r.graph,
          change.at(r.run),
          if failed [failed] else { r.requirements },
          hist-cell(r.blacklisted),
          hist-cell(r.open_issues),
          hist-cell(r.review_rounds),
          if failed [] else if r.accepted_before_cap == "True" [yes] else [no],
          secs(r.wall_time_s),
          ktok(row-tokens(r)),
          gstr(grade-of(r.run)),
        )
      })
      .flatten(),
    [baseline], [single call], [one LLM call], base-row.requirements, base-row.blacklisted, base-row.open_issues, [–], [–], secs(base-row.wall_time_s), ktok(row-tokens(base-row)), gstr(base-grade),
  )
}

The changes that mattered:

- *`20261022_233515`.* The first design had a `restructure` route, where the reviewer could ask for the whole list to be rewritten in one call. That call returned a shorter list and dropped items without saying so. The run ended with #hist("20261022_233515").requirements requirements. I removed the route. Since then every change goes through delete-and-insert on named requirements, and the trace shows each removed item.
- *`20261023_111902`.* This run ended with #hist("20261023_111902").requirements requirements. The reviewer kept calling items `too_broad`, and the resolver split them into smaller and smaller pieces. Some issues also overlapped, so two resolver calls rewrote the same requirement and duplicated its content. I added `group_issues` for that, and one shared definition of a requirement, sized to one acceptance test, that every prompt includes.
- *`20261023_121042`.* At first the candidates that `merge_dedup` did not use were appended to the list, which created duplicates. `assign_unassigned` now maps each one onto an existing requirement when one covers it. The same run added origin tags.
- *Trace investigation on `20261023_122842`.* I read the trace and the state snapshots round by round. Most granularity issues after round 1 were about items that an earlier resolution had just produced, so the loop was undoing its own splits and merges. The fine-grained items themselves came from `extract`, before the loop started. I fixed the extract prompt and added the granularity guard (the `[granularity settled]` tag) in `20261024_165734`.
- *Model swap in `20261024_172523`.* Moving `extract` and `prioritize` to stronger models raised the grade from #grade-of("20261024_165734") to #grade-of("20261024_172523") and removed most priority inversions.
- *Source checking in `20261024_174514` and `20261024_183024`.* A `verify_sources` node on `gpt-5-mini` used #ktok(int(hist("20261024_174514").at("tokens_total_gpt-5-mini"))) tokens. It could only remove citations, and it flagged correct ones. I replaced it with `document_pass`, which reads each document and can also add sources.
- *Baseline.* I asked `gpt-5.6-luna` once for the whole document. It took #secs(base.wall_s) and #ktok(sum-tokens(base.tokens)) tokens and got grade #base-grade, with the best stakeholder questions of all runs. It had only #base.requirements requirements, #base.high of them High, and it missed #grades.find(x => x.run == "baseline").missing12 of the 12 checked items. The baseline showed me that the network lacked a step that sees the whole corpus at once.
- *Hybrid, from `20261024_184705_hybrid` on.* I put one whole-corpus `consolidate` call in place of `merge_dedup` and the coverage pass, and kept per-document extraction as a checklist. Then I banned pointer requirements such as "the reports listed in Appendix A", added source priority notes for explicit markers, and tidied the prompts. The tidy-up in `20261024_195350_hybrid` lost three checked items, and I fixed that before the final run.

== Results

#let out-cols = (("hybrid", hyb), ("network", net), ("baseline", base))
#table(
  columns: (auto, 1fr, 1fr, 1fr),
  align: (left, right, right, right),
  table.header[][hybrid][network][baseline],
  [Requirements], ..out-cols.map(((_, o)) => str(o.requirements)),
  [High / Medium / Low], ..out-cols.map(((_, o)) => [#o.high / #o.medium / #o.low]),
  [Blacklist], ..out-cols.map(((_, o)) => str(o.blacklist)),
  [Stakeholder questions], ..out-cols.map(((_, o)) => str(o.questions)),
  [Open review issues], ..out-cols.map(((_, o)) => str(o.review_issues)),
  [Possibly missed], ..out-cols.map(((_, o)) => str(o.possibly_missed)),
  [Review rounds], ..out-cols.map(((_, o)) => if o.rounds == 0 [–] else [#o.rounds of #o.max_rounds]),
  [Wall time], ..out-cols.map(((_, o)) => secs(o.wall_s)),
  [Tokens], ..out-cols.map(((_, o)) => thousands(sum-tokens(o.tokens))),
)

The `network` document has no stakeholder questions because only `consolidate` writes them. Its blacklist ended empty.

#let g-net = grades.find(x => x.run == "20261024_203609_network")
*Hybrid against the final network.* Opus 5.5 rated the final network run #g-net.grade/10, half a point below the hybrid. Neither document misses any of the 12 checked items, the network has #g-net.wrong_sources wrong sources and the hybrid #g-final.wrong_sources, and the network has the most balanced priorities of any run. Of its 25 sampled requirements #g-net.accurate were accurate and #g-net.partial_accurate partly accurate, against #g-final.accurate accurate in the hybrid. Several scope bullets from D17 survive as requirements, three of them at High, and an untestable "tested and proven" item stays High because no step moved it to the blacklist. One report is split in two, retention is split five ways, and the conflict about checkout at a transfer destination is decided the wrong way without being flagged. According to Opus 5.5 the gap comes from the whole-corpus `consolidate` call: it writes most of the blacklist and all stakeholder questions, and it sees both sides of a conflict.

#let g-base = grades.find(x => x.run == "baseline")
*Hybrid against the baseline.* The single `gpt-5.6-luna` call produced #base.requirements requirements, and the hybrid graph produced #hyb.requirements. The baseline missed #g-base.missing12 of the 12 checked items and only partly covered #g-base.partial12 more, while the hybrid document has all 12. Of 25 sampled requirements the baseline had #g-base.wrong_sources with a wrong source and the hybrid #g-final.wrong_sources. The baseline does better on duplicates, about #g-base.merge_items items needing merge against about #g-final.merge_items, and it is much cheaper: #secs(base.wall_s) and #ktok(sum-tokens(base.tokens)) tokens against #secs(hyb.wall_s) and #ktok(sum-tokens(hyb.tokens)). Opus 5.5 rated the baseline #base-grade/10 and the hybrid #final-grade/10. Most of that difference comes from completeness.

*Grading.* To judge the documents I had Claude Opus 5.5 act as a requirements engineer. For each run it sampled 25 requirements across High, Medium and Low and checked each against the source documents. It also checked 12 items that some development runs had missed, counted items that need merging, and gave a grade out of 10. One model and 25 items per run make these numbers rough.

#table(
  columns: (auto, auto, auto, auto, auto, auto),
  align: (left, right, right, right, right, right),
  table.header[Run][Grade][Accurate][Wrong sources][Missing of 12][Needing merge],
  ..grades
    .map(g => (
      if g.run == "baseline" [baseline] else { rn(g.run, size: 7.5pt) },
      gstr(g.grade),
      if g.at("partial_accurate", default: 0) > 0 [#g.accurate, #g.partial_accurate partly] else [#g.accurate],
      str(g.wrong_sources),
      if g.partial12 > 0 [#g.missing12, #g.partial12 partly] else [#g.missing12],
      [\~#g.merge_items],
    ))
    .flatten(),
)
#text(size: 0.85em)[Accurate and wrong sources count out of the 25 sampled requirements, and "partly" under Accurate counts requirements that are only partly right. Missing of 12 counts checked items that are absent, and "partly" those only partly covered. Needing merge is the Opus 5.5 estimate of near-duplicate items in the whole document.]

Two requirements from the hybrid document:

#for r in hyb.examples [
  #block(inset: (left: 1em), breakable: false)[
    *#r.id #r.name*, #r.priority, sources #r.source_doc_ids.join(", ") \
    #text(size: 9.5pt)[#r.description] \
    #text(size: 9pt, style: "italic")[#r.priority_justification]
  ]
]

Two of its stakeholder questions:
#for q in hyb.question_list.slice(2, 4) [
  - #q.question (#q.doc_ids.join(", "))
]

*Limitations.*
- The grades come from Opus 5.5 reading 25 items per run. They only show a direction.
- Close versions of the code give different results. `20261024_195350_hybrid` lost three checked items that the hybrid runs before and after it kept.
- About #g-final.merge_items near-duplicates remain in the hybrid document.
- The loop almost always hits the round cap. Only `20261024_194017_hybrid` ended with the reviewer accepting on its own.
- The attribution pass costs #ktok(at.tokens) tokens, about #pct(at.tokens / sum-tokens(hyb.tokens)) of the hybrid run, and runs without it already had most sampled sources right.

== Conclusion

Per-document extraction as a checklist plus one whole-corpus consolidation call gave the best documents. Changing the list only through grouped delete-and-insert kept items from disappearing. The granularity guard, built on the origin tags, stopped the split and merge flip-flopping, and the full trace is how I found where the fine-grained items came from.

Three things failed. One call that rewrote the whole list lost items. Checking sources with a small model removed correct citations. The review loop converged only once in 20 runs, because the reviewer almost always finds something, so five rounds mostly polish and sometimes undo.

Next I would stop the loop when a round changes few requirements, add a deterministic near-duplicate check with embeddings before `review`, and run each configuration several times to measure the variance before trusting a difference.

== AI assistance

The network code and this report were co-written with Claude Fable 5.1 and Claude Opus 5.5.
