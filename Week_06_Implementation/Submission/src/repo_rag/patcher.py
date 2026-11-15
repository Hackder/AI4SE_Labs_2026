"""Turn an LLM reply into one method and splice it over the stub, using ``ast`` for both.

Reply handling: the code is taken from a fenced block if there is one, otherwise from the reply
itself, dropping prose before the first ``def``/``class``/decorator line and trailing lines that
do not parse. The method is then looked up by name: at the top level (status ``ok``) or inside
a class, i.e. the model returned the whole class or file (status ``extracted``). If neither
works, or the patched file would not parse, the file is left untouched (``patch_failed``).
"""

from __future__ import annotations

import ast
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

type Status = Literal["ok", "extracted", "patch_failed"]
type FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef

_FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
_CODE_START = re.compile(r"^\s*(@|def |async def |class )")


@dataclass(frozen=True)
class PatchResult:
    status: Status
    code: str | None  # the method as inserted, None if the patch failed
    error: str | None = None


def start_line(node: FunctionNode) -> int:
    """First line of a function including its decorators."""
    return min([node.lineno, *(d.lineno for d in node.decorator_list)])


def find_method(tree: ast.Module, class_name: str, method: str) -> FunctionNode:
    """The method ``class_name.method`` in a parsed file; ValueError if it is missing."""
    for cls in ast.walk(tree):
        if isinstance(cls, ast.ClassDef) and cls.name == class_name:
            for child in cls.body:
                is_function = isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                if is_function and child.name == method:
                    return child
    raise ValueError(f"method {class_name}.{method} not found")


def _parse_snippet(text: str) -> tuple[list[str], ast.Module] | None:
    """Lines and tree of the longest parseable code run starting at the first def/class line."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if _CODE_START.match(line)), None)
    if start is None:
        return None
    for end in range(len(lines), start, -1):
        snippet = textwrap.dedent("\n".join(lines[start:end]))
        try:
            return snippet.splitlines(), ast.parse(snippet)
        except SyntaxError:
            continue
    return None


def _find_in(tree: ast.Module, class_name: str, method: str) -> tuple[FunctionNode, bool] | None:
    """The method node, and whether it had to be pulled out of a class."""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method:
            return node, False
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    classes.sort(key=lambda c: c.name != class_name)  # the target class first
    for cls in classes:
        for child in cls.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == method:
                return child, True
    return None


def extract_method(reply: str, class_name: str, method: str) -> tuple[str, Status] | None:
    """The method's source at column 0, with ``ok`` or ``extracted``; None if not found."""
    for candidate in [*_FENCE.findall(reply), reply]:
        parsed = _parse_snippet(candidate)
        if parsed is None:
            continue
        lines, tree = parsed
        found = _find_in(tree, class_name, method)
        if found is None:
            continue
        node, wrapped = found
        code = textwrap.dedent("\n".join(lines[start_line(node) - 1 : node.end_lineno]))
        return code.rstrip() + "\n", "extracted" if wrapped else "ok"
    return None


def patch_method(path: Path, class_name: str, method: str, reply: str) -> PatchResult:
    """Replace the stub ``class_name.method`` in ``path`` (decorators included) with the method
    found in ``reply``, re-indented to the class body. Stub decorators are kept if the reply
    has none. The file is only written if the result parses."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    stub = find_method(tree, class_name, method)

    extracted = extract_method(reply, class_name, method)
    if extracted is None:
        return PatchResult("patch_failed", None, f"no parseable method {method!r} in the reply")
    code, status = extracted

    lines = source.splitlines(keepends=True)
    start, end = start_line(stub), stub.end_lineno or stub.lineno
    if stub.decorator_list and not code.startswith("@"):
        code = textwrap.dedent("".join(lines[start - 1 : stub.lineno - 1])) + code
    code = textwrap.indent(code, " " * stub.col_offset)
    patched = "".join(lines[: start - 1]) + code + "".join(lines[end:])
    try:
        ast.parse(patched)
    except SyntaxError as exc:
        return PatchResult("patch_failed", None, f"patched file does not parse: {exc}")
    path.write_text(patched, encoding="utf-8")
    return PatchResult(status, code)
