from pathlib import Path

import pytest

from justin_utils.testing import CreateFiles


class TestCreateFiles:
    @pytest.mark.parametrize("value, expected", [
        (None, b""),
        ("content", b"content"),
        (b"\x00\xff", b"\x00\xff"),
    ])
    def test_file_content(
            self,
            tmp_path: Path,
            create_files: CreateFiles,
            value: str | bytes | None,
            expected: bytes,
    ) -> None:
        file_name = "file"

        create_files(tmp_path, {
            file_name: value,
        })

        assert (tmp_path / file_name).read_bytes() == expected

    def test_empty_dict_creates_empty_folder(self, tmp_path: Path, create_files: CreateFiles) -> None:
        folder_name = "folder"
        folder_path = tmp_path / folder_name

        create_files(tmp_path, {
            folder_name: {},
        })

        assert folder_path.is_dir()
        assert not any(folder_path.iterdir())

    def test_nested_dicts_create_tree(self, tmp_path: Path, create_files: CreateFiles) -> None:
        create_files(tmp_path, {
            "a": {
                "b": {
                    "c.txt": "deep",
                },
                "d.txt": None,
            },
        })

        assert (tmp_path / "a" / "b" / "c.txt").read_text() == "deep"
        assert (tmp_path / "a" / "d.txt").is_file()

    def test_existing_folder_is_reused(self, tmp_path: Path, create_files: CreateFiles) -> None:
        folder_name = "folder"
        folder_path = tmp_path / folder_name

        folder_path.mkdir()
        (folder_path / "old.txt").touch()

        create_files(tmp_path, {
            folder_name: {
                "new.txt": None,
            },
        })

        assert {item.name for item in folder_path.iterdir()} == {
            "old.txt",
            "new.txt",
        }
