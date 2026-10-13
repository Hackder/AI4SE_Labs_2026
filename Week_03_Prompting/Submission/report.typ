// Co-written by Claude Opus 5.5 and GPT-6.1 Sol
#import "@preview/lilaq:0.6.0" as lq

// ---------- Data (everything numeric comes from these files) ----------
#let summary = json("analysis/results/summary.json")
#let stats = json("analysis/results/statistics.json")
#let per-q = csv("analysis/results/rtf.per_question.csv", row-type: dictionary)

#let prompts = ("rtf", "icio", "co_star")
#let names = (rtf: "RTF", icio: "ICIO", co_star: "CO-STAR")
#let colors = (rtf: rgb("#0072B2"), icio: rgb("#E69F00"), co_star: rgb("#009E73"))

#let total = per-q.len()
#let n-empty = per-q.filter(r => int(r.expected_count) == 0).len()
#let n-nonempty = total - n-empty

#let attempts(p) = summary.filter(r => r.prompt == p and type(r.attempt) == int).sorted(key: r => r.attempt)
#let first(p) = attempts(p).first()
#let final(p) = summary.find(r => r.prompt == p and r.attempt == "final")

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
#let acc(r) = [#r.correct/#total (#pct(r.accuracy))]
#let f3(x) = str(calc.round(x, digits: 3))
#let fp(p) = if p < 0.001 { "< 0.001" } else if p < 0.01 { str(calc.round(p, digits: 3)) } else {
  str(calc.round(p, digits: 2))
}
#let sig(p) = if p < 0.05 [*yes*] else [no]
#let argmax(f) = prompts.sorted(key: f).last()
#let argmin(f) = prompts.sorted(key: f).first()

// ---------- Page style ----------
#set document(title: "Week 03 – Prompting frameworks for text-to-SQL", author: "Juraj Petras")
#set page(paper: "a4", margin: (x: 2cm, y: 1.8cm), numbering: "1")
#set text(font: "New Computer Modern", size: 10.5pt)
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

// shared chart setup
#let chart-w = 7.2cm
#let chart-h = 4.6cm
#let xs = range(prompts.len())
#let prompt-ticks = (ticks: xs.zip(prompts.map(p => names.at(p))), subticks: none)

= Week 03 – Prompting frameworks for text-to-SQL

Model: #raw(final("rtf").model), #final("rtf").reasoning reasoning, run as a coding agent (one fresh CLI session per prompt).

== Task 1 – Frameworks and prompts

Prompts: `agents/<name>/prompt.txt`.

#table(
  columns: (auto, 1.25fr, 1.6fr, 1.3fr),
  table.header[Framework][Parts][Why chosen][Expectation],
  [RTF], [Role, Task, Format], [Shortest structure - the task is simple.], [Should cause the agent less confusion],

  [ICIO],
  [Instruction, Context, Input, Output],
  [Separates inputs from output. Fits this as a data processing task],
  [Fewer mistakes about what to read and write.],

  [CO-STAR],
  [Context, Objective, Style, Tone, Audience, Response],
  [Tells the model the HOW and for WHO we are doing this],
  [More structured output.],
)

All the prompts include a reference to two hand written examples in `inputs/examples.md`.
I found all of these frameworks on #link("https://frompting.com/frameworks").

I decided to lean into the agentic capabilities of the harness I used (#link("https://openai.com/codex/", "codex"))
and encouraged the agents to test their queries and fix the ones that are wrong.

I also told the agent to stop and report when progress becomes impossible,
which later turned out to be useful due to question no.65

== Task 2 – Results

#table(
  columns: (auto, auto, auto, auto, auto),
  table.header[Prompt][Predictions][Prompt file][Model][Reasoning],
  ..prompts
    .map(p => (
      names.at(p),
      raw("agents/" + p + "/predictions.csv"),
      raw("agents/" + p + "/prompt.txt"),
      raw(final(p).model),
      final(p).reasoning,
    ))
    .flatten(),
)

