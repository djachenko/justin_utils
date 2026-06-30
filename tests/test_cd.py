from pathlib import Path

import pytest

from justin_utils.cd import cd


class TestCd:
    def test_changes_directory(self, temp_dir):
        target = temp_dir / "target"
        target.mkdir()

        with cd(target):
            assert Path.cwd() == target.resolve()

    def test_restores_previous_directory_on_exit(self, temp_dir):
        target = temp_dir / "target"
        target.mkdir()
        previous = Path.cwd()

        with cd(target):
            pass

        assert Path.cwd() == previous

    def test_restores_previous_directory_on_exception(self, temp_dir):
        target = temp_dir / "target"
        target.mkdir()
        previous = Path.cwd()

        with pytest.raises(ValueError):
            with cd(target):
                raise ValueError("boom")

        assert Path.cwd() == previous

    def test_missing_path_raises(self, temp_dir):
        with pytest.raises(AssertionError):
            with cd(temp_dir / "missing"):
                pass

    def test_file_path_raises(self, temp_dir):
        file_path = temp_dir / "file.txt"
        file_path.touch()

        with pytest.raises(AssertionError):
            with cd(file_path):
                pass
