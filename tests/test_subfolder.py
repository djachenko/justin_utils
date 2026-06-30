import sys

import pytest

from justin_utils import subfolder
from justin_utils.cd import cd


def _run(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["sf", *argv])

    subfolder.__run()


class TestRun:
    @pytest.mark.parametrize("argv_pattern, b_log_moved", [
        ([], True),  # default pattern "*" matches everything
        (["*.txt"], False),
    ])
    def test_moves_matching_files(self, temp_dir, monkeypatch, argv_pattern, b_log_moved):
        (temp_dir / "a.txt").touch()
        (temp_dir / "b.log").touch()

        with cd(temp_dir):
            _run(monkeypatch, ["archive", *argv_pattern])

        assert (temp_dir / "archive" / "a.txt").exists()
        assert not (temp_dir / "a.txt").exists()
        assert (temp_dir / "archive" / "b.log").exists() == b_log_moved
        assert (temp_dir / "b.log").exists() == (not b_log_moved)

    def test_creates_subfolder_if_missing(self, temp_dir, monkeypatch):
        (temp_dir / "a.txt").touch()

        with cd(temp_dir):
            _run(monkeypatch, ["new_folder"])

        assert (temp_dir / "new_folder").is_dir()

    def test_no_matches_is_noop(self, temp_dir, monkeypatch):
        with cd(temp_dir):
            _run(monkeypatch, ["archive", "*.missing"])

        assert not (temp_dir / "archive").exists()

    def test_missing_name_argument_raises(self, temp_dir, monkeypatch):
        with cd(temp_dir), pytest.raises(SystemExit):
            _run(monkeypatch, [])
