import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

import pytest

from justin_utils.dictable import (
    Dictable,
    DictableDataclass,
    DictableError,
    fromdict,
    frompath,
)

MOMENT = "2026-03-01T12:00:00"


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
class PlainOuter(DictableDataclass):
    inner: Untimed
    inners: list[Untimed] = field(default_factory=list)


@dataclass
class Stamped(DictableDataclass):
    moment: Annotated[datetime, datetime.fromisoformat]
    history: list[Annotated[datetime, datetime.fromisoformat]] = field(default_factory=list)


@dataclass
class Enveloped(DictableDataclass):
    value: int
    moment: datetime | None = None

    @classmethod
    def from_dict(cls, json_object, rules=None):
        return fromdict(json_object["envelope"], cls, rules)


@dataclass
class EnvelopedOuter(DictableDataclass):
    inner: Enveloped
    items: list[Enveloped] = field(default_factory=list)


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

    def test_tuple_of_scalars(self):
        @dataclass
        class Pair:
            values: tuple[int, ...]

        assert fromdict({"values": ["1", "2"]}, Pair).values == (1, 2)

    def test_bare_list_keeps_items_as_is(self):
        @dataclass
        class Bag:
            items: list

        assert fromdict({"items": [1, {"a": 2}]}, Bag).items == [1, {"a": 2}]

    def test_any_field_keeps_value_as_is(self):
        @dataclass
        class Loose:
            payload: Any

        assert fromdict({"payload": {"a": [1]}}, Loose).payload == {"a": [1]}

    def test_optional_nested_dictable(self):
        @dataclass
        class MaybeLeaf(DictableDataclass):
            leaf: Leaf | None

        assert MaybeLeaf.from_dict({"leaf": {"name": "l"}}).leaf == Leaf(name="l")

    def test_extra_keys_are_ignored(self):
        assert Leaf.from_dict({"name": "l", "unknown": 1}) == Leaf(name="l")


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

    def test_string_for_list_raises(self):
        with pytest.raises(DictableError):
            Node.from_dict({"title": "t", "leaf": {"name": "l"}, "tags": "ab"})

    def test_union_of_several_types_raises(self):
        @dataclass
        class Either:
            value: int | str

        with pytest.raises(DictableError):
            fromdict({"value": "1"}, Either)


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

    def test_nested_list_index(self):
        @dataclass
        class Grid:
            rows: list[list[int]]

        with pytest.raises(DictableError) as info:
            fromdict({"rows": [[1], [2, "x"]]}, Grid)

        assert info.value.path == "Grid.rows[1][1]"

    def test_nested_plain_dataclass(self):
        @dataclass
        class Inner:
            value: int

        @dataclass
        class Outer:
            inner: Inner

        with pytest.raises(DictableError) as info:
            fromdict({"inner": {}}, Outer)

        assert info.value.path == "Outer.inner.value"

    def test_rule_failure(self):
        with pytest.raises(DictableError) as info:
            fromdict({"moment": "garbage"}, Untimed, {datetime: datetime.fromisoformat})

        assert info.value.path == "Untimed.moment"

    def test_parser_failure_inside_list(self):
        with pytest.raises(DictableError) as info:
            Stamped.from_dict({"moment": MOMENT, "history": [MOMENT, "garbage"]})

        assert info.value.path == "Stamped.history[1]"


class TestRuleResolution:
    def test_rule_applied(self):
        untimed = fromdict({"moment": MOMENT}, Untimed, {datetime: datetime.fromisoformat})

        assert untimed.moment == datetime.fromisoformat(MOMENT)

    def test_from_dict_passes_rules(self):
        untimed = Untimed.from_dict({"moment": MOMENT}, {datetime: datetime.fromisoformat})

        assert untimed.moment == datetime.fromisoformat(MOMENT)

    def test_rule_for_base_class_applies_to_subclass(self):
        painted = fromdict({"color": "red"}, Painted, {Color: lambda v: NamedColor(f"rule:{v}")})

        assert painted.color.value == "rule:red"

    def test_without_rule_falls_back_to_constructor(self):
        assert fromdict({"color": "red"}, Painted).color.value == "red"

    def test_nearest_base_rule_wins(self):
        rules = {
            Color: lambda v: NamedColor(f"base:{v}"),
            NamedColor: lambda v: NamedColor(f"own:{v}"),
        }

        assert fromdict({"color": "red"}, Painted, rules).color.value == "own:red"

    def test_rule_for_generic_origin_is_ignored(self):
        node = fromdict(
            {"title": "t", "leaf": {"name": "l"}, "tags": ["a"]},
            Node,
            {list: lambda _: ["rule"]},
        )

        assert node.tags == ["a"]


class TestRulePropagation:
    def test_rules_reach_nested_classes(self):
        outer = fromdict({"inner": {"moment": MOMENT}}, PlainOuter, {datetime: datetime.fromisoformat})

        assert outer.inner.moment == datetime.fromisoformat(MOMENT)

    def test_rules_reach_classes_in_list(self):
        outer = PlainOuter.from_dict(
            {"inner": {"moment": MOMENT}, "inners": [{"moment": MOMENT}]},
            {datetime: datetime.fromisoformat},
        )

        assert outer.inners[0].moment == datetime.fromisoformat(MOMENT)

    def test_rules_reach_nested_plain_dataclass(self):
        @dataclass
        class Inner:
            moment: datetime

        @dataclass
        class Outer:
            inner: Inner

        outer = fromdict({"inner": {"moment": MOMENT}}, Outer, {datetime: datetime.fromisoformat})

        assert outer.inner.moment == datetime.fromisoformat(MOMENT)


