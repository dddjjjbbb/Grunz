"""Tests for ffmpeg failure logging in pre_pro pipeline."""

import logging
from unittest.mock import MagicMock, patch

from main import pre_pro


class TestFfmpegFailureLogging:
    """When ffmpeg fails to parse a video, the failure must be logged, not just printed."""

    @patch("main.create_detector")
    @patch("main.Splitter")
    @patch("main.FileUtils")
    def test_ioerror_during_split_is_logged_as_error(
        self, mock_file_utils_cls, mock_splitter_cls, mock_create_detector, tmp_path, caplog
    ):
        mock_fu = MagicMock()
        mock_fu.find_files_recursively.side_effect = [
            ["/videos/PICT0001.AVI"],
            [],
        ]
        mock_fu.create_json_output_file.return_value = str(tmp_path / "out.json")
        mock_file_utils_cls.return_value = mock_fu

        mock_splitter = MagicMock()
        mock_splitter.export_frames_to_jpeg.side_effect = IOError("corrupt file")
        mock_splitter_cls.return_value = mock_splitter

        mock_detector = MagicMock()
        mock_create_detector.return_value = mock_detector

        with caplog.at_level(logging.ERROR):
            pre_pro(str(tmp_path))

        assert any("PICT0001.AVI" in record.message and record.levelno == logging.ERROR for record in caplog.records)

    @patch("main.create_detector")
    @patch("main.Splitter")
    @patch("main.FileUtils")
    def test_ioerror_does_not_stop_remaining_videos(
        self, mock_file_utils_cls, mock_splitter_cls, mock_create_detector, tmp_path, caplog
    ):
        mock_fu = MagicMock()
        mock_fu.find_files_recursively.side_effect = [
            ["/videos/PICT0001.AVI", "/videos/PICT0002.AVI"],
            [],
        ]
        mock_fu.create_json_output_file.return_value = str(tmp_path / "out.json")
        mock_file_utils_cls.return_value = mock_fu

        splitter_a = MagicMock()
        splitter_a.export_frames_to_jpeg.side_effect = IOError("corrupt")
        splitter_b = MagicMock()
        mock_splitter_cls.side_effect = [splitter_a, splitter_b]

        mock_create_detector.return_value = MagicMock()

        with caplog.at_level(logging.ERROR):
            pre_pro(str(tmp_path))

        splitter_b.export_frames_to_jpeg.assert_called_once()
