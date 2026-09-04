from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

import pytest

from justin_utils.dictable import DictableDataclass, fromdict


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
class Timed(DictableDataclass):
    moment: datetime | None = None

    @classmethod
    def rules(cls) -> dict[type, Callable]:
        return {datetime: datetime.fromisoformat}


class TestScalars:
    def test_plain_fields(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}, "count": 5})

        assert node.title == "t"
        assert node.count == 5

    def test_coerces_type(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}, "count": "7"})

        assert node.count == 7

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
        node = Node.from_dict(
            {
                "title": "t",
                "leaf": {"name": "l"},
                "leaves": [{"name": "one"}, {"name": "two"}],
            }
        )

        assert [leaf.name for leaf in node.leaves] == ["one", "two"]
        assert all(isinstance(leaf, Leaf) for leaf in node.leaves)


class TestDefaults:
    def test_default_factory_on_missing_field(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}})

        assert node.tags == []
        assert node.leaves == []

    def test_default_factory_returns_fresh_instance(self):
        first = Node.from_dict({"title": "t", "leaf": {"name": "l"}})
        second = Node.from_dict({"title": "t", "leaf": {"name": "l"}})

        first.tags.append("mutated")

        assert second.tags == []

    def test_plain_default_on_missing_field(self):
        assert Node.from_dict({"title": "t", "leaf": {"name": "l"}}).count == 0

    def test_default_factory_on_failed_conversion(self):
        node = Node.from_dict({"title": "t", "leaf": {"name": "l"}, "tags": 42})

        assert node.tags == []


class TestLogging:
    def test_broken_field_warns(self, caplog):
        with caplog.at_level("WARNING", logger="justin_utils.dictable"):
            node = Node.from_dict({"title": "t", "leaf": "не объект"})

        assert node.leaf is None
        assert "Node.leaf" in caplog.text

    def test_explicit_null_does_not_warn(self, caplog):
        with caplog.at_level("WARNING", logger="justin_utils.dictable"):
            timed = Timed.from_dict({"moment": None})

        assert timed.moment is None
        assert caplog.text == ""

    def test_missing_field_does_not_warn(self, caplog):
        with caplog.at_level("WARNING", logger="justin_utils.dictable"):
            Node.from_dict({"title": "t", "leaf": {"name": "l"}})

        assert caplog.text == ""


class TestRules:
    def test_rule_applied(self):
        timed = Timed.from_dict({"moment": "2026-03-01T12:00:00.000+1000"})

        assert timed.moment == datetime.fromisoformat("2026-03-01T12:00:00.000+1000")

    def test_null_falls_back_to_default(self):
        assert Timed.from_dict({"moment": None}).moment is None


class TestAsDict:
    def test_roundtrip(self):
        source = {"title": "t", "leaf": {"name": "l"}, "count": 3}
        node = Node.from_dict(source)

        assert node.as_dict()["title"] == "t"
        assert node.as_dict()["count"] == 3


class TestFromdictFunction:
    def test_works_on_plain_dataclass(self):
        @dataclass
        class Plain:
            value: int = 0

        assert fromdict({"value": "9"}, Plain).value == 9

    @pytest.mark.parametrize(
        "payload, expected",
        [
            ({"name": "a"}, "a"),
            ({"name": 1}, "1"),
        ],
    )
    def test_scalar_coercion(self, payload, expected):
        assert Leaf.from_dict(payload).name == expected
