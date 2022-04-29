import glob
import random
import string
from abc import ABC, abstractmethod
from argparse import Namespace
from dataclasses import dataclass
from math import log10
from pathlib import Path
from typing import List, Optional

from justin_utils.cli import Action, Context, Parameter, App, Command

SEPARATOR = "."


@dataclass
class Part:
    index: int
    name: Optional[str]

    path: Path

    @classmethod
    def from_path(cls, path: Path) -> 'Part':
        name_parts = path.name.split(SEPARATOR, maxsplit=1)

        index = int(name_parts[0])
        name = name_parts[1] if len(name_parts) == 2 else None

        return Part(
            index=index,
            name=name,
            path=path
        )

    @staticmethod
    def is_part(path: Path) -> bool:
        split_result = path.name.split(SEPARATOR)

        return len(split_result) > 0 and split_result[0].isdecimal()


# region main funcs


class PartsAction(Action, ABC):
    INDEX_START = 1

    @property
    def parameters(self) -> List[Parameter]:
        return super().parameters + [
            Parameter("root", nargs="?", default="."),
        ]

    def perform(self, args: Namespace, context: Context) -> None:
        pattern: str = args.root

        for str_path in glob.iglob(pattern):
            path = Path(str_path).absolute()
            parts = self.get_parts(path)

            self.perform_for_root(path, parts, args)

    @abstractmethod
    def perform_for_root(self, root: Path, parts: List[Part], args: Namespace):
        pass

    @staticmethod
    def get_parts(path: Path) -> List[Part]:
        existing_subfolders = [f for f in path.iterdir() if f.is_dir()]
        existing_parts = [f for f in existing_subfolders if Part.is_part(f)]
        struct_parts = [Part.from_path(part) for part in existing_parts]

        return struct_parts

    @staticmethod
    def dump_in_temp(root: Path, parts: List[Part]) -> List[Part]:
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

        return tmp_parts

    @staticmethod
    def to_padded_string(number: int, length: int, padding: str) -> str:
        number_len = (int(log10(number)) if number > 0 else 0) + 1

        parts = [padding] * (length - number_len) + [str(number)]

        return "".join(parts)

    @staticmethod
    def new_part_name(part: Part, new_index: int, max_index_length: int) -> str:
        new_name_parts = [
            PartsAction.to_padded_string(new_index, max_index_length, "0"),
            part.name
        ]

        new_name_parts = [i for i in new_name_parts if i]
        new_name = SEPARATOR.join(new_name_parts)

        return new_name

    @staticmethod
    def index_length(index: int) -> int:
        if index == 0:
            return 1
        return int(log10(index)) + 1


class MakeAction(PartsAction):
    @property
    def parameters(self) -> List[Parameter]:
        return super().parameters + [
            Parameter("count", type=int)
        ]

    def perform_for_root(self, root: Path, parts: List[Part], args: Namespace):
        count = args.count

        existing_indices = {part.index for part in parts}

        max_index_length = self.index_length(count)

        for index in range(count):
            index += self.INDEX_START

            if index in existing_indices:
                continue

            part_name = self.to_padded_string(index, max_index_length, "0")

            part_path = root / part_name

            assert not part_path.exists()

            part_path.mkdir(parents=True)


class RenumberAction(PartsAction):

    @property
    def parameters(self) -> List[Parameter]:
        return super().parameters + [
            Parameter(flags=["-w", "--width"], type=int, default=None)
        ]

    def perform_for_root(self, root: Path, parts: List[Part], args: Namespace):

        parts_count = len(parts)

        parts.sort(key=lambda x: x.index)

        parts = self.dump_in_temp(root, parts)

        max_index_length = self.index_length(parts_count)

        if args.width is not None:
            max_index_length = max(max_index_length, args.width)

        for index, part in enumerate(parts, start=RenumberAction.INDEX_START):
            new_name = self.new_part_name(part, index, max_index_length)

            new_path = root / new_name

            part.path.rename(new_path)


class OffsetAction(PartsAction):

    @property
    def parameters(self) -> List[Parameter]:
        return super().parameters + [
            Parameter("offset", type=int),
            Parameter(flags=["-w", "--width"], type=int, default=None),
        ]

    def perform_for_root(self, root: Path, parts: List[Part], args: Namespace):
        parts = self.get_parts(root)

        if not parts:
            return

        offset: int = args.offset

        indices = [part.index for part in parts]

        assert min(indices) + offset >= 0

        max_index = max(indices) + offset
        max_index_length = self.index_length(max_index)

        if args.width is not None:
            max_index_length = max(max_index_length, args.width)

        parts = self.dump_in_temp(root, parts)

        for part in reversed(parts):
            new_index = part.index + offset

            new_name = self.new_part_name(part, new_index, max_index_length)

            new_path = root / new_name

            part.path.rename(new_path)


# endregion main funcs


def __run():
    App([
        Command("make", [MakeAction()]),
        Command("renumber", [RenumberAction()]),
        Command("offset", [OffsetAction()])
    ]).run()
