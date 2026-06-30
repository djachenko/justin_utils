from datetime import date
from unittest.mock import patch

import pytest

from justin_utils.util import parse_date


def _today_year() -> int:
    return date.today().year


class TestParseDate:
    def test_no_year_defaults_to_today(self):
        result = parse_date("1.6")

        assert result == date(_today_year(), 6, 1)

    def test_4_digit_year(self):
        assert parse_date("15.3.2024") == date(2024, 3, 15)

    @pytest.mark.parametrize("two_digit_year, expected_year", [
        (24, 2024),  # year <= today_year % 100 -> 2000s
        (26, 2026),  # year == today_year % 100 -> 2000s
        (27, 1927),  # year > today_year % 100 -> 1900s
        (0, 2000),
        (99, 1999),
    ])
    def test_2_digit_year(self, two_digit_year, expected_year):
        with patch("justin_utils.util.date") as mock_date:
            mock_date.today.return_value = date(2026, 6, 27)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)

            result = parse_date(f"1.6.{two_digit_year:02d}")

        assert result == date(expected_year, 6, 1)
