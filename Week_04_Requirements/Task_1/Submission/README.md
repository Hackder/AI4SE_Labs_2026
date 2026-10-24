# req-refinery

LangGraph agentic network that turns the document corpus in `../data/corpus/` into one
requirements specification.

```sh
uv sync
cp .env.example .env   # then set OPENAI_API_KEY
uv run python -m req_refinery.main --input ../data/corpus --output output/
```

Options: `--graph hybrid|network` (default `hybrid`), `--limit N` (first N documents),
`--max-rounds 5`, `--mock` (fake LLM from `tests/`).

## Graphs

- `hybrid` (default): per-document extraction, one whole-corpus consolidation call, then the
  shared review loop, attribution pass and render. The submission uses this graph; its
  document is `output/hybrid/requirements.md`.
- `network`: per-document extraction, an LLM merge and deduplication step and a
  per-document coverage pass, then the same review loop, attribution pass and render.

The `network` graph and the baseline are comparison outputs used in the report.

## Output layout

```
output/
  hybrid/     requirements.md, requirements.json from the latest hybrid run
  network/    requirements.md, requirements.json from the latest network run
  baseline/   requirements.md, run.json from the single-call baseline
  runs/<timestamp>_<graph>/
    trace.jsonl         one record per node execution (LLM and deterministic), with start,
                        end and duration; LLM nodes include every call's messages, raw
                        response, parsed output and token usage
    state/NN_<node>.json  full graph state snapshot after each superstep
    requirements.md, requirements.json
```

`output/runs/` holds the two runs whose documents are in `output/hybrid/` and `output/network/`.
`report/run_history.csv` is a hand-kept record of all 20 development runs plus the baseline.
18 of those runs are not stored in `output/runs/`.

## Report

From this directory: `typst compile --root . report/report.typ`.

## Baseline

One gpt-5.6-luna call over the whole corpus, in the same document format:

```sh
uv run python -m req_refinery.baseline --input ../data/corpus --output output/
```

It writes `output/baseline/requirements.md` and `output/baseline/run.json` (prompt, raw
response, token usage, wall time, finish reason).

## Checks

```sh
uv run pytest -q
uv run ruff format --check . && uv run ruff check . && uv run basedpyright
```
