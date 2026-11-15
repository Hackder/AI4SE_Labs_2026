"""Turn text into vectors: a local fastembed (ONNX) model, the OpenAI API, or a deterministic
fake for tests.

The local model is the default because the course OpenAI key has no access to embedding models.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

from openai import OpenAI

FAKE_MODEL = "fake-hash"
OPENAI_DIMS = {"text-embedding-3-small": 1536, "text-embedding-3-large": 3072}


class Embedder(Protocol):
    @property
    def model(self) -> str: ...

    @property
    def dim(self) -> int: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIEmbedder:
    """OpenAI embeddings API. Vectors come back L2-normalised."""

    def __init__(self, model: str, batch_size: int = 128) -> None:
        self._model = model
        self._client = OpenAI()
        self._batch_size = batch_size
        self._dim: int | None = OPENAI_DIMS.get(model)

    @property
    def model(self) -> str:
        return self._model

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._dim = len(self.embed(["dimension probe"])[0])
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]
            response = self._client.embeddings.create(model=self._model, input=batch)
            vectors.extend(item.embedding for item in sorted(response.data, key=lambda d: d.index))
        return vectors


class LocalEmbedder:
    """A fastembed ONNX model run locally (no torch). Downloaded on first use from the
    Hugging Face repo fastembed lists for the model, into fastembed's cache directory
    (``FASTEMBED_CACHE_PATH``, default a ``fastembed_cache`` folder in the system temp dir).
    Vectors come back L2-normalised."""

    def __init__(self, model: str) -> None:
        from fastembed import TextEmbedding  # imported lazily: loading onnxruntime is slow

        self._model = model
        self._encoder = TextEmbedding(model_name=model)
        self._dim: int | None = None

    @property
    def model(self) -> str:
        return self._model

    @property
    def dim(self) -> int:
        if self._dim is None:
            self._dim = len(self.embed(["dimension probe"])[0])
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(v) for v in vector] for vector in self._encoder.embed(texts)]


class FakeEmbedder:
    """Hashed bag of identifier tokens. Deterministic and offline, with crude lexical overlap
    so retrieval results are still somewhat meaningful."""

    def __init__(self, dim: int = 256) -> None:
        self._dim = dim

    @property
    def model(self) -> str:
        return f"{FAKE_MODEL}-{self._dim}"

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self._dim
        for token in _tokens(text):
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            vector[int.from_bytes(digest[:4]) % self._dim] += 1.0 if digest[4] & 1 else -1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


def _tokens(text: str) -> list[str]:
    """Lower-cased identifier parts: ``stock_report`` and ``StockReport`` both give stock, report."""
    words = re.findall(r"[A-Za-z][a-z]*|[A-Z]+(?![a-z])|\d+", text)
    return [w.lower() for w in words if len(w) > 1]


def make_embedder(model: str) -> Embedder:
    """``fake`` or ``fake-hash[-dim]`` gives the fake embedder, ``text-embedding-*`` the OpenAI
    API, anything else a local fastembed model (e.g. ``BAAI/bge-small-en-v1.5``)."""
    if model == "fake" or model.startswith(FAKE_MODEL):
        suffix = model.removeprefix(FAKE_MODEL).lstrip("-")
        return FakeEmbedder(int(suffix)) if suffix.isdigit() else FakeEmbedder()
    if model.startswith("text-embedding-"):
        return OpenAIEmbedder(model)
    return LocalEmbedder(model)
