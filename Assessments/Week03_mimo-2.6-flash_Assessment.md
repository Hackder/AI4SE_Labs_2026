# Assessment by mimo-2.6-flash

# Week 03 Prompting
- Awarded: 5b out of 5b
- Commentary: A complete, well-instrumented submission: three permissible frameworks, one fresh agent session per prompt with full attempt archives, an implemented new metric, and a genuine significance analysis. Reported numbers cross-check against the stored data (final accuracy 141/141/147 of 155, session times, p-values). Note that report.pdf could not be opened by this grader (no PDF input support), so all figures were judged from the report.typ source, which defines the tables and charts explicitly, together with the result JSON/CSV files.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: Chose RTF, ICIO and CO-STAR (none forbidden; found via frompting.com, cited with a link) and wrote three prompt.txt files that faithfully follow each framework's parts (Role/Task/Format; Instruction/Context/Input/Output; Context/Objective/Style/Tone/Audience/Response) and were actually reused in Task 2. The report table explains why each was chosen and what was expected, plus the shared few-shot example file. Explanations are terse (one clause per framework) but all required outputs are present and correct.

## Task 2
- Awarded: 1b   (max 1b)
- Commentary: All 155 questions solved under each of the three prompts with predictions stored per prompt alongside prompt-identifying metadata (model gpt-5.6-luna, reasoning effort, prompt SHA-256, wall-clock time, token usage in run/metadata.json) plus every archived attempt and session log. The hint was followed: run_inference.py launches a new ephemeral codex session per prompt. Comparison report contains a results table, accuracy bar chart (first vs final), session-time bar chart and token table; inference/session times measured precisely (117.2 s / 212.3 s / 121.4 s). Minor cosmetic issue: prompt.txt paths refer to the original predictions/, src/, results/ layout, while the packaged files live under agents/<name>/.

## Task 3
- Awarded: 1b   (max 1b)
- Commentary: Proposed a row-level result F1 with a "balanced" variant that averages F1 over empty-answer and non-empty questions separately, removing the free correct answers exact match grants for empty results. Defended with standard IR references, argued as complementing (not replacing) exact accuracy, correctly implemented in analysis/src/metrics.py (Counter multiset TP/FP/FN, SQL error = 0, both-empty = 1), computed for every attempt and final prediction (per-question CSVs, summary.json), and reported with a table and chart comparing the prompts. The underlying F1 idea is standard, but invention is only appreciated, not required.

## Task 4
- Awarded: 2b   (max 2b)
- Commentary: The Task 4 report section delivers everything asked: progress-over-checker-attempt curves, a failed-question heat-map grid, and a significance table combining exact McNemar tests for accuracy with a paired permutation test for balanced F1 and Holm correction across the three pairwise comparisons (implementation verified as correct exact binomial tails and Holm step-down). Interpretation is accurate against statistics.json — no significant final accuracy differences, CO-STAR significantly better on balanced F1, all first-attempt differences significant — and explains outcomes through all three required factors (prompt length/explicitness, the shared model's single-parser behaviour and checker-fitted repairs, and each agent's generated script choices, e.g. RTF's five hardcoded restaurant names vs ICIO's DB-derived lists, both confirmed in the scripts). Honest limits (one run per framework, run-to-run variance unknown, results not attributable to wording alone) are stated.