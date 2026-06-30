import sys

import pytest

from justin_utils import subfolder
from justin_utils.cd import cd


def _run(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", ["sf", *argv])

    subfolder.__run()


class TestRun:
    def test_moves_default_pattern_matches(self, temp_dir, monkeypatch):
        (temp_dir / "a.txt").touch()
        (temp_dir / "b.txt").touch()

        with cd(temp_dir):
            _run(monkeypatch, ["archive"])

        assert (temp_dir / "archive" / "a.txt").exists()
        assert (temp_dir / "archive" / "b.txt").exists()
        assert not (temp_dir / "a.txt").exists()

    def test_moves_only_matching_pattern(self, temp_dir, monkeypatch):
        (temp_dir / "a.txt").touch()
        (temp_dir / "b.log").touch()

        with cd(temp_dir):
            _run(monkeypatch, ["archive", "*.txt"])

        assert (temp_dir / "archive" / "a.txt").exists()
        assert (temp_dir / "b.log").exists()
        assert not (temp_dir / "archive" / "b.log").exists()

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
