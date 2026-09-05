from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

import pytest

from justin_utils.dictable import (
    Dictable,
    DictableDataclass,
    DictableError,
    fromdict,
    frompath,
)

MOMENT = "2026-03-01T12:00:00"
SENTINEL = datetime.fromisoformat("1999-01-01T00:00:00")


@dataclass
class Leaf(DictableDataclass):
    name: str


@dataclass
class Node(DictableDataclass):
    title: str
    leaf: Leaf
    count: int = 0
    tags: list[str] = field(default_factory=list)
    leaves: list[Leaf] = field(default_factory=list)
    optional: str | None = None


@dataclass
class Optionals(DictableDataclass):
    nickname: str | None
    defaulted: str | None = None


@dataclass
class Untimed(DictableDataclass):
    moment: datetime


@dataclass
class Timed(DictableDataclass):
    moment: datetime

    @classmethod
    def rules(cls) -> dict[type, Callable]:
        return {datetime: datetime.fromisoformat}


@dataclass
class PlainOuter(DictableDataclass):
    inner: Untimed


@dataclass
class RulingOuter(DictableDataclass):
    inner: Untimed

    @classmethod
    def rules(cls) -> dict[type, Callable]:
        return {datetime: datetime.fromisoformat}


class Color:
    def __init__(self, value: str) -> None:
        self.value = value


class NamedColor(Color):
    pass


@dataclass
class Painted(DictableDataclass):
    color: NamedColor


class TestScalars:
    def test_plain_fields(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}, "count": 5})

        assert node.title == "t"
        assert node.count == 5

    def test_coerces_type(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}, "count": "7"})

        assert node.count == 7

    @pytest.mark.parametrize("payload, expected", [
        ({"name": "a"}, "a"),
        ({"name": 1}, "1"),
    ])
    def test_scalar_coercion(self, payload, expected):
        assert Leaf.from_dict(payload).name == expected

    def test_optional_present_and_absent(self):
        assert Node.from_dict({"title": "t", "leaf": {"name": "l"}, "optional": "x"}).optional == "x"
        assert Node.from_dict({"title": "t", "leaf": {"name": "l"}}).optional is None


class TestNested:
    def test_nested_dictable(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "deep"}})

        assert isinstance(node.leaf, Leaf)
        assert node.leaf.name == "deep"

    def test_list_of_scalars(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}, "tags": ["a", "b"]})

        assert node.tags == ["a", "b"]

    def test_list_of_dictables(self):
        node = Node.from_dict({
            "title": "t",
            "leaf": {"name": "l"},
            "leaves": [{"name": "one"}, {"name": "two"}],
        })

        assert [leaf.name for leaf in node.leaves] == ["one", "two"]
        assert all(isinstance(leaf, Leaf) for leaf in node.leaves)


class TestMissingFields:
    def test_missing_without_default_raises(self):
        with pytest.raises(DictableError):
            Leaf.from_dict({})

    def test_missing_one_of_several_raises(self):
        with pytest.raises(DictableError):
            Node.from_dict({"title": "t"})

    def test_missing_with_plain_default_uses_default(self):
        assert Node.from_dict({"title": "t", "leaf": {"name": "l"}}).count == 0

    def test_missing_with_factory_uses_factory(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}})

        assert node.tags == []
        assert node.leaves == []

    def test_factory_returns_fresh_instance(self):
        first = Node.from_dict({"title": "t", "leaf": {"name": "l"}})
        second = Node.from_dict({"title": "t", "leaf": {"name": "l"}})

        first.tags.append("mutated")

        assert second.tags == []

    def test_optional_type_without_default_is_still_required(self):
        with pytest.raises(DictableError):
            Optionals.from_dict({})

    def test_none_default_counts_as_a_default(self):
        assert Optionals.from_dict({"nickname": "n"}).defaulted is None


class TestNulls:
    def test_null_into_optional_field_is_none(self):
        assert Optionals.from_dict({"nickname": None}).nickname is None

    def test_null_into_required_field_raises(self):
        with pytest.raises(DictableError):
            Leaf.from_dict({"name": None})

    def test_null_is_not_replaced_by_default(self):
        with pytest.raises(DictableError):
            Node.from_dict({"title": "t", "leaf": {"name": "l"}, "count": None})


