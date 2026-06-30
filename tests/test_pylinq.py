import pytest

from justin_utils.pylinq import Sequence


class TestConstruction:
    @pytest.mark.parametrize("seq", [Sequence(), Sequence.empty()])
    def test_empty_construction(self, seq):
        assert seq.to_list() == []

    def test_with_sequence(self):
        assert Sequence.with_sequence([1, 2, 3]).to_list() == [1, 2, 3]

    def test_with_single(self):
        assert Sequence.with_single(1).to_list() == [1]

    def test_with_dict(self):
        result = Sequence.with_dict({"a": 1, "b": 2}).to_list()

        assert set(result) == {("a", 1), ("b", 2)}


class TestFilter:
    @pytest.mark.parametrize("items, predicate, expected", [
        ([1, 2, 3, 4], lambda x: x % 2 == 0, [2, 4]),
        ([1, 2, 3], lambda x: x > 10, []),
        ([], lambda x: True, []),
    ])
    def test_filter(self, items, predicate, expected):
        result = Sequence.with_sequence(items).filter(predicate).to_list()

        assert result == expected


class TestMap:
    @pytest.mark.parametrize("items, modifier, expected", [
        ([1, 2, 3], lambda x: x * 2, [2, 4, 6]),
        ([1, 2, 3], str, ["1", "2", "3"]),
        ([], lambda x: x, []),
    ])
    def test_map(self, items, modifier, expected):
        result = Sequence.with_sequence(items).map(modifier).to_list()

        assert result == expected


class TestFlatMap:
    def test_flat_map_default_identity(self):
        result = Sequence.with_sequence([[1, 2], [3], []]).flat_map().to_list()

        assert result == [1, 2, 3]

    def test_flat_map_with_modifier(self):
        result = Sequence.with_sequence([1, 2]).flat_map(lambda x: [x, x]).to_list()

        assert result == [1, 1, 2, 2]


class TestTakeSkip:
    @pytest.mark.parametrize("count, expected", [
        (0, []),
        (2, [1, 2]),
        (10, [1, 2, 3, 4]),
    ])
    def test_take(self, count, expected):
        assert Sequence.with_sequence([1, 2, 3, 4]).take(count).to_list() == expected

    @pytest.mark.parametrize("count, expected", [
        (0, [1, 2, 3, 4]),
        (2, [3, 4]),
        (10, []),
    ])
    def test_skip(self, count, expected):
        assert Sequence.with_sequence([1, 2, 3, 4]).skip(count).to_list() == expected


class TestNotNull:
    @pytest.mark.parametrize("items, key, expected", [
        ([1, None, 2, None], None, [1, 2]),
        ([{"v": 1}, {"v": None}, {"v": 2}], lambda x: x["v"], [{"v": 1}, {"v": 2}]),
    ])
    def test_not_null(self, items, key, expected):
        seq = Sequence.with_sequence(items)

        result = (seq.not_null(key=key) if key else seq.not_null()).to_list()

        assert result == expected


class TestAppendAdd:
    def test_append(self):
        result = Sequence.with_sequence([1, 2]).append([3, 4]).to_list()

        assert result == [1, 2, 3, 4]

    def test_add(self):
        result = Sequence.with_sequence([1, 2]).add(3).to_list()

        assert result == [1, 2, 3]


class TestSumReduce:
    @pytest.mark.parametrize("items, key, expected", [
        ([1, 2, 3], None, 6),
        ([{"v": 1}, {"v": 2}], lambda x: x["v"], 3),
        ([], None, 0),
    ])
    def test_sum(self, items, key, expected):
        seq = Sequence.with_sequence(items)

        result = seq.sum(key) if key else seq.sum()

        assert result == expected

    def test_reduce(self):
        result = Sequence.with_sequence([1, 2, 3]).reduce(0, lambda acc, x: acc + x)

        assert result == 6


class TestGroupBy:
    def test_group_by(self):
        items = [1, 2, 3, 4, 5, 6]
        result = Sequence.with_sequence(items).group_by(lambda x: x % 2).to_dict()

        assert {k: v.to_list() for k, v in result.items()} == {
            1: [1, 3, 5],
            0: [2, 4, 6],
        }


class TestDistinct:
    @pytest.mark.parametrize("items, key, expected", [
        ([1, 2, 2, 3, 1], None, [1, 2, 3]),
        ([{"v": 1}, {"v": 1}, {"v": 2}], lambda x: x["v"], [{"v": 1}, {"v": 2}]),
    ])
    def test_distinct(self, items, key, expected):
        seq = Sequence.with_sequence(items)

        result = (seq.distinct(key=key) if key else seq.distinct()).to_list()

        assert result == expected

    @pytest.mark.parametrize("items, expected", [
        ([1, 2, 3], True),
        ([1, 2, 2], False),
        ([], True),
    ])
    def test_is_distinct(self, items, expected):
        assert Sequence.with_sequence(items).is_distinct() == expected


class TestCache:
    def test_cache_materializes_sequence(self):
        calls = []

        def tracked(x):
            calls.append(x)

            return x

        seq = Sequence.with_sequence([1, 2, 3]).map(tracked).cache()

        seq.to_list()
        seq.to_list()

        assert calls == [1, 2, 3]


class TestMinMax:
    @pytest.mark.parametrize("items, expected", [
        ([3, 1, 2], 3),
        ([], None),
    ])
    def test_max(self, items, expected):
        assert Sequence.with_sequence(items).max() == expected

    @pytest.mark.parametrize("items, expected", [
        ([3, 1, 2], 1),
        ([], None),
    ])
    def test_min(self, items, expected):
        assert Sequence.with_sequence(items).min() == expected

    def test_max_with_key(self):
        items = [{"v": 1}, {"v": 3}, {"v": 2}]

        result = Sequence.with_sequence(items).max(key=lambda x: x["v"])

        assert result == {"v": 3}


class TestConversions:
    def test_to_list(self):
        assert Sequence.with_sequence([1, 2]).to_list() == [1, 2]

    def test_to_set(self):
        assert Sequence.with_sequence([1, 1, 2]).to_set() == {1, 2}

    @pytest.mark.parametrize("items, generator, expected", [
        ([(1, "a"), (2, "b")], None, {1: "a", 2: "b"}),
        ([1, 2], lambda x: (x, x * 2), {1: 2, 2: 4}),
    ])
    def test_to_dict(self, items, generator, expected):
        seq = Sequence.with_sequence(items)

        result = seq.to_dict(generator) if generator else seq.to_dict()

        assert result == expected


class TestEach:
    def test_each_calls_action_for_every_element(self):
        seen = []

        Sequence.with_sequence([1, 2, 3]).each(seen.append)

        assert seen == [1, 2, 3]


class TestAny:
    @pytest.mark.parametrize("items, predicate, expected", [
        ([0, 0, 1], None, True),
        ([0, 0, 0], None, False),
        ([], None, False),
        ([1, 2, 3], lambda x: x > 2, True),
        ([1, 2, 3], lambda x: x > 10, False),
    ])
    def test_any(self, items, predicate, expected):
        seq = Sequence.with_sequence(items)

        result = seq.any(predicate) if predicate else seq.any()

        assert result == expected


class TestSame:
    @pytest.mark.parametrize("items, expected", [
        ([1, 1, 1], True),
        ([1, 2], False),
        ([1], True),
    ])
    def test_same(self, items, expected):
        assert Sequence.with_sequence(items).same() == expected
