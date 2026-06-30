from pathlib import Path

import pytest

from justin_utils.filesystem import Folder

FileTree = dict[str, "FileTree | str | None"]


def _nested(names: list[str], leaf: FileTree | str) -> FileTree:
    structure: FileTree = {names[-1]: leaf}

    for name in reversed(names[:-1]):
        structure = {name: structure}

    return structure


class TestGetByPath:
    @pytest.mark.parametrize("names", [
        ["a"],
        ["a", "b"],
        ["a", "b", "c"],
    ])
    def test_existing_path_returns_folder(self, temp_dir, create_files, names):
        create_files(temp_dir, _nested(names, {"file.txt": "x"}))
        folder = Folder(temp_dir)

        result = folder[Path("/".join(names))]

        assert result is not None
        assert result.name == names[-1]

    @pytest.mark.parametrize("lookup", [
        "a/nonexistent",
        "z",
    ])
    def test_missing_path_returns_none(self, temp_dir, create_files, lookup):
        create_files(temp_dir, {"a": {"file.txt": "x"}})
        folder = Folder(temp_dir)

        result = folder[Path(lookup)]

        assert result is None


class TestMergeInto:
    @pytest.mark.parametrize("path_parts", [
        ("file.txt",),
        ("sub", "file.txt"),
    ])
    def test_merge_into_moves_contents(self, temp_dir, create_files, path_parts):
        create_files(temp_dir, {"source": _nested(list(path_parts), "content"), "target": {}})
        source = Folder(temp_dir / "source")
        target = temp_dir / "target"

        source.merge_into(target)

        assert target.joinpath(*path_parts).exists()

    def test_merge_into_updates_path(self, temp_dir, create_files):
        create_files(temp_dir, {"source": {"file.txt": "content"}, "target": {}})
        source = Folder(temp_dir / "source")
        target = temp_dir / "target"

        source.merge_into(target)

        assert source.path == target
