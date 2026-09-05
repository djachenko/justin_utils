import io
import struct
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import IO, ClassVar, Self, TypeAlias

from PIL import Image as ImageModule
from PIL.ExifTags import IFD, Base
from PIL.Image import Image as PilImage

from justin_utils.util import first

ImageSource: TypeAlias = Path | IO[bytes]


class Container(ABC):
    @abstractmethod
    def read(self, path: Path) -> ImageSource | None:
        pass


class RafContainer(Container):
    # Pillow не открывает RAF, но внутри лежит полноразмерный JPEG-превью,
    # смещение и длина которого записаны в заголовке контейнера
    __MAGIC: ClassVar[bytes] = b"FUJIFILMCCD-RAW "
    __JPEG_HEADER_OFFSET: ClassVar[int] = 84

    def read(self, path: Path) -> ImageSource | None:
        with path.open("rb") as file:
            if file.read(len(self.__MAGIC)) != self.__MAGIC:
                return None

            file.seek(self.__JPEG_HEADER_OFFSET)

            offset, length = struct.unpack(">II", file.read(8))

            file.seek(offset)

            return io.BytesIO(file.read(length))


class PlainContainer(Container):
    def read(self, path: Path) -> ImageSource | None:
        return path


class Exif:
    __DATE_FORMAT: ClassVar[str] = "%Y:%m:%d %H:%M:%S"

    __CONTAINERS: ClassVar[list[Container]] = [
        RafContainer(),
        PlainContainer(),
    ]

    def __init__(self, date_taken: datetime) -> None:
        super().__init__()

        self.date_taken = date_taken

    def __lt__(self, other: 'Exif') -> bool:
        return self.date_taken < other.date_taken

    @classmethod
    def from_path(cls, path: Path) -> Self | None:
        try:
            source = first(container.read(path) for container in cls.__CONTAINERS)

            if source is None:
                return None

            # теги читаются лениво, поэтому разбор обязан уложиться в открытую картинку
            with ImageModule.open(source) as image:
                return cls.__from_image(image)
        except OSError:
            return None

    @classmethod
    def __from_image(cls, image: PilImage) -> Self | None:
        date_string = image.getexif().get_ifd(IFD.Exif).get(Base.DateTimeOriginal)

        if date_string is None:
            return None

        if not isinstance(date_string, str):
            return None

        try:
            return cls(datetime.strptime(date_string, cls.__DATE_FORMAT))  # noqa: DTZ007
        except ValueError:
            return None


def parse_exif(path: Path) -> Exif | None:
    if path.is_dir():
        return None

    return Exif.from_path(path)


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
