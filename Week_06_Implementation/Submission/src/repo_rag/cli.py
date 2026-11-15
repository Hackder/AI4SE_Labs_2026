"""Command line: ``repo-rag chunk``, ``repo-rag index``, ``repo-rag query``."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .chunker import chunk_repository, load_chunks, save_chunks
from .config import CHUNKS_PATH, DB_PATH, REPO_DIR, embedding_model
from .embedder import make_embedder
from .retrieve import build_index, retrieve


def _chunk(args: argparse.Namespace) -> None:
    chunks = chunk_repository(args.repo)
    save_chunks(chunks, args.out)
    lines = sorted(c.text.count("\n") for c in chunks)
    chars = sorted(len(c.text) for c in chunks)
    print(f"{len(chunks)} chunks -> {args.out}")
    print("by kind:", dict(Counter(c.kind for c in chunks)))
    print(f"tests: {sum(c.is_test for c in chunks)}, source: {sum(not c.is_test for c in chunks)}")
    print(f"lines  min/median/max: {lines[0]}/{lines[len(lines) // 2]}/{lines[-1]}")
    print(f"chars  min/median/max: {chars[0]}/{chars[len(chars) // 2]}/{chars[-1]}")


def _index(args: argparse.Namespace) -> None:
    chunks = load_chunks(args.chunks)
    embedder = make_embedder(args.model)
    build_index(chunks, embedder, args.db)
    print(f"indexed {len(chunks)} chunks with {embedder.model} (dim {embedder.dim}) -> {args.db}")


def _query(args: argparse.Namespace) -> None:
    hits = retrieve(args.task, args.n, args.db, include_tests=not args.no_tests, exact=args.exact)
    for rank, hit in enumerate(hits, 1):
        c = hit.chunk
        print(
            f"{rank}. {hit.score:.4f}  {c.path}:{c.start_line}-{c.end_line}  {c.qualname} ({c.kind})"
        )
        if args.show:
            print(c.text)


def main() -> None:
    parser = argparse.ArgumentParser(prog="repo-rag")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("chunk", help="chunk the repository into a JSONL file")
    p.add_argument("--repo", type=Path, default=REPO_DIR)
    p.add_argument("--out", type=Path, default=CHUNKS_PATH)
    p.set_defaults(func=_chunk)

    p = sub.add_parser("index", help="embed the chunks and store them in libSQL")
    p.add_argument("--chunks", type=Path, default=CHUNKS_PATH)
    p.add_argument("--db", type=Path, default=DB_PATH)
    p.add_argument(
        "--model",
        default=embedding_model(),
        help="OpenAI embedding model, or 'fake' for the offline hash embedder",
    )
    p.set_defaults(func=_index)

    p = sub.add_parser("query", help="retrieve the top-n chunks for a task description")
    p.add_argument("task")
    p.add_argument("-n", type=int, default=5)
    p.add_argument("--db", type=Path, default=DB_PATH)
    p.add_argument("--no-tests", action="store_true", help="exclude test chunks")
    p.add_argument("--exact", action="store_true", help="exact scan instead of the ANN index")
    p.add_argument("--show", action="store_true", help="print chunk source")
    p.set_defaults(func=_query)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