Full session record (model, timing, tokens, every agent event): `agents/<name>/run/` (`metadata.json`, `events.jsonl`). All checked attempts: `agents/<name>/attempts/`.

#table(
  columns: (auto, 1fr, 1fr, auto, auto),
  align: (left, right, right, right, right),
  table.header[Prompt][First attempt][Final][Checker calls][Session time],
  ..prompts
    .map(p => (
      names.at(p),
      acc(first(p)),
      if p == argmax(q => final(q).correct) { strong(acc(final(p))) } else { acc(final(p)) },
      str(attempts(p).len()),
      str(calc.round(final(p).wall_seconds)) + " s",
    ))
    .flatten(),
)

#grid(
  columns: (1fr, 1fr),
  gutter: 0.6cm,
  figure(
    lq.diagram(
      width: chart-w,
      height: chart-h,
      ylim: (0, 100),
      ylabel: [Accuracy (%)],
      xaxis: prompt-ticks,
      lq.bar(xs, prompts.map(p => first(p).accuracy * 100), offset: -0.2, width: 0.4, fill: prompts.map(p => colors
        .at(p)
        .lighten(55%))),
      lq.bar(xs, prompts.map(p => final(p).accuracy * 100), offset: 0.2, width: 0.4, fill: prompts.map(p => colors.at(
        p,
      ))),
    ),
    caption: [Accuracy: first attempt (light) vs final (solid).],
  ),
  figure(
    lq.diagram(
      width: chart-w,
      height: chart-h,
      ylim: (0, auto),
      ylabel: [Session time (s)],
      xaxis: prompt-ticks,
      lq.bar(xs, prompts.map(p => final(p).wall_seconds), width: 0.5, fill: prompts.map(p => colors.at(p))),
    ),
    caption: [Whole agent session time per prompt.],
  ),
)

#block(breakable: false)[
  Token usage per session (cached ⊂ input, reasoning ⊂ output):

  #table(
    columns: (auto, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right),
    table.header[Prompt][Input tokens][cached][Output tokens][reasoning],
    ..prompts
      .map(p => {
        let t = final(p).tokens
        (
          names.at(p),
          thousands(t.input_tokens),
          thousands(t.cached_input_tokens),
          thousands(t.output_tokens),
          thousands(t.reasoning_output_tokens),
        )
      })
      .flatten(),
  )
]

- #names.at(argmax(p => final(p).correct)) finished best. #names.at(argmax(p => first(p).correct)) started best. #names.at(argmin(p => final(p).wall_seconds)) was fastest.
- Time covers the whole agent session: reading, coding, checking and repairing.
- None reached #total/#total. In part this is because of the trick question no.65 which wasn't a real question. All three noticed it; ICIO named it in its final report.
- Agents wrote a Python script that generates the SQL, then repaired it using
  checker feedback - this was not prompted in, and it seems agents did this on their
  own. It seems they prefer using custom scripts for doing tasks like this.
  The script tries to parse the human written questions and automatically generate sql for it.
  If this was a real application and we actually got similar csv files on the input,
  it might be quite a good idea to have some fast deterministic prepass which might
  knock out most of the questions, and over time it could be improved so that the
  model only needs to handle the edge-cases by itself.

== Task 3 – Added metric: balanced result F1

Exact accuracy marks an answer wrong if even one row is missing or extra. F1 gives partial credit.

Each query returns a list of rows (restaurants). We compare it with the rows of the correct answer and count:
- *TP* (true positives): correct rows the query returned
- *FP* (false positives): wrong rows the query returned
- *FN* (false negatives): correct rows the query missed

$ "F1" = (2 dot "TP") / (2 dot "TP" + "FP" + "FN") $

