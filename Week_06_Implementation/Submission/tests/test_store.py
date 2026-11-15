from pathlib import Path

import pytest

from repo_rag.chunker import Chunk
from repo_rag.embedder import FakeEmbedder
from repo_rag.retrieve import build_index, retrieve
from repo_rag.store import VectorStore


def _chunk(name: str, text: str, is_test: bool = False) -> Chunk:
    return Chunk(f"m.py::{name}", "m.py", name, "function", 1, 2, is_test, text)


CHUNKS = [
    _chunk("stock_report", "def stock_report(self): return warehouse stock report per sku"),
    _chunk("can_afford", "def can_afford(self, total): return customer balance credit limit"),
    _chunk("transition", "def transition(self, source, target): order status state machine"),
    _chunk("test_stock_report", "def test_stock_report(): warehouse stock report sku", True),
]


def test_fake_embedder_is_deterministic_and_normalised() -> None:
    a, b = FakeEmbedder(64).embed(["hello world", "hello world"])
    assert a == b and len(a) == 64
    assert sum(v * v for v in a) == pytest.approx(1.0)


def test_round_trip(tmp_path: Path) -> None:
    db = tmp_path / "index.db"
    build_index(CHUNKS, FakeEmbedder(64), db)

    store = VectorStore(db)
    assert store.meta() == {"embedding_model": "fake-hash-64", "dim": "64", "chunk_count": "4"}
    store.close()

    hits = retrieve("warehouse stock report", n=2, db_path=db)
    assert len(hits) == 2
    assert {h.chunk.qualname for h in hits} == {"stock_report", "test_stock_report"}
    assert hits[0].score >= hits[1].score
    assert hits[0].chunk in CHUNKS

    exact = retrieve("warehouse stock report", n=2, db_path=db, exact=True)
    assert [h.chunk for h in exact] == [h.chunk for h in hits]

    no_tests = retrieve("warehouse stock report", n=2, db_path=db, include_tests=False)
    assert no_tests[0].chunk.qualname == "stock_report"
    assert not any(h.chunk.is_test for h in no_tests)


def test_model_mismatch_is_rejected(tmp_path: Path) -> None:
    db = tmp_path / "index.db"
    build_index(CHUNKS, FakeEmbedder(64), db)
    with pytest.raises(ValueError):
        retrieve("anything", db_path=db, embedder=FakeEmbedder(32))
