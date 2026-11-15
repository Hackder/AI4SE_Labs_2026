from pathlib import Path

from repo_rag.chunker import MAX_CLASS_LINES, chunk_source, load_chunks, save_chunks

SAMPLE = '''"""Sample module."""
import math

LIMIT = 3


def area(r: float) -> float:
    """Circle area."""
    return math.pi * r * r


class Small:
    """A small class."""

    def todo(self) -> int:
        pass

    def done(self) -> int:
        return 1
'''


def _big_class() -> str:
    methods = "".join(
        f"    def m{i}(self) -> int:\n        return {i}\n\n" for i in range(MAX_CLASS_LINES)
    )
    return (
        f'class Big:\n    """Big class doc.\n\n    More text."""\n\n    KIND = "big"\n\n{methods}'
    )


def test_small_module_chunks() -> None:
    chunks = chunk_source(SAMPLE, "pkg/sample.py")
    by_name = {c.qualname: c for c in chunks}
    assert [c.kind for c in chunks] == ["module", "function", "class"]
    assert by_name["<module>"].text == '"""Sample module."""\nimport math\nLIMIT = 3\n'
    assert by_name["area"].start_line == 7 and by_name["area"].end_line == 9
    assert "def todo" in by_name["Small"].text  # small class stays whole, stub included
    assert all(c.path == "pkg/sample.py" and not c.is_test for c in chunks)


def test_big_class_splits_into_methods_with_context() -> None:
    source = _big_class() + "    def stub(self) -> None:\n        pass\n"
    chunks = chunk_source(source, "big.py", is_test=True)
    kinds = [c.kind for c in chunks]
    assert kinds.count("class_header") == 1
    assert kinds.count("method") == MAX_CLASS_LINES  # the bare-pass stub gets no chunk
    header = next(c for c in chunks if c.kind == "class_header")
    assert 'KIND = "big"' in header.text and "def stub(self) -> None: ..." in header.text
    m3 = next(c for c in chunks if c.qualname == "Big.m3")
    assert m3.text.startswith('class Big:\n    """Big class doc."""\n    ...\n    def m3(self)')
    assert m3.id == "big.py::Big.m3" and m3.is_test


def test_save_load_round_trip(tmp_path: Path) -> None:
    chunks = chunk_source(SAMPLE, "pkg/sample.py")
    path = tmp_path / "chunks.jsonl"
    save_chunks(chunks, path)
    assert load_chunks(path) == chunks
