"""Index chunks and retrieve the most relevant ones for a task description."""

from __future__ import annotations

from pathlib import Path

from .chunker import Chunk
from .config import DB_PATH
from .embedder import Embedder, make_embedder
from .store import Hit, VectorStore


def build_index(chunks: list[Chunk], embedder: Embedder, db_path: Path | str = DB_PATH) -> None:
    vectors = embedder.embed([chunk.embedding_text() for chunk in chunks])
    store = VectorStore(db_path)
    try:
        store.rebuild(embedder.model, embedder.dim, chunks, vectors)
    finally:
        store.close()


def retrieve(
    task_text: str,
    n: int = 5,
    db_path: Path | str = DB_PATH,
    include_tests: bool = True,
    exact: bool = False,
    embedder: Embedder | None = None,
) -> list[Hit]:
    """Top ``n`` chunks for ``task_text`` with cosine similarity scores.

    The query is embedded with the model recorded in the database unless ``embedder`` is given;
    a given embedder must match that model.
    """
    store = VectorStore(db_path)
    try:
        model = store.meta()["embedding_model"]
        if embedder is None:
            embedder = make_embedder(model)
        elif embedder.model != model:
            raise ValueError(f"index was built with {model!r}, not {embedder.model!r}")
        query = embedder.embed([task_text])[0]
        return store.search(query, n, include_tests=include_tests, exact=exact)
    finally:
        store.close()
