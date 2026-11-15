// Co-written by Claude Opus 5.5 from the code, NOTES.md and the committed run outputs.
// Build from Submission/: typst compile report/report.typ

#set document(title: "Week 06. Repository-aware code generation with RAG", author: "Juraj Petras")
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

= Repository-aware code generation with RAG

Week 06. Juraj Petras

All code is in `Submission/` (package `src/repo_rag/`, CLI `repo-rag`, see `README.md`). The pipeline is: AST chunking of the cloned repository, local embeddings, a libSQL vector index, top-$n$ retrieval, one LLM call per missing method, automatic patching, and a unit-test run that maps every failure back to the generated method it called.

== Task 1: Cloning the playground

Claude Code has no built-in clone feature. It ran `git clone https://github.com/Neltharion59/AI4SE_Playground` through its *Bash tool*, i.e. as a shell command on my machine, using the locally installed git.

The repository is public, so no credentials were needed in principle. In practice my global `~/.gitconfig` contains `url.git@github.com:.insteadof https://github.com/`, so git silently rewrote the HTTPS URL to SSH and authenticated with my default SSH key from `~/.ssh` (the ssh-agent held no identities). The agent configured none of this; it simply inherited my user environment. Afterwards it ran `rm -rf AI4SE_Playground/.git` so the 28 files (220 KB, upstream commit `b17f753 Init`) are tracked as plain files in my repository, in `Submission/AI4SE_Playground/`.

Before any patching, the playground's `unittest` suite gives 481 tests, 429 passing and 52 failing: the 10 `pass` stubs from `missing_code.json` and the code that depends on them.

== Task 2: Chunking

`chunker.py` splits every `.py` file with the stdlib `ast` module, not with fixed-size windows. A function or method is the unit the generator has to produce and the unit `missing_code.json` asks for, so it is also the natural unit to retrieve. The rules:

- *One `module` chunk per file* with all top-level code that is not a `def` or `class` (docstring, imports, constants). It shows which names a generated method may use without adding imports.
- *One `function` chunk per top-level function.*
- *Classes of at most 40 lines stay whole* (`class`). Small classes such as enums or dataclasses are read as a unit, and splitting them would only produce tiny chunks.
- *Larger classes are split* into a `class_header` chunk (signature, docstring, class attributes, method signatures with `...`) and one `method` chunk per method. Each method chunk starts with the class signature and the first docstring line, so both the embedding and the LLM know which class the method belongs to. The header gives the overview of the class: its attributes and its other methods.
- *Tests are included but flagged* `is_test`. They are part of the repository the agent works in and show how the target methods are called. The flag lets retrieval exclude them (`--no-tests`), which Task 5 uses to measure whether tests help legitimately or just leak the expected behaviour.
- *Stubs get no chunk of their own.* A method whose body is a bare `pass` has nothing beyond its signature, which the class or header chunk already shows. As its own chunk it would be a near-duplicate of the query and waste a top-5 slot.
- Non-Python files (only `.gitignore`) are skipped.

The chunks are stored as JSON lines in `output/chunks.jsonl` (id, path, qualname, kind, line range, `is_test`, text).

#figure(
  table(
    columns: (1fr, auto, auto, auto),
    align: (left, right, right, right),
    [Kind], [Source], [Test], [All],
    [`method`], [92], [312], [404],
    [`class`], [19], [44], [63],
    [`class_header`], [11], [25], [36],
    [`module`], [13], [13], [26],
    [`function`], [6], [3], [9],
    [Total], [141], [397], [538],
  ),
  caption: [Chunks by kind. Text length: min 72, median 270, p90 785, max 1,982 characters (median about 70 tokens), far below any embedding model's input limit.],
)

== Task 3: Embeddings and storage

*What is embedded.* Each chunk is embedded as a one-line locating header followed by its source: `# <path> :: <qualname> (<kind>)`. The header puts file, class and method names into the vector, which matters because tasks name their target class and file.

