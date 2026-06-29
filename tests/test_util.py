from datetime import date
from unittest.mock import patch

import pytest

from justin_utils.util import parse_date


def _today_year() -> int:
    return date.today().year


def test_parse_date_no_year_defaults_to_today():
    result = parse_date("1.6")
    assert result == date(_today_year(), 6, 1)


def test_parse_date_4_digit_year():
    assert parse_date("15.3.2024") == date(2024, 3, 15)


def test_parse_date_2_digit_year_current_century():
    # year <= today_year % 100 → maps to 2000s
    with patch("justin_utils.util.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 27)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = parse_date("1.6.24")
    assert result == date(2024, 6, 1)


def test_parse_date_2_digit_year_boundary():
    # year == today_year % 100 → maps to current year
    with patch("justin_utils.util.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 27)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = parse_date("1.6.26")
    assert result == date(2026, 6, 1)


def test_parse_date_2_digit_year_previous_century():
    # year > today_year % 100 → maps to 1900s
    with patch("justin_utils.util.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 27)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = parse_date("1.6.27")
    assert result == date(1927, 6, 1)


def test_parse_date_2_digit_year_00():
    with patch("justin_utils.util.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 27)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = parse_date("1.6.00")
    assert result == date(2000, 6, 1)


def test_parse_date_2_digit_year_99():
    with patch("justin_utils.util.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 27)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = parse_date("1.6.99")
    assert result == date(1999, 6, 1)
