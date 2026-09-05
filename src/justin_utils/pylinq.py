from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Iterator
from typing import (
    Any,
    Self,
    TypeVar,
    overload,
)

Element = TypeVar("Element")
Result = TypeVar("Result")

Key = TypeVar("Key")
Value = TypeVar("Value")

Acc = TypeVar("Acc")

T = TypeVar("T")


def identity(x: T) -> T:
    return x


def accept_all(_: Any) -> bool:
    return True


class Sequence(Iterable[Element]):
    def __init__(
            self,
            base: Iterable[Any] | None = None,
            predicate: Callable[[Any], bool] = accept_all,
            modifier: Callable[[Any], Any] = identity,
    ) -> None:
        super().__init__()

        if base is None:
            base = []

        self.__base = base
        self.__modifier = modifier
        self.__predicate = predicate

    def __iter__(self) -> Iterator[Element]:
        for i in self.__base:
            if self.__predicate(i):
                yield self.__modifier(i)

    @classmethod
    def empty(cls) -> Sequence:
        return Sequence()

    @classmethod
    def with_sequence(cls, sequence: Iterable[Element]) -> Sequence[Element]:
        return Sequence(sequence)

    @classmethod
    def with_single(cls, element: Element) -> Sequence[Element]:
        return cls.with_sequence([element])

    @classmethod
    def with_dict(cls, dictionary: dict[Key, Value]) -> Sequence[tuple[Key, Value]]:
        return Sequence.with_sequence(dictionary.items())

    def filter(self, predicate: Callable[[Element], bool]) -> Self:
        return type(self)(self, predicate=predicate)

    def map(self, modifier: Callable[[Element], Result]) -> Sequence[Result]:
        return Sequence(self, modifier=modifier)

    @overload
    def flat_map(self: Sequence[Iterable[Result]]) -> Sequence[Result]: ...

    @overload
    def flat_map(self, modifier: Callable[[Element], Iterable[Result]]) -> Sequence[Result]: ...

    def flat_map(self, modifier: Any = identity) -> Sequence[Result]:
        def generator(seq: Sequence[Element]) -> Iterator[Result]:
            for subsequence in seq.map(modifier):
                yield from subsequence

        return Sequence(generator(self))

    def __filter_by_index(self, predicate: Callable[[int], bool]) -> Self:
        return type(self)(enumerate(self), predicate=lambda t: predicate(t[0]), modifier=lambda t: t[1])

    def take(self, count: int) -> Self:
        return self.__filter_by_index(lambda i: i < count)

    def skip(self, count: int) -> Self:
        return self.__filter_by_index(lambda i: i >= count)

    def not_null(self, key: Callable[[Element], Any | None] = identity) -> Self:
        return self.filter(lambda x: key(x) is not None)

    def append(self, seq: Iterable[Element]) -> Self:
        return type(self)(itertools.chain(self, seq))

    def add(self, item: Element) -> Self:
        return self.append([item])

    def sum(self, key: Callable[[Element], Any] = identity) -> int:
        return sum(self.map(key))

    def reduce(self, acc: Acc, f: Callable[[Acc, Element], Acc]) -> Acc:
        for element in self:
            acc = f(acc, element)

        return acc

    def group_by(self, key: Callable[[Element], Key]) -> Sequence[tuple[Key, Sequence[Element]]]:
        def reducer(acc: defaultdict[Key, list[Element]], element: Element) -> defaultdict[Key, list[Element]]:
            acc[key(element)].append(element)

            return acc

        initial: defaultdict[Key, list[Element]] = defaultdict(list)
        result = self.reduce(initial, reducer)

        return Sequence(result.items()).map(lambda e: (e[0], Sequence(e[1])))

    def distinct(self, key: Callable[[Element], Hashable] = identity) -> Self:
        hashes = set()
        results = []

        for e in self:
            e_hash = key(e)

            if e_hash not in hashes:
                hashes.add(e_hash)
                results.append(e)

        return type(self)(results)

    def is_distinct(self, key: Callable[[Element], Hashable] = identity) -> bool:
        hashes = set()

        for e in self.map(key):
            if e in hashes:
                return False

            hashes.add(e)

        return True

    def cache(self) -> Self:
        return type(self)(self.to_list())

    def max(self, key: Callable[[Element], Any] = identity) -> Element | None:
        return max(self, key=key, default=None)

    def min(self, key: Callable[[Element], Any] = identity) -> Element | None:
        return min(self, key=key, default=None)

    def to_list(self) -> list[Element]:
        return list(self)

    def to_set(self) -> set[Element]:
        return set(self)

    @overload
    def to_dict(self: Sequence[tuple[Key, Value]]) -> dict[Key, Value]: ...

    @overload
    def to_dict(self, item_generator: Callable[[Element], tuple[Key, Value]]) -> dict[Key, Value]: ...

    def to_dict(self, item_generator: Any = identity) -> dict[Key, Value]:
        return {k: v for k, v in self.map(item_generator)}

    def each(self, action: Callable[[Element], None]) -> None:
        for element in self:
            action(element)

    def any(self, predicate: Callable[[Element], bool] = bool) -> bool:
        return any(self.map(predicate))

    def same(self) -> bool:
        return len(self.to_set()) == 1
