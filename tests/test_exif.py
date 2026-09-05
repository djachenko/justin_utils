import struct
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image as ImageModule
from PIL import UnidentifiedImageError
from PIL.ExifTags import IFD, Base

from justin_utils.exif import Exif, PlainContainer, RafContainer, parse_exif

# DateTimeOriginal = 36867, DateTime = 306 (PIL ExifTags)
_DATE_STR = "2024:03:15 10:30:00"
_EXPECTED_DT = datetime(2024, 3, 15, 10, 30, 0)  # noqa: DTZ001

_RAF_MAGIC = b"FUJIFILMCCD-RAW "
_RAF_JPEG_HEADER_OFFSET = 84


def _raf_bytes(payload):
    header = _RAF_MAGIC.ljust(_RAF_JPEG_HEADER_OFFSET, b"\0")
    offset = _RAF_JPEG_HEADER_OFFSET + 8

    return header + struct.pack(">II", offset, len(payload)) + payload + b"raw sensor data"


@pytest.fixture
def image_path(tmp_path):
    path = tmp_path / "image.jpg"
    path.write_bytes(b"not a raf")

    return path


@pytest.fixture
def jpeg_path(tmp_path):
    exif = ImageModule.Exif()
    exif.get_ifd(IFD.Exif)[Base.DateTimeOriginal] = _DATE_STR

    path = tmp_path / "real.jpg"
    ImageModule.new("RGB", (1, 1)).save(path, format="JPEG", exif=exif)

    return path


@pytest.fixture
def raf_path(tmp_path):
    payload = b"embedded jpeg bytes"

    path = tmp_path / "image.raf"
    path.write_bytes(_raf_bytes(payload))

    return path, payload


def _source(shooting_exif=None):
    image = MagicMock()
    image.getexif.return_value = MagicMock(get_ifd=lambda tag: shooting_exif or {})
    image.__enter__.return_value = image

    return patch("justin_utils.exif.ImageModule.open", return_value=image)


class TestFromPath:
    def test_reads_datetime_original(self, image_path):
        with _source(shooting_exif={36867: _DATE_STR}):
            exif = Exif.from_path(image_path)

        assert exif is not None
        assert exif.date_taken == _EXPECTED_DT

    def test_ignores_datetime(self, image_path):
        with _source(shooting_exif={306: _DATE_STR}):
            assert Exif.from_path(image_path) is None

    def test_returns_none_without_datetime_original(self, image_path):
        with _source():
            assert Exif.from_path(image_path) is None

    def test_returns_none_on_malformed_date(self, image_path):
        with _source(shooting_exif={36867: "not a date"}):
            assert Exif.from_path(image_path) is None

    @pytest.mark.parametrize("error", [
        UnidentifiedImageError("unreadable"),
        OSError("unreadable"),
    ])
    def test_returns_none_when_unreadable(self, image_path, error):
        with patch("justin_utils.exif.ImageModule.open", side_effect=error):
            assert Exif.from_path(image_path) is None


class TestContainers:
    def test_raf_reads_embedded_jpeg_slice(self, raf_path):
        path, payload = raf_path

        assert RafContainer().read(path).getvalue() == payload

    def test_raf_skips_other_formats(self, image_path):
        assert RafContainer().read(image_path) is None

    def test_plain_returns_path_itself(self, image_path):
        assert PlainContainer().read(image_path) is image_path

    def test_raf_skips_truncated_header(self, tmp_path):
        path = tmp_path / "truncated.raf"
        path.write_bytes(_RAF_MAGIC + b"\0" * 40)

        assert RafContainer().read(path) is None

    def test_raf_read_is_repeatable(self, raf_path):
        path, payload = raf_path
        container = RafContainer()

        assert container.read(path).getvalue() == payload
        assert container.read(path).getvalue() == payload

    def test_unreadable_file_gives_none(self, image_path):
        with patch("justin_utils.exif.ImageModule.open", side_effect=UnidentifiedImageError("nope")):
            assert Exif.from_path(image_path) is None

    def test_raf_is_selected_for_raf(self, raf_path):
        path, payload = raf_path

        with _source(shooting_exif={36867: _DATE_STR}) as open_mock:
            exif = Exif.from_path(path)

        assert exif is not None
        assert exif.date_taken == _EXPECTED_DT
        assert open_mock.call_args.args[0].getvalue() == payload


class TestRealFiles:
    def test_reads_jpeg(self, jpeg_path):
        exif = Exif.from_path(jpeg_path)

        assert exif is not None
        assert exif.date_taken == _EXPECTED_DT

    def test_reads_raf(self, tmp_path, jpeg_path):
        path = tmp_path / "real.raf"
        path.write_bytes(_raf_bytes(jpeg_path.read_bytes()))

        exif = Exif.from_path(path)

        assert exif is not None
        assert exif.date_taken == _EXPECTED_DT

    def test_returns_none_for_non_image(self, tmp_path):
        path = tmp_path / "_meta.json"
        path.write_text('{"not": "an image"}')

        assert Exif.from_path(path) is None

    def test_returns_none_for_truncated_raf(self, tmp_path):
        path = tmp_path / "truncated.raf"
        path.write_bytes(_RAF_MAGIC + b"\0" * 40)

        assert parse_exif(path) is None


class TestParseExif:
    def test_returns_none_for_directory(self, tmp_path):
        assert parse_exif(tmp_path) is None

    def test_delegates_to_exif(self, image_path):
        with _source(shooting_exif={36867: _DATE_STR}):
            exif = parse_exif(image_path)

        assert exif is not None
        assert exif.date_taken == _EXPECTED_DT