class TestAnnotated:
    def test_parser_on_field(self):
        assert Stamped.from_dict({"moment": MOMENT}).moment == datetime.fromisoformat(MOMENT)

    def test_parser_inside_list(self):
        stamped = Stamped.from_dict({"moment": MOMENT, "history": [MOMENT, MOMENT]})

        assert stamped.history == [datetime.fromisoformat(MOMENT)] * 2

    def test_parser_wins_over_rule(self):
        stamped = Stamped.from_dict({"moment": MOMENT}, {datetime: lambda _: None})

        assert stamped.moment == datetime.fromisoformat(MOMENT)

    def test_parser_is_first_metadata(self):
        @dataclass
        class Documented:
            moment: Annotated[datetime, datetime.fromisoformat, "a note"]

        assert fromdict({"moment": MOMENT}, Documented).moment == datetime.fromisoformat(MOMENT)

    @pytest.mark.parametrize("field_type", [
        Annotated[datetime, datetime.fromisoformat] | None,
        Annotated[datetime | None, datetime.fromisoformat],
    ])
    @pytest.mark.parametrize("value, expected", [
        (None, None),
        (MOMENT, datetime.fromisoformat(MOMENT)),
    ])
    def test_optional_parser(self, field_type, value, expected):
        @dataclass
        class Maybe:
            moment: field_type = None

        assert fromdict({"moment": value}, Maybe).moment == expected


class TestOverride:
    def test_nested_override_is_used(self):
        outer = EnvelopedOuter.from_dict({"inner": {"envelope": {"value": 1}}})

        assert outer.inner.value == 1

    def test_rules_reach_override(self):
        outer = EnvelopedOuter.from_dict(
            {"inner": {"envelope": {"value": 1, "moment": MOMENT}}},
            {datetime: datetime.fromisoformat},
        )

        assert outer.inner.moment == datetime.fromisoformat(MOMENT)

    def test_error_path_passes_through_override(self):
        ok = {"envelope": {"value": 1}}

        with pytest.raises(DictableError) as info:
            EnvelopedOuter.from_dict({"inner": ok, "items": [ok, ok, {"envelope": {}}]})

        assert info.value.path == "EnvelopedOuter.items[2].value"


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

    def test_plain_dataclass_is_strict_too(self):
        @dataclass
        class Plain:
            value: int

        with pytest.raises(DictableError):
            fromdict({}, Plain)

    def test_nested_plain_dataclass_is_parsed(self):
        @dataclass
        class Inner:
            value: int

        @dataclass
        class Outer:
            inner: Inner

        parsed = fromdict({"inner": {"value": 1}}, Outer)

        assert parsed.inner == Inner(value=1)

    def test_nested_dataclass_keeps_own_from_dict(self):
        @dataclass
        class Inner(Dictable):
            value: int

            @classmethod
            def from_dict(cls, json_object, rules=None):
                return cls(value=json_object["raw"] * 10)

            def as_dict(self):
                return {"raw": self.value // 10}

        @dataclass
        class Outer:
            inner: Inner

        parsed = fromdict({"inner": {"raw": 1}}, Outer)

        assert parsed.inner == Inner(value=10)

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
        # IsADirectoryError on posix, PermissionError on windows
        with pytest.raises(OSError):
            frompath(temp_dir, Leaf)

    def test_reads_object(self, temp_dir, create_files):
        file_name = "leaf.json"

        create_files(
            temp_dir,
            {
                file_name: json.dumps(
                    {
                        "name": "from file",
                    },
                ),
            },
        )

        assert frompath(temp_dir / file_name, Leaf).name == "from file"

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

    @pytest.mark.parametrize(
        "content",
        [
            b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 1024,
            b"name,size\nphoto.jpg,1\n",
            b"[2026-10-15 04:34] started\n",
        ],
        ids=["binary", "utf8_text", "bracketed_log"],
    )
    def test_non_json_is_rejected_without_full_read(self, temp_dir, create_files, monkeypatch, content):
        file_name = "download"

        create_files(
            temp_dir,
            {
                file_name: content,
            },
        )

        def fail_read_text(*args, **kwargs):
            raise AssertionError("whole file was read")

        monkeypatch.setattr(Path, "read_text", fail_read_text)

        with pytest.raises(DictableError) as info:
            frompath(temp_dir / file_name, Leaf)

        assert "invalid json" in info.value.message

    def test_leading_whitespace_is_allowed(self, temp_dir, create_files):
        file_name = "leaf.json"

        create_files(
            temp_dir,
            {
                file_name: '\n \t{"name": "indented"}',
            },
        )

        assert frompath(temp_dir / file_name, Leaf).name == "indented"

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
        file_name = "node.json"

        create_files(
            temp_dir,
            {
                file_name: json.dumps(
                    {
                        "title": "t",
                        "leaf": {},
                    },
                ),
            },
        )
        node = temp_dir / file_name

        with pytest.raises(DictableError) as info:
            frompath(node, Node)

        assert info.value.path == f"{node} \u2192 Node.leaf.name"

    def test_rules_are_applied(self, temp_dir, create_files):
        file_name = "timed.json"

        create_files(
            temp_dir,
            {
                file_name: json.dumps(
                    {
                        "moment": MOMENT,
                    },
                ),
            },
        )

        untimed = frompath(temp_dir / file_name, Untimed, {datetime: datetime.fromisoformat})

        assert untimed.moment == datetime.fromisoformat(MOMENT)