class TestConversion:
    def test_conversion_failure_raises(self):
        with pytest.raises(DictableError):
            Node.from_dict({"title": "t", "leaf": {"name": "l"}, "count": "not a number"})

    def test_conversion_failure_does_not_fall_back_to_default(self):
        with pytest.raises(DictableError):
            Node.from_dict({"title": "t", "leaf": {"name": "l"}, "tags": 42})

    def test_wrong_shape_for_nested_dictable_raises(self):
        with pytest.raises(DictableError):
            Node.from_dict({"title": "t", "leaf": "not an object"})

    def test_non_object_payload_raises(self):
        with pytest.raises(DictableError):
            Leaf.from_dict([])


class TestErrorPath:
    def test_top_level_field(self):
        with pytest.raises(DictableError) as info:
            Node.from_dict({"title": "t"})

        assert info.value.path == "Node.leaf"

    def test_nested_field(self):
        with pytest.raises(DictableError) as info:
            Node.from_dict({"title": "t", "leaf": {}})

        assert info.value.path == "Node.leaf.name"

    def test_list_index(self):
        with pytest.raises(DictableError) as info:
            Node.from_dict({"title": "t", "leaf": {"name": "l"}, "leaves": [{"name": "a"}, {}]})

        assert info.value.path == "Node.leaves[1].name"

    def test_message_contains_path(self):
        with pytest.raises(DictableError) as info:
            Node.from_dict({"title": "t", "leaf": {}})

        assert "Node.leaf.name" in str(info.value)


class TestRuleResolution:
    def test_rule_applied(self):
        assert Timed.from_dict({"moment": MOMENT}).moment == datetime.fromisoformat(MOMENT)

    def test_from_dict_needs_no_explicit_rules(self):
        assert Timed.from_dict({"moment": MOMENT}).moment == datetime.fromisoformat(MOMENT)

    def test_rule_for_base_class_applies_to_subclass(self):
        painted = fromdict({"color": "red"}, Painted, {Color: lambda v: NamedColor(f"rule:{v}")})

        assert painted.color.value == "rule:red"

    def test_without_rule_falls_back_to_constructor(self):
        assert fromdict({"color": "red"}, Painted).color.value == "red"

    def test_class_rules_win_over_param_rules(self):
        timed = fromdict({"moment": MOMENT}, Timed, {datetime: lambda _: SENTINEL})

        assert timed.moment == datetime.fromisoformat(MOMENT)

    def test_param_rules_apply_where_class_declares_none(self):
        untimed = fromdict({"moment": MOMENT}, Untimed, {datetime: datetime.fromisoformat})

        assert untimed.moment == datetime.fromisoformat(MOMENT)


class TestRulePropagation:
    def test_param_rules_reach_nested_classes(self):
        outer = fromdict({"inner": {"moment": MOMENT}}, PlainOuter, {datetime: datetime.fromisoformat})

        assert outer.inner.moment == datetime.fromisoformat(MOMENT)

    def test_class_rules_do_not_leak_into_nested(self):
        with pytest.raises(DictableError):
            RulingOuter.from_dict({"inner": {"moment": MOMENT}})

    def test_param_rules_survive_a_class_that_overrides_them(self):
        @dataclass
        class Mixed(DictableDataclass):
            timed: Timed
            untimed: Untimed

        mixed = fromdict(
            {"timed": {"moment": MOMENT}, "untimed": {"moment": MOMENT}},
            Mixed,
            {datetime: datetime.fromisoformat},
        )

        assert mixed.timed.moment == mixed.untimed.moment


class TestLogging:
    def test_default_substitution_logs_path(self, caplog):
        with caplog.at_level("DEBUG", logger="justin_utils.dictable"):
            Node.from_dict({"title": "t", "leaf": {"name": "l"}})

        assert "Node.count" in caplog.text

    def test_clean_payload_is_quiet(self, caplog):
        with caplog.at_level("DEBUG", logger="justin_utils.dictable"):
            Leaf.from_dict({"name": "l"})

        assert caplog.text == ""


class TestAbstract:
    def test_dictable_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Dictable()

    def test_subclass_without_as_dict_cannot_be_instantiated(self):
        @dataclass
        class NoAsDict(Dictable):
            value: int = 0

        with pytest.raises(TypeError):
            NoAsDict()

    def test_non_dataclass_as_dict_raises(self):
        class NotADataclass(DictableDataclass):
            pass

        with pytest.raises(TypeError):
            NotADataclass().as_dict()

    def test_frozen_subclass_is_allowed(self):
        @dataclass(frozen=True)
        class Frozen(DictableDataclass):
            name: str

        assert Frozen.from_dict({"name": "f"}).as_dict() == {"name": "f"}


