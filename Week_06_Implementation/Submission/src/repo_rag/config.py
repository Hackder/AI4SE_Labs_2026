"""Paths and settings shared by the CLI steps."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

SUBMISSION_DIR = Path(__file__).resolve().parents[2]
REPO_DIR = SUBMISSION_DIR / "AI4SE_Playground"
OUTPUT_DIR = SUBMISSION_DIR / "output"
CHUNKS_PATH = OUTPUT_DIR / "chunks.jsonl"
DB_PATH = OUTPUT_DIR / "index.db"

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

load_dotenv(SUBMISSION_DIR / ".env")


def embedding_model() -> str:
    """Embedding model name, overridable with EMBEDDING_MODEL in the environment or .env."""
    return os.environ.get("EMBEDDING_MODEL") or DEFAULT_EMBEDDING_MODEL
