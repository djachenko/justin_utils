from abc import ABC
from functools import lru_cache
from typing import TypeVar, Type

T = TypeVar('T', bound='Singleton')


class Singleton(ABC):
    __initiating_from_instance = False

    def __init__(self) -> None:
        assert self.__initiating_from_instance

        super().__init__()

    @classmethod
    @lru_cache()
    def instance(cls: Type[T]) -> T:
        cls.__initiating_from_instance = True

        instance = cls()

        cls.__initiating_from_instance = False

        return instance
