"""Deterministic node that loads the corpus and assigns document IDs."""

from pathlib import Path

from req_refinery.state import Document, GraphState
from req_refinery.trace import Deps, NodeResult


def _is_text(data: bytes) -> bool:
    return b"\x00" not in data[:8192]


async def load_corpus(state: GraphState, _deps: Deps) -> NodeResult:
    root = Path(state["input_dir"])
    if not root.is_dir():
        raise FileNotFoundError(f"input directory not found: {root}")
    files = sorted(
        (p for p in root.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(root).as_posix(),
    )
    texts: list[tuple[str, str]] = []
    skipped: list[dict[str, str]] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if not _is_text(data):
            skipped.append({"path": rel, "reason": "binary content (NUL bytes)"})
            continue
        texts.append((rel, data.decode("utf-8", errors="replace")))
    limit = state["limit"]
    if limit is not None:
        texts = texts[:limit]
    if not texts:
        raise ValueError(f"no text documents found in {root}")
    width = max(2, len(str(len(texts))))
    documents = [
        Document(id=f"D{i:0{width}d}", path=rel, text=text)
        for i, (rel, text) in enumerate(texts, start=1)
    ]
    return NodeResult(
        update={"documents": documents},
        payload={
            "inputs": {
                "graph": state["graph"],
                "input_dir": str(root),
                "limit": limit,
                "files_seen": len(files),
            },
            "outputs": {
                "documents": [
                    {"id": d.id, "path": d.path, "chars": len(d.text)} for d in documents
                ],
                "skipped": skipped,
            },
        },
        round=state["round"],
    )
