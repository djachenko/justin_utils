from datetime import datetime
from unittest.mock import MagicMock

import pytest

from justin_utils.exif import PillowExif, NativeExif


# DateTimeOriginal = 36867, DateTime = 306 (PIL ExifTags)
_DATE_STR = "2024:03:15 10:30:00"
_EXPECTED_DT = datetime(2024, 3, 15, 10, 30, 0)


class TestPillowExif:
    @pytest.mark.parametrize("source", [
        {36867: _DATE_STR},
        {306: _DATE_STR},
        {36867: _DATE_STR, 306: "2000:01:01 00:00:00"},
    ])
    def test_date_taken_prefers_datetime_original(self, source):
        exif = PillowExif(source)

        assert exif.date_taken == _EXPECTED_DT

    def test_date_taken_returns_datetime(self):
        exif = PillowExif({36867: _DATE_STR})

        assert isinstance(exif.date_taken, datetime)

    def test_date_taken_is_cached(self):
        source = {36867: _DATE_STR}
        exif = PillowExif(source)

        result1 = exif.date_taken
        source[36867] = "2000:01:01 00:00:00"  # mutate after first access
        result2 = exif.date_taken

        assert result1 is result2


class TestNativeExif:
    @pytest.mark.parametrize("attr", [
        "datetime_original",
        "datetime_digitized",
    ])
    def test_date_taken_reads_available_attribute(self, attr):
        mock = MagicMock(spec=[attr])
        setattr(mock, attr, _DATE_STR)

        exif = NativeExif(mock)

        assert exif.date_taken == _EXPECTED_DT

    def test_date_taken_returns_datetime(self):
        mock = MagicMock(spec=["datetime_original"])
        mock.datetime_original = _DATE_STR

        exif = NativeExif(mock)

        assert isinstance(exif.date_taken, datetime)

    def test_date_taken_is_cached(self):
        mock = MagicMock(spec=["datetime_original"])
        mock.datetime_original = _DATE_STR
        exif = NativeExif(mock)

        result1 = exif.date_taken
        mock.datetime_original = "2000:01:01 00:00:00"
        result2 = exif.date_taken

        assert result1 is result2
