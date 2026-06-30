from pathlib import Path

import pytest


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def create_files():
    def _create(root: Path, structure: dict) -> None:
        for key, value in structure.items():
            new_path = root / key

            if value is None:
                new_path.touch()
            elif isinstance(value, str):
                new_path.write_text(value)
            elif isinstance(value, dict):
                new_path.mkdir(parents=True, exist_ok=True)

                _create(new_path, value)

    return _create
