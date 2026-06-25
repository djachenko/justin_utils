from abc import abstractmethod, ABC
from datetime import datetime
from functools import cache
from pathlib import Path
from typing import Iterable, Self

from exif import Image

from PIL import ExifTags
from PIL.Image import Exif as PilExif
from PIL import Image as ImageModule

class Exif(ABC):
    @property
    @abstractmethod
    def date_taken(self) -> datetime:
        pass

    def __lt__(self, other: 'Exif') -> bool:
        return self.date_taken < other.date_taken

    @classmethod
    def from_path(cls, path: Path) -> Self:
        pass


class PillowExif(Exif):
    __reverse_mapping = {v: k for k, v in ExifTags.TAGS.items()}

    @property
    @cache
    def date_taken(self) -> datetime:
        return datetime.strptime(
            self.__get_tag_value("DateTimeOriginal") or self.__get_tag_value("DateTime"),
            "%Y:%m:%d %H:%M:%S"
        )

    def __get_tag_value(self, tag: str) -> str | None:
        return self.source_exif.get(PillowExif.__reverse_mapping[tag])

    def __init__(self, exif: PilExif) -> None:
        super().__init__()

        self.source_exif = exif

    @classmethod
    def from_path(cls, path: Path) -> Self:
        return PillowExif(ImageModule.open(path).getexif())


class NativeExif(Exif):
    @property
    @cache
    def date_taken(self) -> datetime:
        if hasattr(self.source_exif, "datetime_original"):
            return datetime.strptime(
                self.source_exif.datetime_original,
                "%Y:%m:%d %H:%M:%S"
            )
        elif hasattr(self.source_exif, "datetime_digitized"):
            return datetime.strptime(
                self.source_exif.datetime_digitized,
                "%Y:%m:%d %H:%M:%S"
            )
        else:
            assert False

    def __init__(self, exif: Image) -> None:
        super().__init__()

        self.source_exif = exif

    @classmethod
    def from_path(cls, path: Path) -> Self:
        with path.open("rb") as image_file:
            my_image = Image(image_file)

            return NativeExif(my_image)


def parse_exif(path: Path) -> Exif | None:
    if path is None:
        return None

    if path.is_dir():
        return None

    suffix = path.suffix.lower()

    if suffix in [".nef", ".dng", ]:
        exif_class = PillowExif
    elif suffix in [".jpg", ]:
        exif_class = NativeExif
    else:
        return None

    return exif_class.from_path(path)


def exif_sorted(seq: Iterable[Path]) -> Iterable[Path]:
    class Comparator:
        def __init__(self, path: Path) -> None:
            super().__init__()

            self.exif = parse_exif(path)
            self.name = path.name

        def __lt__(self, other: 'Comparator') -> bool:
            if other.exif and self.exif:
                return self.exif.date_taken < other.exif.date_taken

            return self.name < other.name

    return sorted(seq, key=Comparator)
