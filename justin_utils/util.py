import glob
import random
from collections import defaultdict
from collections.abc import Sequence
from datetime import time, date, datetime
from pathlib import Path
from time import process_time
from typing import Iterable, TypeVar, Callable, Dict, Any, List

T = TypeVar("T")
V = TypeVar("V")


def split_by_predicates(seq: Iterable[T], *lambdas: Callable[[T], bool]) -> Iterable[Iterable[T]]:
    return list(map(lambda x: list(filter(x, seq)), lambdas))


def ask_for_permission(question: str) -> bool:
    while True:
        answer_input = input(f"{question} y/n ")

        answer_input = answer_input.lower().strip()

        if answer_input in ["y", "n"]:
            answer = answer_input == "y"

            return answer


def ask_for_choice_flagged(question: str, options: List[str]) -> str | None:
    print(question)

    for index, option in enumerate(options):
        print(f"{index}: {option}")

    print(f"-: abort")
    print(f"\"\": empty")

    answer = input("Enter chosen option: ")

    if answer == "-":
        return None
    elif answer == "":
        return ""
    elif answer.isdecimal():
        option_index = int(answer)

        if option_index in range(0, len(options)):
            return options[option_index]

    return answer


def ask_for_choice_with_other(question: str, options: List[str]) -> str:
    other = "other"

    options.append(other)

    option = ask_for_choice(question, options)

    if option == other:
        option = input("> ")

    return option


def ask_for_choice(question: str, options: List[T]) -> T | str:
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

            if option_index in range(0, len(options)):
                return options[option_index]

        except ValueError:
            pass


def measure_time(name=None):
    if name is None:
        name = "Execution"

    def decorator(func):
        def inner(*args, **kwargs):
            start = process_time()

            result = func(*args, **kwargs)

            end = process_time()

            passed = end - start

            print(f"{name} took {passed} s.")

            return result

        return inner

    return decorator


def concat_dictionaries(*dictionaries: Dict[T, Any]) -> Dict[T, Any]:
    result = {}

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


def flatten_lazy(list_of_lists: Iterable[Iterable[T]]) -> Iterable[T]:
    for sublist in list_of_lists:
        for item in sublist:
            yield item


def flat_map(list_of_lists: Iterable[Iterable[T]]) -> List[T]:
    return list(flatten_lazy(list_of_lists))


def distinct(items: Iterable[T]) -> List[T]:
    return list(set(items))


def is_distinct(seq: List[T], key: Callable[[T], Any] = lambda x: x) -> bool:
    return len(set(map(key, seq))) == len(seq)


def is_iterable(obj: Any) -> bool:
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def all_same_type(seq: Iterable) -> bool:
    return same(type(i) for i in seq)


def same(seq: Iterable) -> bool:
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

    today_year = date.today().year

    if not year_list:
        year = today_year
    else:
        year = year_list[0]

    if year <= today_year:
        year += 2000
    elif year < 100:
        year += 1900

    return date(year, month, day)


def random_date(start: time, end: time, count: int):
    today = date.today()

    time_delta = datetime.combine(today, end) - datetime.combine(today, start)
    minutes_delta = int(time_delta.total_seconds() / 60) - 1

    start_in_minutes = start.hour * 60 + start.minute

    for _ in range(count):
        time_in_minutes = start_in_minutes + random.randint(0, minutes_delta)

        result = time(hour=time_in_minutes // 60, minute=time_in_minutes % 60)

        yield result


def group_by(key: Callable[[T], V], seq: Iterable[T]) -> Dict[V, List[T]]:
    mapping = defaultdict(lambda: [])

    for i in seq:
        mapping[key(i)].append(i)

    return mapping


def stride(seq: Iterable[T], step: int) -> Iterable[Iterable[T]]:
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


def first(seq: Iterable[T], key: Callable[[T], bool] = lambda x: x, default: T = None) -> T | None:
    for i in seq:
        if key(i):
            return i

    return default


def bfs(start: T, provider: Callable[[T], Iterable[T]]) -> None:
    roots = [start]

    while roots:
        roots += provider(roots.pop(0))


def get_prefixes(s: str, separator: str) -> List[str]:
    prefixes = []
    split = s.split(separator)

    for i in range(1, len(split) + 1):
        prefixes.append(separator.join(split[:i]))

    return prefixes


def merge_dicts(merger: Callable[[V, V], V], *dicts: Dict[T, V]) -> Dict[T, V]:
    result = {}

    for d in dicts:
        for key in d:
            if key in result:
                result[key] = merger(result[key], d[key])
            else:
                result[key] = d[key]

    return result

