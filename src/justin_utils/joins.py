import itertools
from typing import Callable, Iterable, Tuple, TypeVar, List

T = TypeVar("T")
V = TypeVar("V")


# todo: rewrite in lazy way

def full_outer(seq1: Iterable[T], seq2: Iterable[V], on: Callable[[T, V], bool]) -> List[Tuple[T, V]]:
    sequences = [seq1, seq2]

    inclusion_mapping = [{e: False for e in seq} for seq in [seq1, seq2]]

    result = itertools.product(*sequences)  # type: ignore[var-annotated]

    def unwrapper(t):
        return on(*t)

    result = list(filter(unwrapper, result))  # type: ignore[assignment]

    for joining in result:
        for i, element in enumerate(joining):
            inclusion_mapping[i][element] = True

    for i in range(len(sequences)):
        for element, state in inclusion_mapping[i].items():
            if not state:
                pre_tuple = [None for _ in sequences]

                pre_tuple[i] = element  # type: ignore[call-overload]

                joining = tuple(pre_tuple)

                result.append(joining)  # type: ignore[attr-defined, arg-type]

    return result  # type: ignore[return-value]


def __has_left(pair: Tuple) -> bool:
    return pair[0] is not None


def __has_right(pair: Tuple) -> bool:
    return pair[1] is not None


def __has_both(pair: Tuple) -> bool:
    return __has_left(pair) and __has_right(pair)


def inner(seq1: Iterable[T], seq2: Iterable[V], on: Callable[[T, V], bool]) -> Iterable[Tuple[T, V]]:
    return [i for i in full_outer(seq1, seq2, on) if __has_both(i)]


def left(seq1: Iterable[T], seq2: Iterable[V], on: Callable[[T, V], bool]) -> Iterable[Tuple[T, V]]:
    return [i for i in full_outer(seq1, seq2, on) if __has_left(i)]


def right(seq1: Iterable[T], seq2: Iterable[V], on: Callable[[T, V], bool]) -> Iterable[Tuple[T, V]]:
    return [i for i in full_outer(seq1, seq2, on) if __has_right(i)]
