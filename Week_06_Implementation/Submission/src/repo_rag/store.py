"""Chunk and embedding storage in a local libSQL file with native vector search.

One database file holds the vectors of one embedding model; the model name and dimension are
kept in the ``meta`` table, so the query side can embed with the same model. To compare models,
index into separate files with ``--db``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import libsql

from .chunker import Chunk

INDEX_NAME = "chunks_embedding_idx"
# DiskANN settings. With the defaults a 1536-dim index over ~540 chunks takes ~170 MB on disk;
# float8 neighbour vectors and at most 32 neighbours bring that to ~35 MB at the same recall.
INDEX_OPTIONS = "'metric=cosine', 'compress_neighbors=float8', 'max_neighbors=32'"
_COLUMNS = "c.id, c.path, c.qualname, c.kind, c.start_line, c.end_line, c.is_test, c.text"


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float  # cosine similarity, 1 - vector_distance_cos


def _vec(values: list[float]) -> str:
    return json.dumps(values)


class VectorStore:
    def __init__(self, path: Path | str) -> None:
        if isinstance(path, Path):
            path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = libsql.connect(str(path))

    def close(self) -> None:
        self._conn.close()

    def rebuild(
        self, model: str, dim: int, chunks: list[Chunk], vectors: list[list[float]]
    ) -> None:
        """Replace the whole index with ``chunks`` and their ``vectors``."""
        if len(chunks) != len(vectors):
            raise ValueError("one vector per chunk expected")
        c = self._conn
        c.execute("DROP INDEX IF EXISTS " + INDEX_NAME)
        c.execute("DROP TABLE IF EXISTS chunks")
        c.execute("DROP TABLE IF EXISTS meta")
        c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        c.execute(
            f"""CREATE TABLE chunks (
                rowid INTEGER PRIMARY KEY,
                id TEXT NOT NULL UNIQUE,
                path TEXT NOT NULL,
                qualname TEXT NOT NULL,
                kind TEXT NOT NULL,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                is_test INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding F32_BLOB({int(dim)}) NOT NULL
            )"""
        )
        c.execute(
            f"CREATE INDEX {INDEX_NAME} ON chunks (libsql_vector_idx(embedding, {INDEX_OPTIONS}))"
        )
        c.executemany(
            "INSERT INTO meta (key, value) VALUES (?, ?)",
            [("embedding_model", model), ("dim", str(dim)), ("chunk_count", str(len(chunks)))],
        )
        for chunk, vector in zip(chunks, vectors, strict=True):
            c.execute(
                "INSERT INTO chunks (id, path, qualname, kind, start_line, end_line, is_test, text,"
                " embedding) VALUES (?, ?, ?, ?, ?, ?, ?, ?, vector32(?))",
                (
                    chunk.id,
                    chunk.path,
                    chunk.qualname,
                    chunk.kind,
                    chunk.start_line,
                    chunk.end_line,
                    int(chunk.is_test),
                    chunk.text,
                    _vec(vector),
                ),
            )
        c.commit()

    def meta(self) -> dict[str, str]:
        rows = self._conn.execute("SELECT key, value FROM meta").fetchall()
        return {str(key): str(value) for key, value in rows}

    def search(
        self, query: list[float], n: int, include_tests: bool = True, exact: bool = False
    ) -> list[Hit]:
        """Top ``n`` chunks by cosine similarity.

        Uses the ANN index (``vector_top_k``) by default. Filtering out tests, or ``exact=True``,
        switches to an exact scan ordered by ``vector_distance_cos``.
        """
        q = _vec(query)
        if include_tests and not exact:
            sql = (
                f"SELECT {_COLUMNS}, vector_distance_cos(c.embedding, vector32(?)) AS d "
                f"FROM vector_top_k('{INDEX_NAME}', vector32(?), ?) AS k "
                "JOIN chunks AS c ON c.rowid = k.id ORDER BY d"
            )
            params: tuple[object, ...] = (q, q, n)
        else:
            where = "" if include_tests else "WHERE c.is_test = 0 "
            sql = (
                f"SELECT {_COLUMNS}, vector_distance_cos(c.embedding, vector32(?)) AS d "
                f"FROM chunks AS c {where}ORDER BY d LIMIT ?"
            )
            params = (q, n)
        rows = self._conn.execute(sql, params).fetchall()
        return [
            Hit(
                Chunk(r[0], r[1], r[2], r[3], r[4], r[5], bool(r[6]), r[7]),
                1.0 - float(r[8]),
            )
            for r in rows
        ]
