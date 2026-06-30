
from justin_utils.joins import inner, left, right


def _eq(a, b) -> bool:
    return a == b


# region inner

def test_inner_falsy_zero():
    assert list(inner([0], [0], _eq)) == [(0, 0)]


def test_inner_falsy_false():
    assert list(inner([False], [False], _eq)) == [(False, False)]


def test_inner_falsy_empty_string():
    assert list(inner([""], [""], _eq)) == [("", "")]


def test_inner_falsy_no_match_returns_empty():
    assert list(inner([0], [1], _eq)) == []


def test_inner_mixed_falsy_and_truthy():
    result = list(inner([0, 1, 2], [0, 2], _eq))
    assert set(result) == {(0, 0), (2, 2)}


# endregion

# region left

def test_left_keeps_unmatched_left_falsy():
    # 0 has no match in seq2 — should appear as (0, None)
    result = list(left([0], [1], _eq))
    assert (0, None) in result


def test_left_keeps_matched_falsy():
    result = list(left([0], [0], _eq))
    assert (0, 0) in result


def test_left_empty_string_unmatched():
    result = list(left([""], ["x"], _eq))
    assert ("", None) in result


def test_left_false_matched():
    result = list(left([False], [False], _eq))
    assert (False, False) in result


# endregion

# region right

def test_right_keeps_unmatched_right_falsy():
    result = list(right([1], [0], _eq))
    assert (None, 0) in result


def test_right_keeps_matched_falsy():
    result = list(right([0], [0], _eq))
    assert (0, 0) in result


def test_right_empty_string_unmatched():
    result = list(right(["x"], [""], _eq))
    assert (None, "") in result


# endregion
