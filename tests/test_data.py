from datetime import timedelta

import pytest

from justin_utils.data import DataSize, DataSpeed


class TestDataSizeUnitForValue:
    @pytest.mark.parametrize("value, expected_unit", [
        (0, DataSize.Unit.BYTE),
        (1, DataSize.Unit.BYTE),
        (1024, DataSize.Unit.KILOBYTE),
        (1025, DataSize.Unit.KILOBYTE),
        (2 ** 20, DataSize.Unit.MEGABYTE),
        (2 ** 20 + 1, DataSize.Unit.MEGABYTE),
        (2 ** 30, DataSize.Unit.GIGABYTE),
        (2 ** 30 + 1, DataSize.Unit.GIGABYTE),
    ])
    def test_for_value(self, value, expected_unit):
        assert DataSize.Unit.for_value(value) == expected_unit


class TestDataSizeFormatted:
    @pytest.mark.parametrize("size_in_bytes, expected", [
        (0, "0.00 B"),
        (512, "512.00 B"),
        (1025, "1.00 KB"),
        (2 ** 20 + 1, "1.00 MB"),
        (2 ** 30 + 1, "1.00 GB"),
        (int(1.5 * 2 ** 20) + 1, "1.50 MB"),
    ])
    def test_formatted(self, size_in_bytes, expected):
        assert DataSize(size_in_bytes).formatted() == expected

    def test_str_uses_formatted(self):
        assert str(DataSize(0)) == DataSize(0).formatted()


class TestDataSizeArithmetic:
    def test_canonic_value_returns_bytes(self):
        assert DataSize(2048).canonic_value() == 2048

    def test_from_bytes_roundtrips(self):
        assert DataSize.from_bytes(2048).canonic_value() == 2048

    def test_sub_returns_data_size(self):
        result = DataSize(2048) - DataSize(1024)

        assert isinstance(result, DataSize)
        assert result.canonic_value() == 1024

    def test_sub_non_data_size_asserts(self):
        with pytest.raises(AssertionError):
            DataSize(1024) - 512

    def test_truediv_timedelta_returns_data_speed(self):
        result = DataSize(1024) / timedelta(seconds=1)

        assert isinstance(result, DataSpeed)

    def test_truediv_data_speed_returns_timedelta(self):
        speed = DataSize(1024) / timedelta(seconds=1)
        result = DataSize(2048) / speed

        assert result == timedelta(seconds=2)

    def test_truediv_zero_time_speed_returns_none(self):
        speed = DataSize(1024) / timedelta(seconds=0)

        assert DataSize(2048) / speed is None

    def test_truediv_invalid_type_asserts(self):
        with pytest.raises(AssertionError):
            DataSize(1024) / 2

    @pytest.mark.parametrize("other, expected", [
        (DataSize(2048), True),
        (DataSize(512), False),
        (2048, True),
        (512, False),
    ])
    def test_lt(self, other, expected):
        assert (DataSize(1024) < other) == expected


class TestDataSpeed:
    def test_canonic_value_zero_time_returns_none(self):
        speed = DataSpeed(DataSize(1024), timedelta(seconds=0))

        assert speed.canonic_value() is None

    def test_canonic_value_computes_bytes_per_second(self):
        speed = DataSpeed(DataSize(2048), timedelta(seconds=2))

        assert speed.canonic_value() == 1024

    def test_formatted_zero_time_returns_na(self):
        speed = DataSpeed(DataSize(1024), timedelta(seconds=0))

        assert speed.formatted() == "N/A"

    def test_formatted_computes_rate(self):
        speed = DataSpeed(DataSize(2048), timedelta(seconds=2))

        assert speed.formatted() == "1.00 KB/s"

    def test_str_uses_formatted(self):
        speed = DataSpeed(DataSize(2048), timedelta(seconds=2))

        assert str(speed) == speed.formatted()

    def test_invalid_amount_type_asserts(self):
        with pytest.raises(AssertionError):
            DataSpeed(1024, timedelta(seconds=1))

    def test_invalid_time_type_asserts(self):
        with pytest.raises(AssertionError):
            DataSpeed(DataSize(1024), 1)
