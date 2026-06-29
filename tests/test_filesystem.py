from pathlib import Path

import pytest

from justin_utils.filesystem import Folder


def make_folder(tmp_path: Path, structure: dict) -> Path:
    """Recursively create a directory structure. Values are file contents (str) or nested dicts."""
    for name, content in structure.items():
        child = tmp_path / name
        if isinstance(content, dict):
            child.mkdir()
            make_folder(child, content)
        else:
            child.write_text(content)
    return tmp_path


# region Folder.__get_by_path

def test_get_by_path_single_component(tmp_path):
    make_folder(tmp_path, {"a": {"file.txt": "x"}})
    folder = Folder(tmp_path)
    result = folder[Path("a")]
    assert result is not None
    assert result.name == "a"


def test_get_by_path_two_levels(tmp_path):
    make_folder(tmp_path, {"a": {"b": {"file.txt": "x"}}})
    folder = Folder(tmp_path)
    result = folder[Path("a/b")]
    assert result is not None
    assert result.name == "b"


def test_get_by_path_three_levels(tmp_path):
    make_folder(tmp_path, {"a": {"b": {"c": {"file.txt": "x"}}}})
    folder = Folder(tmp_path)
    result = folder[Path("a/b/c")]
    assert result is not None
    assert result.name == "c"


def test_get_by_path_missing_returns_none(tmp_path):
    make_folder(tmp_path, {"a": {"file.txt": "x"}})
    folder = Folder(tmp_path)
    result = folder[Path("a/nonexistent")]
    assert result is None


def test_get_by_path_missing_root_returns_none(tmp_path):
    make_folder(tmp_path, {"a": {"file.txt": "x"}})
    folder = Folder(tmp_path)
    result = folder[Path("z")]
    assert result is None


# endregion

# region Folder.merge_into

def test_merge_into_moves_files(tmp_path):
    make_folder(tmp_path, {
        "source": {"file.txt": "content"},
        "target": {},
    })
    source = Folder(tmp_path / "source")
    target = tmp_path / "target"

    source.merge_into(target)

    assert (target / "file.txt").exists()


def test_merge_into_updates_path(tmp_path):
    make_folder(tmp_path, {
        "source": {"file.txt": "content"},
        "target": {},
    })
    source = Folder(tmp_path / "source")
    target = tmp_path / "target"

    source.merge_into(target)

    assert source.path == target


def test_merge_into_moves_subfolders(tmp_path):
    make_folder(tmp_path, {
        "source": {"sub": {"file.txt": "content"}},
        "target": {},
    })
    source = Folder(tmp_path / "source")
    target = tmp_path / "target"

    source.merge_into(target)

    assert (target / "sub" / "file.txt").exists()


# endregion