*Embedding model.* The plan was OpenAI's `text-embedding-3-small`, but the provided OpenAI key returns 403 for every embedding model (`text-embedding-3-small`, `-3-large`, `ada-002`). The pipeline therefore embeds locally with `fastembed` and `BAAI/bge-small-en-v1.5`: 384 dimensions, ONNX runtime without torch, a 64 MB ONNX model downloaded once into fastembed's cache outside the repository. Indexing all 538 chunks takes about 80 s on CPU. The embedder is pluggable behind a small `Embedder` protocol (`embedder.py`): local fastembed models, OpenAI `text-embedding-*` models and an offline deterministic hash embedder.

*Storage.* Chunks and vectors live in one local libSQL file, `output/index.db`, using libSQL's native vector support. It's basically sqlite with native vector support which makes it a perfect fit for something like this. We don't have to run a vector db as another process and don't have to implement custom searching or matching with custom storage.

- table `chunks` with the chunk fields and a column `embedding F32_BLOB(384)`, filled with `vector32(?)`;
- a DiskANN index `libsql_vector_idx(embedding, 'metric=cosine', 'compress_neighbors=float8', 'max_neighbors=32')`;
- table `meta` with `embedding_model`, `dim` and `chunk_count`, so the query side embeds with the same model.

One SQL file holds text, metadata and vectors, can be filtered with ordinary `WHERE` clauses, and needs no server. The two index options matter: with libSQL's defaults a 1536-dimensional index over about 540 rows took about 170 MB on disk; float8 neighbour vectors and at most 32 neighbours brought it to about 35 MB with the same recall\@10 on a random test set. With 384-dimensional bge-small vectors the whole database is 10 MB.

== Task 4: Retrieving the top $n$ chunks

As we used libsql this is natively supported, including cosine similarity: `vector_top_k('chunks_embedding_idx', vector32(?), n)`, `1 - vector_distance_cos(...)`

== Task 5: Generating the missing methods

*Pipeline* (`generate.py`). One run uses one chat model. It copies the playground into `output/runs/<timestamp>_<model>[_<variant>]/playground` (gitignored; the committed clone is never modified) and, for each of the 10 entries in `missing_code.json`, builds the task text, retrieves the top 5 chunks, makes one chat call and patches the reply into the copy. Then it runs the test suite on the committed clone (baseline) and on the copy, and writes `summary.json`, `summary.md` and `trace.jsonl` (every call with retrieved chunks, prompt, raw reply, tokens and timing). `repo-rag compare` aggregates all runs into `output/runs/comparison.md`.

*Prompt.* The system prompt asks for only the complete method (decorators, signature, docstring, body) in one Python block, keeping the stub's signature, adding no imports and following the conventions of the code shown. The user prompt lists the retrieved chunks (path, line range, qualname, source) and ends with the task: target, docstring and the current stub. Calls use the `openai` SDK directly and send no temperature, which reasoning models reject.

*Automatic patching* (`patcher.py`). We were allowed to paste the code in by hand; I automated it so that many models could be compared on equal terms. The code is taken from a fenced block or, failing that, from the reply with leading prose and unparseable trailing lines dropped. The method is found by name with `ast`, either at the top level (`ok`) or inside a returned class or file (`extracted`). It re-indented to the stub's column and replaces the stub's line range; the stub's decorators (such as `@property`) are kept if the reply has none. The file is written only if it still parses, otherwise the status is `patch_failed` and the raw reply is kept. In all runs below, all 10 patches came back `ok`, so the fallbacks were never needed.

*Test attribution* (`testrun.py`). The suite runs in a subprocess with a `sys.setprofile` hook that records which target methods each test calls, so each failing test is attributed to the generated methods it depends on.

=== Results

Six of the seven allowed models were run with top-5 retrieval. `gpt-4.1-nano` was not run: the API returns 404 "model has been deprecated". Two variations were run with the strongest and a weak model: `no-tests` (test chunks excluded from retrieval) and `no-rag` (no chunks at all, only the task and stub).

