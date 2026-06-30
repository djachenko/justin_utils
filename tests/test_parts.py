from pathlib import Path

import pytest
from typer.testing import CliRunner

from justin_utils.cd import cd
from justin_utils.parts import Part, app, index_length, make, new_part_name, offset, renumber, to_padded_string

runner = CliRunner()


class TestPaddedString:
    @pytest.mark.parametrize("number, length, expected", [
        (3, 3, "003"),
        (123, 2, "123"),
        (1, 1, "1"),
        (100, 3, "100"),
    ])
    def test_to_padded_string(self, number, length, expected):
        assert to_padded_string(number, length, "0") == expected


class TestIndexLength:
    @pytest.mark.parametrize("index, expected", [
        (0, 1),
        (9, 1),
        (10, 2),
        (100, 3),
    ])
    def test_index_length(self, index, expected):
        assert index_length(index) == expected


class TestPartIsPart:
    @pytest.mark.parametrize("name, expected", [
        ("3.name", True),
        ("name", False),
    ])
    def test_is_part(self, name, expected):
        assert Part.is_part(Path(name)) == expected


class TestPartFromPath:
    @pytest.mark.parametrize("name, expected_index, expected_name", [
        ("3.intro", 3, "intro"),
        ("3", 3, None),
    ])
    def test_from_path(self, name, expected_index, expected_name):
        part = Part.from_path(Path(name))

        assert part.index == expected_index
        assert part.name == expected_name


class TestNewPartName:
    @pytest.mark.parametrize("name, expected", [
        ("intro", "02.intro"),
        (None, "02"),
    ])
    def test_new_part_name(self, name, expected):
        part = Part(index=1, name=name, path=Path(f"1.{name}" if name else "1"))

        assert new_part_name(part, 2, 2) == expected


class TestMake:
    @pytest.mark.parametrize("pre_existing", [None, "2"])
    def test_creates_numbered_folders(self, temp_dir, pre_existing):
        if pre_existing:
            (temp_dir / pre_existing).mkdir()

        make(3, root=[str(temp_dir)])

        assert sorted(p.name for p in temp_dir.iterdir()) == ["1", "2", "3"]

    def test_default_root_uses_cwd(self, temp_dir):
        with cd(temp_dir):
            make(2, root=["."])

        assert sorted(p.name for p in temp_dir.iterdir()) == ["1", "2"]

    def test_multiple_roots(self, temp_dir):
        root_a = temp_dir / "a"
        root_b = temp_dir / "b"
        root_a.mkdir()
        root_b.mkdir()

        make(2, root=[str(root_a), str(root_b)])

        assert sorted(p.name for p in root_a.iterdir()) == ["1", "2"]
        assert sorted(p.name for p in root_b.iterdir()) == ["1", "2"]


class TestRenumber:
    def test_resequences_with_gaps(self, temp_dir):
        first_name, second_name = "intro", "outro"

        (temp_dir / f"1.{first_name}").mkdir()
        (temp_dir / f"5.{second_name}").mkdir()

        renumber(root=[str(temp_dir)], width=None)

        assert sorted(p.name for p in temp_dir.iterdir()) == [f"1.{first_name}", f"2.{second_name}"]

    def test_width_option(self, temp_dir):
        (temp_dir / "1").mkdir()
        (temp_dir / "2").mkdir()

        renumber(root=[str(temp_dir)], width=3)

        assert sorted(p.name for p in temp_dir.iterdir()) == ["001", "002"]

    def test_single_part_flattens(self, temp_dir):
        only_part = temp_dir / "1.only"
        only_part.mkdir()
        (only_part / "file.txt").write_text("hi")

        renumber(root=[str(temp_dir)], width=None)

        assert (temp_dir / "file.txt").read_text() == "hi"
        assert not only_part.exists()


class TestOffset:
    def test_shifts_indices(self, temp_dir):
        (temp_dir / "1").mkdir()
        (temp_dir / "2").mkdir()

        offset(5, root=[str(temp_dir)], width=None)

        assert sorted(p.name for p in temp_dir.iterdir()) == ["6", "7"]

    def test_width_option(self, temp_dir):
        (temp_dir / "1").mkdir()

        offset(0, root=[str(temp_dir)], width=3)

        assert sorted(p.name for p in temp_dir.iterdir()) == ["001"]

    def test_negative_below_zero_raises(self, temp_dir):
        (temp_dir / "1").mkdir()

        with pytest.raises(AssertionError):
            offset(-2, root=[str(temp_dir)], width=None)

    def test_no_parts_is_noop(self, temp_dir):
        offset(5, root=[str(temp_dir)], width=None)

        assert list(temp_dir.iterdir()) == []


class TestCli:
    def test_make(self, temp_dir):
        result = runner.invoke(app, ["make", "3", str(temp_dir)])

        assert result.exit_code == 0
        assert sorted(p.name for p in temp_dir.iterdir()) == ["1", "2", "3"]

    def test_offset_with_width(self, temp_dir):
        (temp_dir / "1").mkdir()

        result = runner.invoke(app, ["offset", "0", str(temp_dir), "-w", "3"])

        assert result.exit_code == 0
        assert sorted(p.name for p in temp_dir.iterdir()) == ["001"]

    def test_renumber_default_root(self, temp_dir):
        (temp_dir / "1").mkdir()
        (temp_dir / "5").mkdir()

        with cd(temp_dir):
            result = runner.invoke(app, ["renumber"])

        assert result.exit_code == 0
        assert sorted(p.name for p in temp_dir.iterdir()) == ["1", "2"]
