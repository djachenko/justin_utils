import glob
import random
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, Sequence
from datetime import date, datetime, time
from pathlib import Path
from time import process_time
from typing import Any, TypeVar

T = TypeVar("T")
V = TypeVar("V")


def split_by_predicates[T](seq: Iterable[T], *lambdas: Callable[[T], bool]) -> Iterable[Iterable[T]]:
    return [list(filter(x, seq)) for x in lambdas]


def ask_for_permission(question: str) -> bool:
    while True:
        answer_input = input(f"{question} y/n ")

        answer_input = answer_input.lower().strip()

        if answer_input in ["y", "n"]:
            answer = answer_input == "y"

            return answer


def ask_for_choice_flagged(question: str, options: list[str]) -> str | None:
    print(question)

    for index, option in enumerate(options):
        print(f"{index}: {option}")

    print("-: abort")
    print('"": empty')

    answer = input("Enter chosen option: ")

    if answer == "-":
        return None
    elif answer == "":
        return ""
    elif answer.isdecimal():
        option_index = int(answer)

        if option_index in range(len(options)):
            return options[option_index]

    return answer


def ask_for_choice_with_other(question: str, options: list[str]) -> str:
    other = "other"

    options.append(other)

    option = ask_for_choice(question, options)

    if option == other:
        option = input("> ")

    return option


def ask_for_choice[T](question: str, options: list[T]) -> T | str:
    assert len(options) > 0

    if len(options) == 1:
        return options[0]

    print(question)

    for index, option in enumerate(options):
        print(f"{index}. {option}")

    while True:
        answer = input("Enter chosen index: ")

        try:
            option_index = int(answer)

            if option_index in range(len(options)):
                return options[option_index]

        except ValueError:
            pass


def measure_time(name: str | None = None) -> Callable[..., Any]:
    if name is None:
        name = "Execution"

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def inner(*args: Any, **kwargs: Any) -> Any:
            start = process_time()

            result = func(*args, **kwargs)

            end = process_time()

            passed = end - start

            print(f"{name} took {passed} s.")

            return result

        return inner

    return decorator


def concat_dictionaries[T](*dictionaries: dict[T, Any]) -> dict[T, Any]:
    result: dict[T, Any] = {}

    for dictionary in dictionaries:
        keys = dictionary.keys()

        assert len(set(keys).intersection(result.keys())) == 0

        result.update(dictionary)

    return result


def resolve_patterns(*patterns: str) -> Iterable[Path]:
    for pattern in patterns:
        for str_path in glob.iglob(pattern):
            path = Path(str_path).absolute()

            yield path


def flatten_lazy[T](list_of_lists: Iterable[Iterable[T]]) -> Iterable[T]:
    for sublist in list_of_lists:
        yield from sublist


def flat_map[T](list_of_lists: Iterable[Iterable[T]]) -> list[T]:
    return list(flatten_lazy(list_of_lists))


def distinct[T](items: Iterable[T]) -> list[T]:
    cache = set()
    result = []

    for item in items:
        if item not in cache:
            cache.add(item)
            result.append(item)

    return result


def is_distinct[T](seq: Iterable[T], key: Callable[[T], Any] = lambda x: x) -> bool:
    try:
        # noinspection PyTypeChecker
        seq_len = len(seq)  # type: ignore[arg-type]
    except TypeError:
        seq = list(seq)

        seq_len = len(seq)

    return len(set(map(key, seq))) == seq_len


def is_iterable(obj: Any) -> bool:
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def all_same_type(seq: Iterable[Any]) -> bool:
    return same(type(i) for i in seq)


def same(seq: Iterable[Any]) -> bool:
    return len(set(seq)) == 1


def parse_time(string: str) -> time:
    separator = ":"

    string = string.replace(".", separator)

    parts = string.split(separator)

    parts = [part.zfill(2) for part in parts]

    string = separator.join(parts)

    result = time.fromisoformat(string)

    return result


def parse_date(string: str) -> date:
    separator = "."

    day, month, *year_list = [int(i) for i in string.split(separator)]

    today_year = date.today().year  # noqa: DTZ011

    if not year_list:
        year = today_year
    else:
        year = year_list[0]

    if year < 100:
        if year <= today_year % 100:
            year += 2000
        else:
            year += 1900

    return date(year, month, day)


def random_date(start: time, end: time, count: int) -> Iterator[time]:
    today = date.today()  # noqa: DTZ011

    time_delta = datetime.combine(today, end) - datetime.combine(today, start)
    minutes_delta = int(time_delta.total_seconds() / 60) - 1

    start_in_minutes = start.hour * 60 + start.minute

    for _ in range(count):
        time_in_minutes = start_in_minutes + random.randint(0, minutes_delta)

        result = time(hour=time_in_minutes // 60, minute=time_in_minutes % 60)

        yield result


def group_by[T, V](key: Callable[[T], V], seq: Iterable[T]) -> dict[V, list[T]]:
    mapping = defaultdict(list)

    for i in seq:
        mapping[key(i)].append(i)

    return mapping


def stride[T](seq: Iterable[T], step: int) -> Iterable[list[T]]:
    # i = iter(seq)
    #
    # def inner() -> Iterable[T]:
    #     for j in range(step):
    #         print(j)
    #
    #         yield next(i)
    #
    # while True:
    #     try:
    #         yield inner()
    #     except StopIteration:
    #         break
    #
    current = []

    for i in seq:
        current.append(i)

        if len(current) == step:
            yield current

            current = []

    if current:
        yield current


def first[T](seq: Iterable[T], key: Callable[[T], Any] = lambda x: x, default: T | None = None) -> T | None:
    for i in seq:
        if key(i):
            return i

    return default


def bfs[T](start: T, provider: Callable[[T], Iterable[T]]) -> None:
    roots = [start]

    while roots:
        roots += provider(roots.pop(0))


def get_prefixes(s: str, separator: str) -> list[str]:
    prefixes = []
    split = s.split(separator)

    for i in range(1, len(split) + 1):
        prefixes.append(separator.join(split[:i]))

    return prefixes


def merge_dicts[V, T](merger: Callable[[V, V], V], *dicts: dict[T, V]) -> dict[T, V]:
    result: dict[T, V] = {}

    for d in dicts:
        for key in d:
            if key in result:
                result[key] = merger(result[key], d[key])
            else:
                result[key] = d[key]

    return result


K = TypeVar("K")


class keydefaultdict(dict[K, V]):
    def __init__(self, default_factory: Callable[[K], V], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.default_factory = default_factory

    def __missing__(self, key: K) -> V:
        if self.default_factory is None:
            raise KeyError(key)
        else:
            result = self.default_factory(key)

            self[key] = result

            return result