#figure(
  table(
    columns: (1fr, auto, auto, auto, auto, auto),
    align: (left, left, right, right, right, right),
    [Model], [Variant], [Tests passed], [Delta], [Targets all-pass], [Tokens],
    [gpt-6-luna], [top 5], [480/481], [+51], [9/10], [12,076],
    [gpt-5.6-luna], [top 5], [479/481], [+50], [9/10], [11,473],
    [gpt-5.4-nano], [top 5], [472/481], [+43], [8/10], [9,536],
    [gpt-5-nano], [top 5], [471/481], [+42], [8/10], [20,738],
    [gpt-4o-mini], [top 5], [470/481], [+41], [8/10], [9,454],
    [gpt-5-mini], [top 5], [468/481], [+39], [7/10], [14,424],
    [gpt-6-luna], [no-tests], [478/481], [+49], [8/10], [11,141],
    [gpt-4o-mini], [no-tests], [477/481], [+48], [8/10], [9,504],
    [gpt-6-luna], [no-rag], [429/481], [+0], [2/10], [8,741],
    [gpt-4o-mini], [no-rag], [425/481], [−4], [2/10], [2,122],
  ),
  caption: [Unit test results per run (embeddings `BAAI/bge-small-en-v1.5`; baseline 429/481). Delta is versus the unpatched baseline. A target is "all-pass" when every test that called it passes. All runs patched 10/10 `ok`.],
)

#let runs = ("g6", "g5.6", "5.4n", "5n", "5m", "4o", "g6 −T", "4o −T", "g6 −R", "4o −R")
#let rows = (
  ("OrderStatus.is_terminal", "4/4", "4/4", "4/4", "4/4", "4/4", "4/4", "4/4", "4/4", "3/4", "0/4"),
  ("InventoryLedger.__contains__", "4/5", "3/5", "3/5", "3/5", "4/5", "2/5", "3/5", "2/5", "0/5", "0/5"),
  ("Warehouse.stock_report", "3/3", "3/3", "3/3", "3/3", "3/3", "3/3", "3/3", "3/3", "0/3", "0/3"),
  (
    "OrderStateMachine.transition",
    "24/24",
    "24/24",
    "24/24",
    "24/24",
    "19/24",
    "24/24",
    "24/24",
    "24/24",
    "0/24",
    "0/24",
  ),
  ("OrderLog.by_status", "3/3", "3/3", "3/3", "3/3", "3/3", "3/3", "2/3", "3/3", "1/2", "0/2"),
  ("Customer.can_afford", "8/8", "8/8", "8/8", "8/8", "8/8", "8/8", "8/8", "8/8", "8/8", "8/8"),
  ("Order.__len__", "7/7", "7/7", "7/7", "7/7", "7/7", "7/7", "7/7", "7/7", "0/6", "0/6"),
  ("BulkDiscountPricing.price", "10/10", "10/10", "3/10", "2/10", "3/10", "2/10", "10/10", "9/10", "0/10", "0/10"),
  ("EventBus.__contains__", "6/6", "6/6", "6/6", "6/6", "6/6", "6/6", "6/6", "6/6", "6/6", "6/6"),
  ("Money.__bool__", "2/2", "2/2", "2/2", "2/2", "2/2", "2/2", "2/2", "2/2", "0/2", "0/2"),
)
#let cell(s) = {
  let (k, n) = s.split("/")
  if k == n { s } else { text(fill: rgb("#b00020"), weight: "bold", s) }
}

#figure(
  {
    set text(size: 8.5pt)
    table(
      columns: (auto,) + (1fr,) * runs.len(),
      align: (left,) + (right,) * runs.len(),
      inset: (x: 3pt, y: 3pt),
      [Target], ..runs.map(r => r),
      ..rows.map(r => (raw(r.at(0)),) + r.slice(1).map(cell)).flatten(),
    )
  },
  caption: [Tests calling each target that pass, per run. Columns: gpt-6-luna, gpt-5.6-luna, gpt-5.4-nano, gpt-5-nano, gpt-5-mini, gpt-4o-mini; −T is `no-tests`, −R is `no-rag`. Red cells have a failing test.],
)



=== Findings

*Retrieval is essential.* Without retrieved chunks both models end at or below the baseline (429 and 425 of 481) and only 2 of 10 targets pass, the two that need no knowledge of private state (`Customer.can_afford`, `EventBus.__contains__`). The failures are invented attribute names: `_transitions` and `allowed_transitions` on `OrderStateMachine`, `line_items` on `Order`, `on_hand` instead of `_on_hand`, `orders` instead of `_orders`, `amount` on `Money`, and invented threshold field names on `BulkDiscountPricing`. The code is plausible but does not fit this repository. With top-5 retrieval every model passes 468 to 480 tests.

