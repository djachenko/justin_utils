import pytest

from justin_utils.joins import inner, left, right


def _eq(a, b) -> bool:
    return a == b


class TestInner:
    @pytest.mark.parametrize("seq1, seq2, expected", [
        ([0], [0], [(0, 0)]),
        ([False], [False], [(False, False)]),
        ([""], [""], [("", "")]),
        ([0], [1], []),
    ])
    def test_inner_falsy_values(self, seq1, seq2, expected):
        assert list(inner(seq1, seq2, _eq)) == expected

    def test_inner_mixed_falsy_and_truthy(self):
        result = list(inner([0, 1, 2], [0, 2], _eq))

        assert set(result) == {(0, 0), (2, 2)}


class TestLeft:
    @pytest.mark.parametrize("seq1, seq2, expected_pair", [
        ([0], [1], (0, None)),
        ([0], [0], (0, 0)),
        ([""], ["x"], ("", None)),
        ([False], [False], (False, False)),
    ])
    def test_left_keeps_falsy_values(self, seq1, seq2, expected_pair):
        result = list(left(seq1, seq2, _eq))

        assert expected_pair in result


class TestRight:
    @pytest.mark.parametrize("seq1, seq2, expected_pair", [
        ([1], [0], (None, 0)),
        ([0], [0], (0, 0)),
        (["x"], [""], (None, "")),
    ])
    def test_right_keeps_falsy_values(self, seq1, seq2, expected_pair):
        result = list(right(seq1, seq2, _eq))

        assert expected_pair in result
