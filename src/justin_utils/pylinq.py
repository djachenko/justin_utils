from collections import defaultdict
from typing import TypeVar, Callable, Iterable, Iterator, List, Set, Tuple, Dict, Optional, Hashable, Any

Element = TypeVar("Element")
Result = TypeVar("Result")

Key = TypeVar("Key")
Value = TypeVar("Value")

Acc = TypeVar("Acc")

T = TypeVar("T")


def identity(x):
    return x


class Sequence(Iterable[Element]):
    def __init__(
            self,
            base: Iterable[Element] = None,
            predicate: Callable[[Element], bool] = lambda _: True,
            modifier: Callable[[Element], Result] = identity
    ) -> None:
        super().__init__()

        if base is None:
            base = []

        self.__base = base
        self.__modifier = modifier
        self.__predicate = predicate

    def __iter__(self) -> Iterator[Result]:
        for i in self.__base:
            if self.__predicate(i):
                yield self.__modifier(i)

    @classmethod
    def empty(cls) -> 'Sequence':
        return Sequence()

    @classmethod
    def with_sequence(cls, sequence: Iterable[Element]) -> 'Sequence[Element]':
        return Sequence(sequence)

    @classmethod
    def with_single(cls, element: Element) -> 'Sequence[Element]':
        return cls.with_sequence([element])

    @classmethod
    def with_dict(cls, dictionary: Dict[Key, Value]) -> 'Sequence[Tuple[Key, Value]]':
        return Sequence.with_sequence(dictionary.items())

    def filter(self, predicate: Callable[[Element], bool]) -> 'Sequence[Element]':
        return Sequence(self, predicate=predicate)

    def map(self, modifier: Callable[[Element], Result]) -> 'Sequence[Result]':
        return Sequence(self, modifier=modifier)

    def flat_map(self, modifier: Callable[[Element], Iterable[Result]] = identity) -> 'Sequence[Result]':
        def generator(seq):
            for subsequence in seq.map(modifier):
                for i in subsequence:
                    yield i

        return Sequence(generator(self))

    def __filter_by_index(self, predicate: Callable[[int], bool]) -> 'Sequence[Element]':
        return Sequence(
            enumerate(self),
            predicate=lambda t: predicate(t[0]),
            modifier=lambda t: t[1]
        )

    def take(self, count: int) -> 'Sequence[Element]':
        return self.__filter_by_index(lambda i: i < count)

    def skip(self, count: int) -> 'Sequence[Element]':
        return self.__filter_by_index(lambda i: i >= count)

    def not_null(self, key: Callable[[Element], Optional[Any]] = identity) -> 'Sequence[Element]':
        return self.filter(lambda x: key(x) is not None)

    def append(self, seq: Iterable[Element]) -> 'Sequence[Element]':
        def gen(*seqs: Iterable[Element]):
            for s in seqs:
                yield s

        return Sequence(gen(self, seq)).flat_map()

    def add(self, item: Element) -> 'Sequence[Element]':
        return self.append([item])

    def sum(self, key: Callable[[Element], Any] = identity) -> int:
        return sum(self.map(key))

    def reduce(self, acc: Acc, f: Callable[[Acc, Element], Acc]) -> Acc:
        for element in self:
            acc = f(acc, element)

        return acc

    def group_by(self, key: Callable[[Element], Key]) -> 'Sequence[Tuple[Key, Sequence[Element]]]':
        def reducer(acc, element):
            acc[key(element)].append(element)

            return acc

        result = self.reduce(defaultdict(lambda: []), reducer)

        return Sequence(result.items()) \
            .map(lambda e: (e[0], Sequence(e[1])))

    def distinct(self, key: Callable[[Element], Hashable] = identity) -> 'Sequence[Element]':
        hashes = set()
        results = []

        for e in self:
            e_hash = key(e)

            if e_hash not in hashes:
                hashes.add(e_hash)
                results.append(e)

        return Sequence(results)

    def is_distinct(self, key: Callable[[Element], Hashable] = identity) -> bool:
        hashes = set()

        for e in self.map(key):
            if e in hashes:
                return False

            hashes.add(e)

        return True

    def cache(self) -> 'Sequence[Element]':
        return Sequence(self.to_list())

    def max(self, key: Callable[[Element], Any] = identity) -> Optional[Element]:
        return max(self, key=key, default=None)

    def min(self, key: Callable[[Element], Any] = identity) -> Optional[Element]:
        return min(self, key=key, default=None)

    def to_list(self) -> List[Element]:
        return list(self)

    def to_set(self) -> Set[Element]:
        return set(self)

    def to_dict(self, item_generator: Callable[[Element], Tuple[Key, Value]] = identity) -> Dict[Key, Value]:
        return {k: v for k, v in self.map(item_generator)}

    def each(self, action: Callable[[Element], None]) -> None:
        for element in self:
            action(element)

    def any(self, predicate: Callable[[Element], bool] = lambda x: x) -> bool:
        return any(self.map(predicate))

    def same(self) -> bool:
        return len(self.to_set()) == 1