*Test leakage is not what drives success.* Excluding test chunks moved gpt-6-luna from 480 to 478 and *improved* gpt-4o-mini from 470 to 477. The source chunks (the class, its header, neighbouring methods) carry the information that matters. gpt-4o-mini even went from 2/10 to 9/10 on `BulkDiscountPricing.price` without tests, though one run per setting cannot separate that from run-to-run variation.

*Where models differ.* The hardest target is `BulkDiscountPricing.price`, which needs `Money` arithmetic. Only gpt-6-luna and gpt-5.6-luna pass it; the weaker models invent `Money.amount` (gpt-5.4-nano, gpt-4o-mini) or apply `//` to a `Money` and an `int` (gpt-5-nano, gpt-5-mini). gpt-5-mini also raises a bare `Exception` in `OrderStateMachine.transition` instead of the repository's `InvalidTransitionError`, failing 5 of its 24 tests.

*The one test every run fails is disputed.* `test_contains_present_even_if_zero_on_hand_after_commit` adds 2 units of a SKU, reserves and commits both, and expects the SKU to still be `in` the ledger. The docstring in `missing_code.json` says `__contains__` returns whether the SKU "normalises to a SKU with positive on-hand stock", which is false after the commit. gpt-6-luna implemented the docstring exactly (`self._on_hand.get(sku, 0) > 0`), so its only failure reflects the conflict between docstring and test, not a model error. I expect this is the same test against cheating as in previous assignment, so with that test discounted, gpt-6-luna's patch passes every test.

== Bonus: An ideal pipeline for repository-aware code generation

*Is embedding matching the best strategy?* Not on its own. The experiment shows what the model actually needs: the target's own class (attribute names such as `_on_hand`, the methods it can call), the exact signatures of the types it touches (`Money` arithmetic, `InvalidTransitionError`), and the module's imports. Most of that is *structurally* determined by the target and can be found exactly without similarity search; embeddings were weakest exactly where a structural lookup is trivial (`Money.__bool__` got an unrelated test as its top hit). The pipeline I would build:

+ *Index the repository as a code graph, not only as text.* Parse with `ast` (or tree-sitter for other languages) into symbols with their kind, signature, docstring, attributes, and edges for contains, calls, inherits, imports and "tested by". Keep the AST chunks from Task 2 as the text units attached to graph nodes. Re-index incrementally per file on change.
+ *Deterministic context first.* For a target method, always include: its class header with attributes (including those assigned in `__init__`), sibling methods that use the same attributes, the module's imports, and the signatures and attributes of every type referenced in the class and the stub's annotations (here `Money`, `OrderStatus`, the exception classes). This would have prevented every invented attribute in the `no-rag` runs and the `Money.amount` errors in the top-5 runs.
+ *Hybrid retrieval for the rest.* Combine BM25 over identifiers with a code embedding model. Then expand the hits one hop along the call graph (callers show how the result is used, as `Order.advance` did for `transition`). Lexical search matters because tasks name identifiers exactly.
+ *A token budget instead of a fixed $n$.* Five chunks was enough here because chunks are small (median about 70 tokens). The right amount is "fill a budget of a few thousand tokens in priority order": deterministic context, then fused hits, deduplicated. Small chunks are better than large ones as long as they carry their class context, as in Task 2.
+ *Tests as a separate, explicit input.* Show existing tests of the target as usage examples, but keep a held-out set for evaluation. The `no-tests` variation showed that leakage was not the driver, but an evaluation should not depend on that.
+ *AST-aware patching.* Ask for the method only, extract and splice it with the AST, keep decorators, and reject replies that do not parse, as `patcher.py` does. For multi-file changes, use structured edits (replace symbol X) rather than free-form diffs.
+ *A test-driven feedback loop.* Run the tests that call the target (found by the call tracing in `testrun.py`), then retry with the failure messages, tracebacks and the definitions of any names the error mentions (`'Money' object has no attribute 'amount'` should trigger retrieval of `Money`). Add a type checker and linter as cheaper first gates, and cap retries. When tests and docstring disagree, as with `InventoryLedger.__contains__`, the loop should report the conflict instead of overfitting to the test.
