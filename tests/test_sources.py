from unittest.mock import patch

import pytest

from justin_utils.filesystem import File
from justin_utils.sources import ExternalMetadataSource, InternalMetadataSource, parse_sources


def _file(temp_dir, name: str) -> File:
    path = temp_dir / name
    path.touch()

    return File(path)


class TestInternalMetadataSource:
    def test_name_is_stem(self, temp_dir):
        source = InternalMetadataSource(_file(temp_dir, "photo.jpg"))

        assert source.name == "photo"

    def test_files_returns_single_file(self, temp_dir):
        file = _file(temp_dir, "photo.jpg")
        source = InternalMetadataSource(file)

        assert source.files() == [file]

    def test_mtime_delegates_to_file(self, temp_dir):
        file = _file(temp_dir, "photo.jpg")
        source = InternalMetadataSource(file)

        assert source.mtime == file.mtime

    def test_exif_delegates_to_parse_exif(self, temp_dir):
        file = _file(temp_dir, "photo.jpg")
        source = InternalMetadataSource(file)

        with patch("justin_utils.sources.parse_exif") as mock_parse:
            mock_parse.return_value = "exif-result"

            assert source.exif == "exif-result"
            mock_parse.assert_called_once_with(file.path)


class TestExternalMetadataSource:
    def test_name_is_raw_stem(self, temp_dir):
        raw = _file(temp_dir, "photo.nef")
        metadata = _file(temp_dir, "photo.xmp")

        source = ExternalMetadataSource(raw, metadata)

        assert source.name == "photo"

    def test_files_includes_metadata_when_present(self, temp_dir):
        raw = _file(temp_dir, "photo.nef")
        metadata = _file(temp_dir, "photo.xmp")

        source = ExternalMetadataSource(raw, metadata)

        assert source.files() == [raw, metadata]

    def test_files_excludes_missing_metadata(self, temp_dir):
        raw = _file(temp_dir, "photo.nef")

        source = ExternalMetadataSource(raw, None)

        assert source.files() == [raw]

    def test_mtime_uses_metadata_when_present(self, temp_dir):
        raw = _file(temp_dir, "photo.nef")
        metadata = _file(temp_dir, "photo.xmp")

        source = ExternalMetadataSource(raw, metadata)

        assert source.mtime == metadata.mtime

    def test_mtime_is_minus_one_without_metadata(self, temp_dir):
        raw = _file(temp_dir, "photo.nef")

        source = ExternalMetadataSource(raw, None)

        assert source.mtime == -1

    def test_jpg_raw_asserts(self, temp_dir):
        raw = _file(temp_dir, "photo.jpg")

        with pytest.raises(AssertionError):
            ExternalMetadataSource(raw, None)

    def test_mismatched_stems_assert(self, temp_dir):
        raw = _file(temp_dir, "photo.nef")
        metadata = _file(temp_dir, "other.xmp")

        with pytest.raises(AssertionError):
            ExternalMetadataSource(raw, metadata)


class TestParseSources:
    @pytest.mark.parametrize("raw_extension, metadata_extension", [
        (".nef", ".xmp"),
        (".NEF", ".XMP"),
        (".Nef", ".Xmp"),
        (".nef", ".XMP"),
    ])
    def test_pairs_raw_with_matching_metadata(self, temp_dir, raw_extension, metadata_extension):
        files = [_file(temp_dir, f"a{raw_extension}"), _file(temp_dir, f"a{metadata_extension}")]

        sources = parse_sources(files)

        assert len(sources) == 1
        assert isinstance(sources[0], ExternalMetadataSource)
        assert sources[0].name == "a"
        assert sources[0].metadata is not None

    def test_raw_without_metadata_still_included(self, temp_dir):
        files = [_file(temp_dir, "a.nef")]

        sources = parse_sources(files)

        assert len(sources) == 1
        assert isinstance(sources[0], ExternalMetadataSource)
        assert sources[0].metadata is None

    @pytest.mark.parametrize("extension", [".jpg", ".JPG", ".Jpg"])
    def test_jpg_becomes_internal_source(self, temp_dir, extension):
        files = [_file(temp_dir, f"a{extension}")]

        sources = parse_sources(files)

        assert len(sources) == 1
        assert isinstance(sources[0], InternalMetadataSource)

    def test_mixed_sources(self, temp_dir):
        files = [
            _file(temp_dir, "a.nef"),
            _file(temp_dir, "a.xmp"),
            _file(temp_dir, "b.jpg"),
        ]

        sources = parse_sources(files)

        assert len(sources) == 2
        names = {source.name for source in sources}
        assert names == {"a", "b"}
