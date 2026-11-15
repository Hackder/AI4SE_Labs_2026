import runpy
from pathlib import Path

import pytest

from repo_rag.patcher import patch_method

SOURCE = '''"""Sample module."""


class Box:
    """A box of items."""

    def __init__(self, items: list[int]) -> None:
        self._items = list(items)

    @property
    def empty(self) -> bool:
        pass

    def count(self) -> int:
        pass

    def last(self) -> int:
        return self._items[-1]
'''

COUNT = "def count(self) -> int:\n    return len(self._items)\n"
INDENTED = "    def count(self) -> int:\n        return len(self._items)\n"


def _load(path: Path) -> type:
    box = runpy.run_path(str(path))["Box"]
    assert isinstance(box, type)
    return box


@pytest.mark.parametrize(
    ("reply", "status"),
    [
        (f"Sure! Here it is:\n\n```python\n{COUNT}```\n\nThis counts the items.", "ok"),
        (INDENTED, "ok"),
        (f"Here you go:\n{INDENTED}\nIt returns the length.", "ok"),
        (f"```python\nclass Box:\n{INDENTED}```", "extracted"),
        (
            f'```python\n"""Module."""\nimport math\n\n\nclass Box:\n    X = 1\n\n{INDENTED}```',
            "extracted",
        ),
        (f"```python\n{COUNT}", "ok"),  # unclosed fence
    ],
)
def test_reply_shapes_are_patched(tmp_path: Path, reply: str, status: str) -> None:
    path = tmp_path / "box.py"
    path.write_text(SOURCE, encoding="utf-8")

    result = patch_method(path, "Box", "count", reply)

    assert result.status == status
    assert result.code == "    def count(self) -> int:\n        return len(self._items)\n"
    box = _load(path)
    assert box([1, 2, 3]).count() == 3
    assert box([1, 2]).last() == 2  # neighbouring code untouched
    assert path.read_text(encoding="utf-8").count("pass") == 1  # only the other stub is left


def test_stub_decorators_are_kept(tmp_path: Path) -> None:
    path = tmp_path / "box.py"
    path.write_text(SOURCE, encoding="utf-8")

    without = "def empty(self) -> bool:\n    return not self._items\n"
    assert patch_method(path, "Box", "empty", without).status == "ok"
    assert _load(path)([]).empty is True

    replaced = "@property\ndef empty(self) -> bool:\n    return len(self._items) == 0\n"
    assert patch_method(path, "Box", "empty", replaced).status == "ok"
    assert path.read_text(encoding="utf-8").count("@property") == 1
    assert _load(path)([1]).empty is False


@pytest.mark.parametrize(
    "reply",
    [
        "I am sorry, I cannot help with that.",
        "```python\ndef other(self) -> int:\n    return 1\n```",
        "```python\ndef count(self) -> int:\n    return len(self._items\n```",
    ],
)
def test_garbage_leaves_the_file_untouched(tmp_path: Path, reply: str) -> None:
    path = tmp_path / "box.py"
    path.write_text(SOURCE, encoding="utf-8")

    result = patch_method(path, "Box", "count", reply)

    assert result.status == "patch_failed"
    assert result.code is None and result.error
    assert path.read_text(encoding="utf-8") == SOURCE


def test_unknown_target_raises(tmp_path: Path) -> None:
    path = tmp_path / "box.py"
    path.write_text(SOURCE, encoding="utf-8")
    with pytest.raises(ValueError):
        patch_method(path, "Box", "missing", COUNT)
