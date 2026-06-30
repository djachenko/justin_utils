from pathlib import Path

import pytest

from justin_utils.filesystem import Folder


class TestGetByPath:
    @pytest.mark.parametrize("structure, lookup, expected_name", [
        ({"a": {"file.txt": "x"}}, "a", "a"),
        ({"a": {"b": {"file.txt": "x"}}}, "a/b", "b"),
        ({"a": {"b": {"c": {"file.txt": "x"}}}}, "a/b/c", "c"),
    ])
    def test_existing_path_returns_folder(self, temp_dir, create_files, structure, lookup, expected_name):
        create_files(temp_dir, structure)
        folder = Folder(temp_dir)

        result = folder[Path(lookup)]

        assert result is not None
        assert result.name == expected_name

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
    @pytest.mark.parametrize("structure, expected_path", [
        ({"file.txt": "content"}, ("file.txt",)),
        ({"sub": {"file.txt": "content"}}, ("sub", "file.txt")),
    ])
    def test_merge_into_moves_contents(self, temp_dir, create_files, structure, expected_path):
        create_files(temp_dir, {"source": structure, "target": {}})
        source = Folder(temp_dir / "source")
        target = temp_dir / "target"

        source.merge_into(target)

        assert target.joinpath(*expected_path).exists()

    def test_merge_into_updates_path(self, temp_dir, create_files):
        create_files(temp_dir, {"source": {"file.txt": "content"}, "target": {}})
        source = Folder(temp_dir / "source")
        target = temp_dir / "target"

        source.merge_into(target)

        assert source.path == target