class TestAsDict:
    def test_roundtrip(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}, "count": 3})

        assert node.as_dict()["title"] == "t"
        assert node.as_dict()["count"] == 3


class TestFromdictFunction:
    def test_works_on_plain_dataclass(self):
        @dataclass
        class Plain:
            value: int = 0

        assert fromdict({"value": "9"}, Plain).value == 9

    @pytest.mark.parametrize("payload, expected", [
        ({"name": "a"}, "a"),
        ({"name": 1}, "1"),
    ])
    def test_scalar_coercion(self, payload, expected):
        assert Leaf.from_dict(payload).name == expected

    def test_plain_dataclass_is_strict_too(self):
        @dataclass
        class Plain:
            value: int

        with pytest.raises(DictableError):
            fromdict({}, Plain)

    def test_rules_apply_to_plain_dataclass(self):
        @dataclass
        class Plain:
            moment: datetime

        parsed = fromdict({"moment": MOMENT}, Plain, {datetime: datetime.fromisoformat})

        assert parsed.moment == datetime.fromisoformat(MOMENT)


class TestFrompath:
    def test_missing_file_raises(self, temp_dir):
        with pytest.raises(FileNotFoundError):
            frompath(temp_dir / "absent.json", Leaf)

    def test_directory_raises(self, temp_dir):
        with pytest.raises(IsADirectoryError):
            frompath(temp_dir, Leaf)

    def test_reads_object(self, temp_dir, create_files):
        create_files(temp_dir, {"leaf.json": '{"name": "from file"}'})

        assert frompath(temp_dir / "leaf.json", Leaf).name == "from file"

    def test_decode_error_propagates(self, temp_dir, create_files):
        create_files(temp_dir, {"leaf.json": "{}"})

        with pytest.raises(DictableError):
            frompath(temp_dir / "leaf.json", Leaf)

    def test_broken_json_names_the_file(self, temp_dir, create_files):
        create_files(temp_dir, {"broken.json": "{"})
        broken = temp_dir / "broken.json"

        with pytest.raises(DictableError) as info:
            frompath(broken, Leaf)

        assert info.value.path == str(broken)
        assert str(broken) in str(info.value)
        assert "invalid json" in info.value.message

    def test_binary_file_names_the_file(self, temp_dir, create_files):
        create_files(temp_dir, {"._leaf.json": b"\x00\x05\x16\x07\xff\xfe"})
        apple_double = temp_dir / "._leaf.json"

        with pytest.raises(DictableError) as info:
            frompath(apple_double, Leaf)

        assert info.value.path == str(apple_double)
        assert "invalid json" in info.value.message

    def test_structure_mismatch_names_the_file(self, temp_dir, create_files):
        create_files(temp_dir, {"leaf.json": "{}"})
        leaf = temp_dir / "leaf.json"

        with pytest.raises(DictableError) as info:
            frompath(leaf, Leaf)

        assert info.value.path == f"{leaf} \u2192 Leaf.name"

    def test_field_message_survives_wrapping(self, temp_dir, create_files):
        create_files(temp_dir, {"leaf.json": "{}"})
        leaf = temp_dir / "leaf.json"

        with pytest.raises(DictableError) as info:
            frompath(leaf, Leaf)

        assert info.value.message == "field is missing and has no default"
        assert str(leaf) in str(info.value)
        assert "Leaf.name" in str(info.value)
        assert "field is missing and has no default" in str(info.value)

    def test_nested_path_survives_wrapping(self, temp_dir, create_files):
        create_files(temp_dir, {"node.json": '{"title": "t", "leaf": {}}'})
        node = temp_dir / "node.json"

        with pytest.raises(DictableError) as info:
            frompath(node, Node)

        assert info.value.path == f"{node} \u2192 Node.leaf.name"

    def test_rules_are_applied(self, temp_dir, create_files):
        create_files(temp_dir, {"timed.json": f'{{"moment": "{MOMENT}"}}'})

        assert frompath(temp_dir / "timed.json", Timed).moment == datetime.fromisoformat(MOMENT)
