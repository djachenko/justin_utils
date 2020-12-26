from datetime import timedelta
from enum import Enum
from functools import lru_cache
from typing import List, Optional


class DataSize:
    class Unit(Enum):
        BYTE = (2 ** 0, "B")
        KILOBYTE = (2 ** 10, "KB")
        MEGABYTE = (2 ** 20, "MB")
        GIGABYTE = (2 ** 30, "GB")

        def __init__(self, size: int, acronym: str) -> None:
            super().__init__()

            self.size = size
            self.acronym = acronym

        @staticmethod
        @lru_cache()
        def sorted_units() -> List['DataSize.Unit']:
            return sorted([
                DataSize.Unit.BYTE,
                DataSize.Unit.KILOBYTE,
                DataSize.Unit.MEGABYTE,
                DataSize.Unit.GIGABYTE,
            ],
                key=lambda u: u.size,
                reverse=True)

        @staticmethod
        def for_value(value: int) -> 'DataSize.Unit':
            for unit in DataSize.Unit.sorted_units():
                if value > unit.size:
                    return unit

            return DataSize.Unit.BYTE

    def __init__(self, size_in_bytes: int) -> None:
        super().__init__()

        assert isinstance(size_in_bytes, int)

        self.__bytes = size_in_bytes

    def __str__(self) -> str:
        return self.formatted()

    def formatted(self) -> str:
        unit = DataSize.Unit.for_value(self.__bytes)

        converted_size = round(self.__bytes / unit.size, 2)

        result = f"{converted_size:.2f} {unit.acronym}"

        return result

    def canonic_value(self) -> int:
        return round(self.__as_unit(DataSize.Unit.BYTE))

    def __as_unit(self, unit: Unit) -> float:
        return self.__bytes / unit.size

    def add_bytes(self, bytes_: int):
        self.__bytes += bytes_

    @classmethod
    def __from_unit(cls, size: float, unit: Unit) -> 'DataSize':
        return DataSize(round(size * unit.size))

    @classmethod
    def from_bytes(cls, size: int) -> 'DataSize':
        return DataSize.__from_unit(size, DataSize.Unit.BYTE)

    def __truediv__(self, other):
        if isinstance(other, timedelta):
            return DataSpeed(self, other)
        elif isinstance(other, DataSpeed):
            speed_canonic = other.canonic_value()

            if speed_canonic is None:
                return None

            self_canonic = self.canonic_value()

            time_in_seconds = self_canonic / speed_canonic

            return timedelta(seconds=time_in_seconds)
        else:
            assert False

    def __sub__(self, other) -> 'DataSize':
        if isinstance(other, DataSize):
            return DataSize.from_bytes(self.canonic_value() - other.canonic_value())
        else:
            assert False


class DataSpeed:
    def __init__(self, amount: DataSize, time: timedelta) -> None:
        super().__init__()

        assert isinstance(amount, DataSize)
        assert isinstance(time, timedelta)

        self.__amount = amount
        self.__time = time

    def __str__(self) -> str:
        return self.formatted()

    def formatted(self) -> str:
        speed = self.canonic_value()

        if speed is None:
            return "N/A"

        unit = DataSize.Unit.for_value(round(speed))

        converted_size = speed / unit.size

        result = f"{converted_size:.2f} {unit.acronym}/s"

        return result

    def canonic_value(self) -> Optional[float]:
        if self.__time.total_seconds() == 0:
            return None

        return self.__amount.canonic_value() / self.__time.total_seconds()
