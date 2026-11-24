# Assessment by laguna-s-2.1

# Week 03 Prompting
- Awarded: 5b out of 5b
- Commentary: The student solved the text-to-SQL restaurant retrieval task (155 questions) with three distinct prompting frameworks — RTF, ICIO and CO-STAR — each applied in its own fresh coding-agent session. All deliverables are present: framework prompts, per-attempt archived predictions, a custom checker, an analysis pipeline, and a Typst report with tables and charts. A custom "balanced result F1" metric was invented, implemented and compared alongside the original exact-accuracy metric, with McNemar and permutation tests (Holm-corrected). Work is thorough, reproducible and well above the passing threshold. The rendered report.pdf charts could not be viewed, but their definitions in report.typ derive directly from the JSON/CSV result files.

## Task 1
- Awarded: 1b   (max 1b)
- Commentary: Three legitimate prompting frameworks were chosen (none is ROSES or zero-shot): RTF (Role/Task/Format), ICIO (Instruction/Context/Input/Output) and CO-STAR (Context/Objective/Style/Tone/Audience/Response). Each has a dedicated structured prompt in agents/<name>/prompt.txt whose sections match the framework parts, and each prompt references the two hand-written examples in inputs/examples.md. The Task 1 section of report.typ explains the rationale and expectation for each framework and states they were found on frompting.com/frameworks. Fully complete.

## Task 2
- Awarded: 1b   (max 1b)
- Commentary: Each prompt was run in a separate fresh agent session and produced predictions.csv (id,question,predicted_sql) with model/prompt/tokens/wall_seconds metadata in run/metadata.json; every iteration was archived under agents/<name>/attempts/ and checker output is in checker.txt. Inference time is measured (wall_seconds) and shown in the report. The Task 2 section compares first-vs-final accuracy, checker calls and session time with a bar chart of accuracy and a bar chart of session time. Predictions, timing and comparison report are all present. Fully complete.

## Task 3
- Awarded: 1b   (max 1b)
- Commentary: A new, original metric — "balanced result F1" — was proposed: per-question row-level F1 (2TP/(2TP+FP+FN)) with the mean taken separately over questions with empty correct answers and the rest, then averaged. It is implemented in analysis/src/metrics.py, computed over the Task 2 predictions, and written to per_question.csv and summary.json. The Task 3 section defines TP/FP/FN and the formula, justifies the balanced adjustment (empty answers otherwise inflate accuracy), and argues it complements rather than replaces exact accuracy. A comparison table and bar chart rank the three prompts. Fully complete.

## Task 4
- Awarded: 2b   (max 2b)
- Commentary: The report's Task 4 section provides a detailed reiteration with a progress-over-attempts line chart, a failed-question heatmap, and a significance table. Statistical significance is determined with exact McNemar tests for accuracy and paired permutation tests for balanced F1, Holm-corrected at α=0.05, all sourced from statistics.json. Differences are explained considering all three required factors: prompt (CO-STAR longest/most explicit wins; RTF shortest), model (one regex parser with checker-driven repairs; CO-STAR swings most = more risk), and coding agent (results driven by each script's parsing choices; ID 65 acted as a hard-coded-answer control). Limits (single run per framework, unreadable model scripts, confounding of prompt wording with repair choices) are honestly acknowledged. Fully complete and well above threshold.
