from abc import ABC
from functools import cache
from typing import Self, TypeVar

T = TypeVar('T', bound='Singleton')


class Singleton(ABC):  # noqa: B024 ABC declares a base class, the assert blocks direct use
    __initiating_from_instance = False

    def __init__(self) -> None:
        assert self.__initiating_from_instance

        super().__init__()

    @classmethod
    @cache
    def instance(cls) -> Self:
        cls.__initiating_from_instance = True

        instance = cls()

        cls.__initiating_from_instance = False

        return instance
