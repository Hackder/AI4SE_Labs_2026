# Working notes (input for the report)

## Task 1: how the clone was made

- The coding agent (Claude Code) ran `git clone https://github.com/Neltharion59/AI4SE_Playground`
  through its **Bash tool**, i.e. a shell command on the local machine. The agent has no
  built-in "clone" feature; it only issues shell commands.
- The command used the locally installed **git binary** (`/opt/homebrew/bin/git`, git 2.56.0).
- **Network access** from the agent's shell to github.com was allowed.
- The repository is **public**, so no credentials were needed in principle. In practice the
  user's global `~/.gitconfig` has `url.git@github.com:.insteadof https://github.com/`, so git
  silently rewrote the HTTPS URL to SSH (`git@github.com:Neltharion59/AI4SE_Playground`) and
  authenticated with the user's existing SSH key in `~/.ssh` (the ssh-agent held no identities,
  so the default key file was used). The agent did not configure any of this.
- **Permission prompt:** none was shown to the agent; the command ran directly under the
  session's permission mode. (Whether the user saw an approval prompt is not visible from
  inside the agent.)
- Afterwards the agent deleted the clone's `.git` directory (`rm -rf AI4SE_Playground/.git`) so
  the files are tracked as plain files in this repository. Upstream commit at clone time:
  `b17f753 Init`. Size without `.git`: 220 KB, 28 files.

The clone lives in `AI4SE_Playground/`; paths in `../Assignments/missing_code.json`
(`playground/playground/enums.py`, ...) are relative to that directory.

## Baseline playground tests (before any patching)

Run from `AI4SE_Playground/playground/` (the package `playground` and `tests/` live there; the
tests are stdlib `unittest`, no extra dependencies):

```sh
cd AI4SE_Playground/playground
../../.venv/bin/python -m unittest discover     # or: ../../.venv/bin/python -m pytest -q
```

Python 3.14.9: 481 tests, 429 pass, 52 fail (unittest: 35 failures + 17 errors). The failures
are the 10 `pass` stubs from `missing_code.json` and the code that depends on them (orders,
pricing, simulation, ...).

## Task 2: chunking decisions

- **Granularity:** AST structure, not fixed-size windows. A function or method is the unit the
  generator needs to see and the unit `missing_code.json` asks for.
- **Small classes (<= 40 lines) stay whole**; larger classes become a `class_header` chunk
  (signature, docstring, class attributes, method signatures) plus one `method` chunk per
  method. Each method chunk starts with the class signature and first docstring line, so the
  embedding and the LLM know which class it belongs to.
- **Module-level code** (docstring, imports, constants) is one `module` chunk per file; it
  shows the imports a generated method may rely on.
- **Non-Python files** (only `.gitignore`) are skipped.
- **Tests are included** and flagged `is_test`: they are part of the repository the agent works
  in and show how the target methods are called, which is useful usage context; retrieval can
  exclude them (`--no-tests`) to measure how much they help versus leak expected behaviour.
- **Target stubs get no chunk of their own:** a bare-`pass` method has only its signature,
  which the class/header chunk already shows; as its own chunk it would be a near-duplicate of
  the query and waste a top-5 slot.
- Result: 538 chunks (141 source, 397 test); kinds: 404 method, 63 class, 36 class header,
  26 module, 9 function. Text size median ~270 chars (~70 tokens), p90 ~790, max ~2 000 chars,
  well under any embedding model input limit.

## Task 3/4: storage and retrieval

- libSQL (`libsql` 0.1.11 Python package, works on Python 3.14) in a local file
  `output/index.db`. Column `embedding F32_BLOB(dim)`, vectors inserted with `vector32(?)`
  (JSON array text), DiskANN index
  `libsql_vector_idx(embedding, 'metric=cosine', 'compress_neighbors=float8', 'max_neighbors=32')`.
- Query: `vector_top_k('chunks_embedding_idx', vector32(?), n)` joined back on `rowid`, scored
  with `1 - vector_distance_cos(...)`. `--exact` (and `--no-tests`, which needs a WHERE filter)
  use a plain `ORDER BY vector_distance_cos(...) LIMIT n` scan.
- Index size: with libSQL's default index settings a 1536-dim index over ~540 rows is ~170 MB;
  the options above bring it to ~35 MB with the same recall@10 on a random test set. The
  database is regenerable and gitignored.
- The `meta` table records `embedding_model`, `dim` and `chunk_count`; the query side embeds
  with the recorded model. Compare models by indexing into separate files with `--db`.

## Task 5: generation, patching, testing

- **Prompt:** system prompt asks for only the complete method (decorators, signature, docstring,
  body) in one python block, keeping the stub signature, adding no imports. The user prompt
  lists the 5 retrieved chunks (path, lines, qualname, source), then the task: target, docstring
  and the stub (signature from the file plus the docstring). The same task text is the
  retrieval query.
- **Patching (`patcher.py`):** code is taken from a fenced block, else from the reply with prose
  before the first def/class line and unparseable trailing lines dropped. The method is found
  by name with `ast`: top level (`ok`) or inside a returned class/file (`extracted`). It is
  dedented, re-indented to the stub's column and replaces the stub's line range (decorators
  included; the stub's decorators are kept if the reply has none, e.g. `@property`). The file
  is written only if it still parses; otherwise `patch_failed` and the raw reply stays in
  `summary.json`/`trace.jsonl`.
- **Tests (`testrun.py`):** the suite runs in a subprocess (no bytecode written, so the baseline
  run on the committed clone leaves it untouched); a `sys.setprofile` hook records which target
  methods each test called, which maps every failing test to the generated methods it depends
  on. A test that calls several targets is counted under each.
- Chat calls use the `openai` SDK (already a dependency for embeddings) rather than
  langchain-openai; no temperature is sent, since reasoning models reject it.
- **Embeddings:** the course OpenAI project returns 403 for every embedding model
  (text-embedding-3-small/-large, ada-002), so the default is now the local fastembed model
  `BAAI/bge-small-en-v1.5` (384 dim, ONNX mirror `Qdrant/bge-small-en-v1.5-onnx-Q`, 64 MB in
  fastembed's temp cache). Indexing 538 chunks takes ~80 s on CPU; `index.db` is 10 MB.
- **First real run (gpt-6-luna):** 10/10 patched `ok`, 480/481 tests pass (baseline 429,
  +51), 12 076 tokens. The one failure, `test_contains_present_even_if_zero_on_hand_after_commit`,
  contradicts the `InventoryLedger.__contains__` docstring ("positive on-hand stock"); the
  model followed the docstring.
- **Model comparison and ablations** (`output/runs/comparison.md`): six allowed models pass
  468-480/481 with top-5 RAG. gpt-4.1-nano was not run: the API returns 404 "model has been
  deprecated". Weak models fail `BulkDiscountPricing.price` (they invent `Money.amount` or use
  `Money // int`); gpt-5-mini raises a bare `Exception` instead of `InvalidTransitionError`.
  Without test chunks (`--no-tests`) results barely move (478 and 477), so leaking tests is not
  what drives success. Without retrieval (`-n 0`) both models fall to the baseline (429 and
  425): they hallucinate private attribute names (`_transitions`, `line_items`, `on_hand`).
  Every run fails the disputed `__contains__` test, which shows the docstring-vs-test
  conflict rather than a model error.
