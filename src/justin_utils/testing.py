from collections.abc import Callable
from pathlib import Path

import pytest

FileTree = dict[str, "FileTree | str | bytes | None"]
CreateFiles = Callable[[Path, FileTree], None]


@pytest.fixture
def create_files() -> CreateFiles:
    def _create(root: Path, structure: FileTree) -> None:
        for key, value in structure.items():
            new_path = root / key

            if value is None:
                new_path.touch()
            elif isinstance(value, str):
                new_path.write_text(value)
            elif isinstance(value, bytes):
                new_path.write_bytes(value)
            elif isinstance(value, dict):
                new_path.mkdir(parents=True, exist_ok=True)

                _create(new_path, value)

    return _create