F1 is 1 for a perfect answer and 0 when no returned row is correct. It is a standard metric in information retrieval and machine learning (C. J. van Rijsbergen, _Information Retrieval_, 1979; #link("https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html")[scikit-learn `f1_score`]).

*Balanced:* #n-empty of the #total questions have an empty correct answer, so a query that returns nothing gets those right for free. We average F1 over those #n-empty questions and over the other #n-nonempty separately, then take the mean of the two.

This metric complements the original exact accuracy. We might prefer a model that has a few big mistakes but most things correct than a model that has a small mistake almost everywhere, so using F1 and the exact metric gives us more information than using either individually.

Code: `analysis/src/metrics.py`. Run: `python3 analysis/src/analyze.py`. Per-question scores: `analysis/results/<name>.per_question.csv`.

#grid(
  columns: (auto, 1fr),
  gutter: 0.8cm,
  align: horizon,
  table(
    columns: 3,
    align: (left, right, right),
    table.header[Prompt][First][Final],
    ..prompts
      .map(p => (
        names.at(p),
        f3(first(p).balanced_f1),
        if p == argmax(q => final(q).balanced_f1) { strong(f3(final(p).balanced_f1)) } else {
          f3(final(p).balanced_f1)
        },
      ))
      .flatten(),
  ),
  figure(
    lq.diagram(
      width: chart-w,
      height: chart-h,
      ylim: (0, 1),
      ylabel: [Balanced F1],
      xaxis: prompt-ticks,
      lq.bar(xs, prompts.map(p => first(p).balanced_f1), offset: -0.2, width: 0.4, fill: prompts.map(p => colors
        .at(p)
        .lighten(55%))),
      lq.bar(xs, prompts.map(p => final(p).balanced_f1), offset: 0.2, width: 0.4, fill: prompts.map(p => colors.at(p))),
    ),
    caption: [Balanced F1: first attempt (light) vs final (solid).],
  ),
)

We can see that the first metric tied RTF and ICIO on accuracy, but
looking at F1 we can see that RTF's wrong answers are closer to correct at the end, though not significantly.

== Task 4 – Analysis

=== Progress over checker attempts

#figure(
  lq.diagram(
    width: 14cm,
    height: 5cm,
    xlabel: [Checker attempt],
    ylabel: [Correct (of #total)],
    ylim: (0, total),
    xaxis: (ticks: range(1, calc.max(..prompts.map(p => attempts(p).len())) + 1).map(i => (i, str(i))), subticks: none),
    legend: (position: bottom + right),
    ..prompts.map(p => lq.plot(
      attempts(p).map(r => r.attempt),
      attempts(p).map(r => r.correct),
      color: colors.at(p),
      label: names.at(p),
      mark-size: 4pt,
    )),
  ),
  caption: [Correct answers after each checker call. Drops show repairs that made things worse.],
)

All prompts improved most in the first few attempts. Some repairs broke questions that had passed before, so scores sometimes dropped.
Interestingly the most successful prompt (CO-STAR) swings in accuracy the most. It may indicate
that the model took more risk which turned out successful in this case.

=== Which questions failed

#let failed = prompts.map(p => (p, final(p).failed_ids)).to-dict()
#let all-failed = prompts.map(p => failed.at(p)).flatten().dedup().sorted()
#let shared = all-failed.filter(id => prompts.all(p => id in failed.at(p)))
#let cell-w = 0.33cm

#figure(
  {
    set text(size: 7pt)
    grid(
      columns: (auto,) + (cell-w,) * all-failed.len(),
      rows: 0.42cm,
      gutter: 1pt,
      align: center + horizon,
      [],
      ..all-failed.map(id => rotate(-90deg, reflow: true, str(id))),
      ..prompts
        .map(p => (
          align(right, text(size: 8pt, names.at(p)) + h(4pt)),
          ..all-failed.map(id => box(
            width: 100%,
            height: 100%,
            fill: if id in failed.at(p) { colors.at(p) } else { luma(238) },
          )),
        ))
        .flatten()
    )
  },
  caption: [Failed questions in the final predictions (filled = failed). Columns are question IDs failed by at least one prompt.],
)

