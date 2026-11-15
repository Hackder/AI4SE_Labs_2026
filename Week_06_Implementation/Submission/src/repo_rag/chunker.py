"""Split a Python repository into structural chunks with the stdlib ``ast`` module.

Granularity:
- one ``module`` chunk per file with the top-level code that is not a def or class
  (docstring, imports, constants);
- one ``function`` chunk per top-level function;
- one ``class`` chunk per class of at most ``MAX_CLASS_LINES`` lines;
- a larger class becomes a ``class_header`` chunk (signature, docstring, class attributes and
  method signatures) plus one ``method`` chunk per method, prefixed with a short class context.

Methods whose body is a bare ``pass`` are the unimplemented targets of the assignment. They
carry nothing beyond their signature, so they get no chunk of their own; the signature stays
visible in the class or class header chunk. Non-Python files are skipped.
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

type Kind = Literal["module", "function", "class", "class_header", "method"]

MAX_CLASS_LINES = 40
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}


@dataclass(frozen=True)
class Chunk:
    id: str
    path: str
    qualname: str
    kind: Kind
    start_line: int
    end_line: int
    is_test: bool
    text: str

    def embedding_text(self) -> str:
        """The representation that is embedded: a locating header followed by the source."""
        return f"# {self.path} :: {self.qualname} ({self.kind})\n{self.text}"


def _segment(lines: list[str], node: ast.stmt) -> tuple[int, int, str]:
    """Source of a statement including its decorators, as (start, end, text), 1-based."""
    start = min([node.lineno, *(d.lineno for d in getattr(node, "decorator_list", []))])
    end = node.end_lineno or node.lineno
    return start, end, "".join(lines[start - 1 : end])


def _is_stub(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return len(node.body) == 1 and isinstance(node.body[0], ast.Pass)


def _signature(
    lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
) -> str:
    """Decorators and the ``def``/``class`` line(s) up to the start of the body."""
    start, _, _ = _segment(lines, node)
    body_start = node.body[0].lineno
    if ast.get_docstring(node) is None and body_start == node.lineno:
        return lines[node.lineno - 1].rstrip()  # one-line def such as ``def f(): pass``
    return "".join(lines[start - 1 : body_start - 1]).rstrip()


def _class_header(lines: list[str], node: ast.ClassDef) -> str:
    """Class signature, docstring, class-level statements and method signatures."""
    parts = [_signature(lines, node)]
    doc = ast.get_docstring(node)
    if doc:
        parts.append(f'    """{doc}"""')
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parts.append(_signature(lines, child) + " ...")
        elif not (isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant)):
            parts.append(_segment(lines, child)[2].rstrip())
    return "\n".join(parts) + "\n"


def _method_context(node: ast.ClassDef, lines: list[str]) -> str:
    doc = ast.get_docstring(node)
    first = doc.splitlines()[0] if doc else ""
    header = _signature(lines, node).splitlines()[-1]
    return f"{header}\n" + (f'    """{first}"""\n' if first else "") + "    ...\n"


def chunk_source(source: str, path: str, is_test: bool = False) -> list[Chunk]:
    """Chunk one Python file. ``path`` is stored as given (relative to the repository root)."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    chunks: list[Chunk] = []

    def add(qualname: str, kind: Kind, start: int, end: int, text: str) -> None:
        chunk_id = f"{path}::{qualname}" if kind != "class_header" else f"{path}::{qualname}#header"
        chunks.append(Chunk(chunk_id, path, qualname, kind, start, end, is_test, text))

    module_parts: list[tuple[int, int, str]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _is_stub(node):
                add(node.name, "function", *_segment(lines, node))
        elif isinstance(node, ast.ClassDef):
            start, end, text = _segment(lines, node)
            if end - start + 1 <= MAX_CLASS_LINES:
                add(node.name, "class", start, end, text)
                continue
            add(node.name, "class_header", start, end, _class_header(lines, node))
            context = _method_context(node, lines)
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and not _is_stub(
                    child
                ):
                    m_start, m_end, m_text = _segment(lines, child)
                    add(f"{node.name}.{child.name}", "method", m_start, m_end, context + m_text)
        else:
            module_parts.append(_segment(lines, node))

    if module_parts:
        text = "\n".join(part[2].rstrip() for part in module_parts) + "\n"
        add("<module>", "module", module_parts[0][0], module_parts[-1][1], text)
    chunks.sort(key=lambda c: c.start_line)
    return chunks


def chunk_repository(repo_dir: Path) -> list[Chunk]:
    """Chunk every ``.py`` file under ``repo_dir``; other files are skipped."""
    chunks: list[Chunk] = []
    for file in sorted(repo_dir.rglob("*.py")):
        rel = file.relative_to(repo_dir)
        if SKIP_DIRS.intersection(rel.parts):
            continue
        is_test = "tests" in rel.parts or file.name.startswith("test_")
        chunks.extend(chunk_source(file.read_text(encoding="utf-8"), rel.as_posix(), is_test))
    return chunks


def save_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def load_chunks(path: Path) -> list[Chunk]:
    with path.open(encoding="utf-8") as f:
        return [Chunk(**json.loads(line)) for line in f if line.strip()]
