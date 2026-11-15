# repo-rag

Retrieval for repository-aware code generation over `AI4SE_Playground/` (the cloned
playground repository): AST chunking, embeddings, libSQL native vector search.

```sh
uv sync
cp .env.example .env   # then set OPENAI_API_KEY (for generation; optional EMBEDDING_MODEL)

uv run repo-rag chunk                 # AI4SE_Playground -> output/chunks.jsonl
uv run repo-rag index                 # embed locally with BAAI/bge-small-en-v1.5 -> output/index.db
uv run repo-rag index --model jinaai/jina-embeddings-v2-base-code --db output/jina.db
uv run repo-rag index --model text-embedding-3-small   # OpenAI; the course key has no access
uv run repo-rag index --model fake    # offline deterministic hash embedder
uv run repo-rag query "Return a mapping of SKU to available quantity." -n 5 [--show]
```

Local models run with `fastembed` (ONNX runtime, no torch). The model (~67 MB for
bge-small) is downloaded on first use into fastembed's cache (`FASTEMBED_CACHE_PATH`, default
`$TMPDIR/fastembed_cache`), outside the repository.

`query` options: `--no-tests` (exclude test chunks), `--exact` (exact scan instead of the ANN
index), `--db PATH` (use another index, e.g. one per embedding model).

From Python: `repo_rag.retrieve.retrieve(task_text, n)` returns `Hit(chunk, score)` objects.

## Generating the missing methods (Task 5)

```sh
uv run repo-rag generate                                # gpt-6-luna, all of missing_code.json
uv run repo-rag generate --model gpt-6-luna gpt-5-mini  # one run per model
uv run repo-rag generate --model fake                   # offline: answers with a non-solution
uv run repo-rag compare                                 # table over all runs -> output/runs/comparison.md
```

`--model` accepts only the allowed models (gpt-6-luna, gpt-5.6-luna, gpt-5.4-nano, gpt-5-nano,
gpt-5-mini, gpt-4.1-nano, gpt-4o-mini) or `fake`. Other options: `-n` (chunks per task, default 5),
`--no-tests` (retrieve no test chunks), `--db`, `--tasks`, `--repo`, `--runs-dir`.

Per entry the run builds the task text (target, docstring and the stub signature), retrieves the
top 5 chunks, asks the model for the method only, and patches it into a copy of the playground.
Each run writes to `output/runs/<timestamp>_<model>/`:

- `playground/`: the patched copy (gitignored); the committed clone is never modified
- `trace.jsonl`: every LLM call (retrieved chunks, prompt, raw response, token usage, timing)
- `summary.json` / `summary.md`: patch status per target (`ok`, `extracted` when the method was
  pulled out of a returned class or file, `patch_failed` with the raw response kept, `llm_error`),
  unit test counts versus the unpatched baseline, and for each target the tests that called it
  and which of those fail

## Layout

- `src/repo_rag/chunker.py`: AST chunking, JSONL persistence
- `src/repo_rag/embedder.py`: local fastembed, OpenAI and fake embedders
- `src/repo_rag/store.py`: libSQL schema, insert, ANN and exact search
- `src/repo_rag/retrieve.py`: `build_index`, `retrieve`
- `src/repo_rag/llm.py`: OpenAI chat model and the offline fake, allowed model list
- `src/repo_rag/patcher.py`: extract the method from a reply and splice it over the stub
- `src/repo_rag/testrun.py`: run the playground tests, recording which targets each test calls
- `src/repo_rag/generate.py`: the Task 5 pipeline (`run_generation`) and `compare_runs`
- `src/repo_rag/cli.py`: `chunk`, `index`, `query`, `generate`, `compare` commands
- `typings/libsql/`: minimal type stub for the untyped libsql extension
- `output/chunks.jsonl`: the chunks (Task 2 output); `output/*.db` is generated, not committed
- `NOTES.md`: clone mechanism, baseline test run, design notes for the report

## Checks

```sh
uv run ruff check && uv run ruff format --check && uv run basedpyright && uv run pytest
```
