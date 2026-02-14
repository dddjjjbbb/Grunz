"""Tests for safe path handling in json_parser."""

from grunz.json_parser.json_parser import JSONParser

import pytest


class TestConvertJpegPathToAvi:
    """__convert_jpeg_path_to_original_avi must handle non-matching filenames safely."""

    def test_non_matching_filename_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot extract AVI filename"):
            JSONParser.convert_jpeg_paths_to_avi_paths(["some/path/random_image.jpeg"])

    def test_matching_filename_still_works(self):
        result = JSONParser.convert_jpeg_paths_to_avi_paths(["some/path/PICT0001.AVI-001.jpeg"])
        assert len(result) == 1
        assert "PICT0001.AVI" in str(result[0])