- #all-failed.len() distinct questions failed in at least one final result.
- Failed by all three: #shared.map(str).join(", ").
- ICIO's failures sit in other ID blocks than RTF's and CO-STAR's, so its script had different blind spots.
  It would be an interesting experiment to try and run ICIO and CO-STAR in parallel, and then have one agent merge their solutions
  taking the successful ones from both.

=== Is the difference significant?

Tests: McNemar (exact) for accuracy, paired permutation test for balanced F1, Holm correction for 3 comparisons, α = 0.05. Data: `analysis/results/statistics.json`.

#let sig-rows(key, label) = {
  let s = stats.at(key)
  (table.cell(colspan: 7, fill: luma(245))[_#label _],)
  for m in s.mcnemar {
    let f = s.balanced_f1_permutation.find(r => r.a == m.a and r.b == m.b)
    (
      [#names.at(m.a) vs #names.at(m.b)],
      [#m.a_only / #m.b_only],
      fp(m.p_holm),
      sig(m.p_holm),
      str(calc.round(f.difference, digits: 3)),
      fp(f.p_holm),
      sig(f.p_holm),
    )
  }
}

#table(
  columns: (1fr, auto, auto, auto, auto, auto, auto),
  stroke: (x, y) => if y == 0 { none } else if y == 1 { (bottom: 0.7pt) } else { (bottom: 0.3pt + luma(200)) },
  align: (left, right, right, center, right, right, center),
  table.header(
    [],
    table.cell(colspan: 3, align: center, stroke: (bottom: 0.3pt))[Accuracy (McNemar)],
    table.cell(colspan: 3, align: center, stroke: (bottom: 0.3pt))[Balanced F1 (permutation)],
    ..([A vs B], [Only A / only B], [p], [Sig.], [A − B], [p], [Sig.]).map(strong),
  ),
  ..sig-rows("final", "Final results"),
  ..sig-rows("first", "First attempts"),
)

#text(
  size: 0.85em,
)[_Only A / only B:_ questions only A / only B got right. _A − B:_ difference in balanced F1. _p:_ p-value after Holm correction. _Sig.:_ p < 0.05.]

- Final, accuracy: #if stats.final.mcnemar.all(r => r.p_holm >= 0.05) [no significant difference.] else [some differences are significant.]
- Final, balanced F1: CO-STAR significantly better than both.
- First attempts: #if stats.first.mcnemar.all(r => r.p_holm < 0.05) [all accuracy differences significant] else [not all accuracy differences significant] (#prompts.sorted(key: p => -first(p).correct).map(p => names.at(p)).join(" > ")).

#block(breakable: false)[
  === Why the differences

  *Prompt*
  - CO-STAR is the longest and most explicit.
  - RTF is shortest. Its first script was the weakest (#first("rtf").correct/#total).
]

*Model* (same for all, #final("rtf").reasoning reasoning)
- Wrote one regex-based parser that translates all questions with the same rules.
- Fitted fixes to checker feedback; some repairs made scores worse (CO-STAR #attempts("co_star").slice(-3).map(r => str(r.correct)).join(" → ")).

*Coding agent*
- Results depend mostly on each script's parsing choices:
  - RTF: hardcoded list of 5 restaurant names.
  - ICIO: read the database to build city and name lists, which was good, but it also patched one question (ID 28) by ID.
  - CO-STAR: its parsing handled the most questions, so it scored the most points.
- Every script created by the model is really unreadable. I wouldn't want to be the one left to maintain this.
- ID 65 ("What is the lifes greates illusion?") was a control against hardcoded answers. #if prompts.all(p => 65 in failed.at(p)) [All three failed it, which suggests none hardcoded the expected result rows.] else [Not all prompts failed it.]

=== Limits
- One run per framework, so run-to-run variation is unknown.
- Different scripts and repairs mean differences can't be attributed to prompt wording alone. I wouldn't consider any of these results conclusive at all.

== AI assistance
The analysis scripts and visualizations were co-written with Claude Opus 5.5 and GPT-6.1 Sol.
