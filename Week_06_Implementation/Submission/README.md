# repo-rag

Retrieval for repository-aware code generation over `AI4SE_Playground/` (the cloned
playground repository): AST chunking, embeddings, libSQL native vector search.

```sh
uv sync
cp .env.example .env   # then set OPENAI_API_KEY (optional EMBEDDING_MODEL)

uv run repo-rag chunk                 # AI4SE_Playground -> output/chunks.jsonl
uv run repo-rag index                 # embed with text-embedding-3-small -> output/index.db
uv run repo-rag index --model fake    # offline deterministic hash embedder, no API key
uv run repo-rag query "Return a mapping of SKU to available quantity." -n 5 [--show]
```

`query` options: `--no-tests` (exclude test chunks), `--exact` (exact scan instead of the ANN
index), `--db PATH` (use another index, e.g. one per embedding model).

From Python: `repo_rag.retrieve.retrieve(task_text, n)` returns `Hit(chunk, score)` objects.

## Layout

- `src/repo_rag/chunker.py`: AST chunking, JSONL persistence
- `src/repo_rag/embedder.py`: OpenAI and fake embedders
- `src/repo_rag/store.py`: libSQL schema, insert, ANN and exact search
- `src/repo_rag/retrieve.py`: `build_index`, `retrieve`
- `src/repo_rag/cli.py`: `chunk`, `index`, `query` commands
- `typings/libsql/`: minimal type stub for the untyped libsql extension
- `output/chunks.jsonl`: the chunks (Task 2 output); `output/*.db` is generated, not committed
- `NOTES.md`: clone mechanism, baseline test run, design notes for the report

## Checks

```sh
uv run ruff check && uv run ruff format --check && uv run basedpyright && uv run pytest
```
