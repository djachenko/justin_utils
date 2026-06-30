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

    @pytest.mark.parametrize("create_as_file", [False, True])
    def test_invalid_path_raises(self, temp_dir, create_as_file):
        path = temp_dir / "target"

        if create_as_file:
            path.touch()

        with pytest.raises(AssertionError):
            with cd(path):
                pass
