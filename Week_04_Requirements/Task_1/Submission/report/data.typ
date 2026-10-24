// Data processing for report.typ. Reads the run outputs directly at compile time.

#let runs = (
  hybrid: "../output/runs/20261024_202345_hybrid",
  network: "../output/runs/20261024_203609_network",
)

#let lanes = (
  hybrid: (
    "load_corpus",
    "extract",
    "consolidate",
    "assign_unassigned",
    "prioritize",
    "assign_ids",
    "review",
    "group_issues",
    "resolve_issue",
    "apply_resolutions",
    "document_pass[attribution]",
    "apply_document_pass[attribution]",
    "render",
  ),
  network: (
    "load_corpus",
    "extract",
    "merge_dedup",
    "assign_unassigned",
    "document_pass[coverage]",
    "apply_document_pass[coverage]",
    "prioritize",
    "assign_ids",
    "review",
    "group_issues",
    "resolve_issue",
    "apply_resolutions",
    "document_pass[attribution]",
    "apply_document_pass[attribution]",
    "render",
  ),
)

#let llm-nodes = (
  "extract",
  "merge_dedup",
  "consolidate",
  "assign_unassigned",
  "document_pass[coverage]",
  "document_pass[attribution]",
  "prioritize",
  "review",
  "resolve_issue",
)

// One parsed record per line of trace.jsonl.
#let read-jsonl(path) = {
  read(path).split("\n").filter(l => l.trim() != "").map(l => json(bytes(l)))
}

// Seconds since midnight of an ISO time stamp such as 2026-10-24T20:23:45.045+02:00.
// All runs start and end on the same day, so this is enough for differences.
#let clock(stamp) = {
  let t = stamp.slice(11, 23).split(":")
  int(t.at(0)) * 3600 + int(t.at(1)) * 60 + float(t.at(2))
}

#let calls(rec) = rec.payload.at("llm_calls", default: none)
#let calls-of(rec) = if calls(rec) == none { () } else { calls(rec) }
#let tokens-of(rec) = calls-of(rec).map(c => c.at("usage", default: (:)).at("total", default: 0)).sum(default: 0)

// Length of the union of (start, end) intervals.
#let busy(spans) = {
  let total = 0.0
  let end = -1e9
  for (s, e) in spans.sorted(key: x => x.at(0)) {
    if s > end {
      total += e - s
      end = e
    } else if e > end {
      total += e - end
      end = e
    }
  }
  total
}

// Greedy sub-lane per interval so that bars in one sub-lane never overlap.
#let pack(spans) = {
  let order = range(spans.len()).sorted(key: i => spans.at(i).at(0))
  let ends = ()
  let slot = (0,) * spans.len()
  for i in order {
    let (s, e) = spans.at(i)
    let k = ends.position(last => last <= s)
    if k == none {
      ends.push(e)
      slot.at(i) = ends.len() - 1
    } else {
      ends.at(k) = e
      slot.at(i) = k
    }
  }
  slot
}

