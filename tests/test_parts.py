from pathlib import Path

import pytest
from typer.testing import CliRunner

from justin_utils.cd import cd
from justin_utils.parts import Part, app, index_length, make, new_part_name, offset, renumber, to_padded_string

runner = CliRunner()


# --- helper functions ---

def test_to_padded_string_pads_with_zeros():
    assert to_padded_string(3, 3, "0") == "003"


def test_to_padded_string_no_padding_needed():
    assert to_padded_string(123, 2, "0") == "123"


def test_index_length_zero():
    assert index_length(0) == 1


def test_index_length_single_digit():
    assert index_length(9) == 1


def test_index_length_multi_digit():
    assert index_length(100) == 3


def test_part_is_part_true():
    assert Part.is_part(Path("3.name"))


def test_part_is_part_false():
    assert not Part.is_part(Path("name"))


def test_part_from_path_with_name():
    part = Part.from_path(Path("3.intro"))
    assert part.index == 3
    assert part.name == "intro"


def test_part_from_path_without_name():
    part = Part.from_path(Path("3"))
    assert part.index == 3
    assert part.name is None


def test_new_part_name_with_name():
    part = Part(index=1, name="intro", path=Path("1.intro"))
    assert new_part_name(part, 2, 2) == "02.intro"


def test_new_part_name_without_name():
    part = Part(index=1, name=None, path=Path("1"))
    assert new_part_name(part, 2, 2) == "02"


# --- make: direct calls ---

def test_make_creates_numbered_folders(tmp_path):
    make(3, root=[str(tmp_path)])
    assert sorted(p.name for p in tmp_path.iterdir()) == ["1", "2", "3"]


def test_make_skips_existing_indices(tmp_path):
    (tmp_path / "2").mkdir()
    make(3, root=[str(tmp_path)])
    assert sorted(p.name for p in tmp_path.iterdir()) == ["1", "2", "3"]


def test_make_default_root_uses_cwd(tmp_path):
    with cd(tmp_path):
        make(2, root=["."])
    assert sorted(p.name for p in tmp_path.iterdir()) == ["1", "2"]


def test_make_multiple_roots(tmp_path):
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    root_a.mkdir()
    root_b.mkdir()

    make(2, root=[str(root_a), str(root_b)])

    assert sorted(p.name for p in root_a.iterdir()) == ["1", "2"]
    assert sorted(p.name for p in root_b.iterdir()) == ["1", "2"]


# --- renumber: direct calls ---

def test_renumber_resequences_with_gaps(tmp_path):
    (tmp_path / "1.intro").mkdir()
    (tmp_path / "5.outro").mkdir()

    renumber(root=[str(tmp_path)], width=None)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["1.intro", "2.outro"]


def test_renumber_width_option(tmp_path):
    (tmp_path / "1").mkdir()
    (tmp_path / "2").mkdir()

    renumber(root=[str(tmp_path)], width=3)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["001", "002"]


def test_renumber_single_part_flattens(tmp_path):
    only_part = tmp_path / "1.only"
    only_part.mkdir()
    (only_part / "file.txt").write_text("hi")

    renumber(root=[str(tmp_path)], width=None)

    assert (tmp_path / "file.txt").read_text() == "hi"
    # known bug: the now-empty original folder is left behind, see backlog
    assert only_part.exists()
    assert list(only_part.iterdir()) == []


# --- offset: direct calls ---

def test_offset_shifts_indices(tmp_path):
    (tmp_path / "1").mkdir()
    (tmp_path / "2").mkdir()

    offset(5, root=[str(tmp_path)], width=None)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["6", "7"]


def test_offset_width_option(tmp_path):
    (tmp_path / "1").mkdir()

    offset(0, root=[str(tmp_path)], width=3)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["001"]


def test_offset_negative_below_zero_raises(tmp_path):
    (tmp_path / "1").mkdir()

    with pytest.raises(AssertionError):
        offset(-2, root=[str(tmp_path)], width=None)


def test_offset_no_parts_is_noop(tmp_path):
    offset(5, root=[str(tmp_path)], width=None)

    assert list(tmp_path.iterdir()) == []


# --- CLI-level tests ---

def test_cli_make(tmp_path):
    result = runner.invoke(app, ["make", "3", str(tmp_path)])

    assert result.exit_code == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["1", "2", "3"]


def test_cli_offset_with_width(tmp_path):
    (tmp_path / "1").mkdir()

    result = runner.invoke(app, ["offset", "0", str(tmp_path), "-w", "3"])

    assert result.exit_code == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["001"]


def test_cli_renumber_default_root(tmp_path):
    (tmp_path / "1").mkdir()
    (tmp_path / "5").mkdir()

    with cd(tmp_path):
        result = runner.invoke(app, ["renumber"])

    assert result.exit_code == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["1", "2"]
