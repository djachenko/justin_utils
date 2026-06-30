import glob
import random
import string
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from math import log10
from pathlib import Path

import typer

SEPARATOR = "."
INDEX_START = 1

app = typer.Typer()


@dataclass
class Part:
    index: int
    name: str | None

    path: Path

    @classmethod
    def from_path(cls, path: Path) -> "Part":
        name_parts = path.name.split(SEPARATOR, maxsplit=1)

        index = int(name_parts[0])

        if len(name_parts) == 2:
            name = name_parts[1]
        else:
            name = None

        return Part(
            index=index,
            name=name,
            path=path
        )

    @staticmethod
    def is_part(path: Path) -> bool:
        split_result = path.name.split(SEPARATOR)

        return len(split_result) > 0 and split_result[0].isdecimal()


def get_parts(path: Path) -> list[Part]:
    existing_subfolders = [f for f in path.iterdir() if f.is_dir()]
    existing_parts = [f for f in existing_subfolders if Part.is_part(f)]
    struct_parts = [Part.from_path(part) for part in existing_parts]

    return struct_parts


@contextmanager
def dump_in_temp(root: Path, parts: list[Part]) -> Iterator[list[Part]]:
    while True:
        tmp_folder_name = "".join(random.choices(string.digits + string.ascii_letters, k=10))

        tmp_folder_path = root / tmp_folder_name

        if not tmp_folder_path.exists():
            break

    tmp_folder_path.mkdir(parents=True)

    tmp_parts = []

    for part in parts:
        tmp_path = tmp_folder_path / part.path.name

        part.path.rename(tmp_path)

        tmp_parts.append(Part.from_path(tmp_path))

    try:
        yield tmp_parts
    finally:
        tmp_folder_path.rmdir()


def to_padded_string(number: int, length: int, padding: str) -> str:
    if number > 0:
        number_len = int(log10(number)) + 1
    else:
        number_len = 1

    parts = [padding] * (length - number_len) + [str(number)]

    return "".join(parts)


def new_part_name(part: Part, new_index: int, max_index_length: int) -> str:
    new_name_parts = [
        to_padded_string(new_index, max_index_length, "0"),
        part.name
    ]

    name_parts = [i for i in new_name_parts if i is not None]
    new_name = SEPARATOR.join(name_parts)

    return new_name


def index_length(index: int) -> int:
    if index == 0:
        return 1
    return int(log10(index)) + 1


def for_each_root(root_patterns: list[str], perform_for_root: Callable[[Path, list[Part]], None]) -> None:
    for pattern in root_patterns:
        for str_path in glob.iglob(pattern):
            path = Path(str_path).absolute()

            if not path.is_dir():
                continue

            perform_for_root(path, get_parts(path))


@app.command()
def make(count: int, root: list[str] = typer.Argument(["."])) -> None:
    def perform_for_root(root_path: Path, parts: list[Part]) -> None:
        existing_indices = {part.index for part in parts}

        max_index_length = index_length(count)

        for index in range(count):
            index += INDEX_START

            if index in existing_indices:
                continue

            part_name = to_padded_string(index, max_index_length, "0")

            part_path = root_path / part_name

            assert not part_path.exists()

            part_path.mkdir(parents=True)

    for_each_root(root, perform_for_root)


@app.command()
def renumber(root: list[str] = typer.Argument(["."]), width: int | None = typer.Option(None, "-w", "--width")) -> None:
    def perform_for_root(root_path: Path, parts: list[Part]) -> None:
        parts_count = len(parts)

        if parts_count == 1:
            part = parts[0]

            for item in part.path.iterdir():
                item.rename(root_path / item.name)

            part.path.rmdir()

            return

        parts.sort(key=lambda x: x.index)

        max_index_length = index_length(parts_count)

        if width is not None:
            max_index_length = max(max_index_length, width)

        with dump_in_temp(root_path, parts) as sorted_parts:
            for index, part in enumerate(sorted_parts, start=INDEX_START):
                new_name = new_part_name(part, index, max_index_length)

                new_path = root_path / new_name

                part.path.rename(new_path)

    for_each_root(root, perform_for_root)


@app.command()
def offset(offset: int, root: list[str] = typer.Argument(["."]), width: int | None = typer.Option(None, "-w", "--width")) -> None:
    def perform_for_root(root_path: Path, parts: list[Part]) -> None:
        if not parts:
            return

        indices = [part.index for part in parts]

        assert min(indices) + offset >= 0

        max_index = max(indices) + offset
        max_index_length = index_length(max_index)

        if width is not None:
            max_index_length = max(max_index_length, width)

        with dump_in_temp(root_path, parts) as shifted_parts:
            for part in reversed(shifted_parts):
                new_index = part.index + offset

                new_name = new_part_name(part, new_index, max_index_length)

                new_path = root_path / new_name

                part.path.rename(new_path)

    for_each_root(root, perform_for_root)


def __run() -> None:
    app()