#let run-data(graph) = {
  let recs = read-jsonl(runs.at(graph) + "/trace.jsonl").filter(r => r.round != -1)
  let t0 = calc.min(..recs.map(r => clock(r.started_at)))
  let spans = recs.map(r => (clock(r.started_at) - t0, clock(r.ended_at) - t0))
  let wall = calc.max(..spans.map(s => s.at(1)))
  let timeline = ()
  let summary = ()
  for node in lanes.at(graph) {
    let idx = range(recs.len()).filter(i => recs.at(i).node == node)
    let node-spans = idx.map(i => spans.at(i))
    let slots = pack(node-spans)
    let subs = calc.max(..slots, 0) + 1
    let models = idx.map(i => calls-of(recs.at(i)).map(c => c.model)).flatten().dedup().sorted()
    let kind = if node in llm-nodes { "llm" } else { "det" }
    for (j, i) in idx.enumerate() {
      let r = recs.at(i)
      let cs = calls-of(r)
      timeline.push((
        graph: graph,
        node: node,
        sub: slots.at(j),
        subs: subs,
        round: r.round,
        start_s: spans.at(i).at(0),
        end_s: spans.at(i).at(1),
        kind: kind,
        model: if cs.len() > 0 { cs.first().model } else { "" },
        tokens: tokens-of(r),
      ))
    }
    let b = busy(node-spans)
    summary.push((
      graph: graph,
      node: node,
      kind: kind,
      model: models.join("/", default: ""),
      invocations: idx.len(),
      llm_calls: idx.map(i => calls-of(recs.at(i)).len()).sum(default: 0),
      busy_s: b,
      share: b / wall,
      tokens: idx.map(i => tokens-of(recs.at(i))).sum(default: 0),
    ))
  }
  let prio = range(recs.len()).filter(i => recs.at(i).node == "prioritize").map(i => spans.at(i).at(0)).sorted()
  let marks = prio.enumerate().map(((k, s)) => (graph: graph, label: "r" + str(k + 1), start_s: s))
  let attr = range(recs.len())
    .filter(i => recs.at(i).node == "document_pass[attribution]")
    .map(i => spans.at(i).at(0))
  marks.push((graph: graph, label: "attr.", start_s: calc.min(..attr)))
  let by-model = (:)
  for r in recs {
    for c in calls-of(r) {
      let n = c.at("usage", default: (:)).at("total", default: 0)
      by-model.insert(c.model, by-model.at(c.model, default: 0) + n)
    }
  }
  let extracted = recs.filter(r => r.node == "extract").map(r => r.payload.outputs.len()).sum(default: 0)
  let au = recs.find(r => r.node == "assign_unassigned")
  let unassigned = (
    extracted: extracted,
    leftover: au.payload.candidates,
    mapped: au.payload.mapped,
    new: au.payload.new,
    seconds: au.duration_ms / 1000,
  )
  (
    recs: recs,
    timeline: timeline,
    summary: summary,
    marks: marks,
    wall: wall,
    by-model: by-model,
    unassigned: unassigned,
  )
}

#let example-ids = ("R001", "R043")

#let graph-output(graph, rd) = {
  let doc = json("../output/" + graph + "/requirements.json")
  let reqs = doc.requirements
  let issues = doc.open_issues
  (
    requirements: reqs.len(),
    high: reqs.filter(r => r.priority == "High").len(),
    medium: reqs.filter(r => r.priority == "Medium").len(),
    low: reqs.filter(r => r.priority == "Low").len(),
    blacklist: doc.blacklist.len(),
    questions: doc.open_questions.len(),
    review_issues: issues.filter(i => i.type != "possibly_missed").len(),
    possibly_missed: issues.filter(i => i.type == "possibly_missed").len(),
    rounds: doc.metadata.review_rounds,
    max_rounds: doc.metadata.max_rounds,
    wall_s: rd.wall,
    tokens: rd.by-model,
    glossary: doc.glossary.len(),
    attribution: doc.metadata.at("source_attribution", default: (:)),
    examples: reqs.filter(r => r.id in example-ids),
    question_list: doc.open_questions,
  )
}

// Text of one "## title" section of a markdown document.
#let md-section(text, title) = {
  let parts = text.split("\n## ")
  let hit = parts.find(p => p.starts-with(title + "\n"))
  if hit == none { "" } else { hit }
}
#let count-req(text) = text.matches(regex("(?m)^### R\d+")).len()

#let baseline-output() = {
  let run = json("../output/baseline/run.json")
  let md = read("../output/baseline/requirements.md")
  (
    requirements: count-req(md),
    high: count-req(md-section(md, "Requirements: High priority")),
    medium: count-req(md-section(md, "Requirements: Medium priority")),
    low: count-req(md-section(md, "Requirements: Low priority")),
    blacklist: md.matches(regex("(?m)^### B\d+")).len(),
    questions: md-section(md, "Open issues").matches(regex("(?m)^- ")).len(),
    review_issues: 0,
    possibly_missed: 0,
    rounds: 0,
    max_rounds: 0,
    wall_s: run.wall_time_s,
    tokens: ((run.model): run.usage.total),
  )
}

#let hyb-run = run-data("hybrid")
#let net-run = run-data("network")
#let outputs = (
  hybrid: graph-output("hybrid", hyb-run),
  network: graph-output("network", net-run),
  baseline: baseline-output(),
)
#let unassigned = (hybrid: hyb-run.unassigned, network: net-run.unassigned)
#let summary = hyb-run.summary + net-run.summary
#let timeline-rows = hyb-run.timeline + net-run.timeline
#let round-marks = hyb-run.marks + net-run.marks
#let history = csv("run_history.csv", row-type: dictionary)
#let grades = json("reviewer_grades.json")
