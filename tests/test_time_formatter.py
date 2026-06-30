from datetime import timedelta

import pytest

from justin_utils.time_formatter import format_time


class TestFormatTime:
    @pytest.mark.parametrize("seconds, expected", [
        (0, "0.0 s"),
        (1, "1.0 s"),
        (30, "30.0 s"),
        (59, "59.0 s"),
        (59.9, "59.9 s"),
    ])
    def test_seconds_only(self, seconds, expected):
        assert format_time(timedelta(seconds=seconds)) == expected

    @pytest.mark.parametrize("seconds, expected", [
        (60, "1.0 m"),
        (90, "1.5 m"),
        (3599, "60.0 m"),
    ])
    def test_minutes(self, seconds, expected):
        assert format_time(timedelta(seconds=seconds)) == expected

    @pytest.mark.parametrize("seconds, expected", [
        (3600, "1.0 h"),
        (5400, "1.5 h"),
        (7200, "2.0 h"),
    ])
    def test_hours(self, seconds, expected):
        assert format_time(timedelta(seconds=seconds)) == expected
