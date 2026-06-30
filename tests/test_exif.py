from datetime import datetime
from unittest.mock import MagicMock

from justin_utils.exif import PillowExif, NativeExif


# DateTimeOriginal = 36867, DateTime = 306 (PIL ExifTags)
_DATE_STR = "2024:03:15 10:30:00"
_EXPECTED_DT = datetime(2024, 3, 15, 10, 30, 0)


# region PillowExif

def test_pillow_exif_date_taken_from_datetime_original():
    source = {36867: _DATE_STR}
    exif = PillowExif(source)
    assert exif.date_taken == _EXPECTED_DT


def test_pillow_exif_date_taken_falls_back_to_datetime():
    source = {306: _DATE_STR}
    exif = PillowExif(source)
    assert exif.date_taken == _EXPECTED_DT


def test_pillow_exif_date_taken_is_cached():
    source = {36867: _DATE_STR}
    exif = PillowExif(source)

    result1 = exif.date_taken
    source[36867] = "2000:01:01 00:00:00"  # mutate after first access
    result2 = exif.date_taken

    assert result1 is result2


def test_pillow_exif_date_taken_returns_datetime():
    exif = PillowExif({36867: _DATE_STR})
    assert isinstance(exif.date_taken, datetime)


# endregion

# region NativeExif

def test_native_exif_date_taken_from_datetime_original():
    mock = MagicMock(spec=["datetime_original"])
    mock.datetime_original = _DATE_STR
    exif = NativeExif(mock)
    assert exif.date_taken == _EXPECTED_DT


def test_native_exif_date_taken_falls_back_to_datetime_digitized():
    mock = MagicMock(spec=["datetime_digitized"])
    mock.datetime_digitized = _DATE_STR
    exif = NativeExif(mock)
    assert exif.date_taken == _EXPECTED_DT


def test_native_exif_date_taken_is_cached():
    mock = MagicMock(spec=["datetime_original"])
    mock.datetime_original = _DATE_STR
    exif = NativeExif(mock)

    result1 = exif.date_taken
    mock.datetime_original = "2000:01:01 00:00:00"
    result2 = exif.date_taken

    assert result1 is result2


def test_native_exif_date_taken_returns_datetime():
    mock = MagicMock(spec=["datetime_original"])
    mock.datetime_original = _DATE_STR
    exif = NativeExif(mock)
    assert isinstance(exif.date_taken, datetime)


# endregion
