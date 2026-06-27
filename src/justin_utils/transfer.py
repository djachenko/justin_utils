from datetime import datetime, timedelta
from typing import List, Tuple

from justin_utils.data import DataSize, DataSpeed


class TransferSpeedMeter:
    __HISTORY_SIZE = 6

    # noinspection PyTypeChecker
    def __init__(self) -> None:
        self.__global_start_time: datetime | None = None
        self.__global_stop_time: datetime | None = None
        self.__total_size: int | None = None

        self.__history_start_time: datetime | None = None
        self.__history: List[Tuple[datetime, int]] = []

    def start(self) -> None:
        now = datetime.now()

        self.__global_start_time = now
        self.__total_size = 0

        self.__history_start_time = now
        self.__history = [(now, 0) for _ in range(TransferSpeedMeter.__HISTORY_SIZE)]

    def feed(self, size: int) -> None:
        assert len(self.__history) > 0

        assert self.__total_size is not None

        now = datetime.now()

        self.__total_size += size
        self.__global_stop_time = now

        self.__history.append((now, size))
        self.__history_start_time = self.__history[0][0]

        self.__history = self.__history[-TransferSpeedMeter.__HISTORY_SIZE:]

    @property
    def current_value(self) -> DataSpeed:
        assert len(self.__history) > 0

        assert self.__history_start_time is not None

        total_size = sum(size for _, size in self.__history)
        elapsed_time = self.__history[-1][0] - self.__history_start_time

        return DataSpeed(DataSize.from_bytes(total_size), elapsed_time)

    @property
    def average_value(self) -> DataSpeed:
        assert self.__global_start_time is not None
        assert self.__global_stop_time is not None
        assert self.__total_size is not None

        return DataSpeed(DataSize.from_bytes(self.__total_size), self.__global_stop_time - self.__global_start_time)


class TransferTimeEstimator:
    @staticmethod
    def estimate(speed: DataSpeed, remaining_size: DataSize) -> timedelta:
        remaining_time = remaining_size / speed

        return remaining_time
