"""Tests for configurable output paths in file_utils and main."""

from pathlib import Path

from grunz.file_utils.file_utils import FileUtils


class TestCreateJsonOutputFile:
    """create_json_output_file should write to the specified directory."""

    def test_creates_file_in_specified_directory(self, tmp_path):
        file_utils = FileUtils(tmp_path)
        result = file_utils.create_json_output_file(output_dir=tmp_path)
        result_path = Path(result)

        assert result_path.exists()
        assert result_path.parent == tmp_path
