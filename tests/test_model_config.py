"""Tests MegaDetector migration from manual .pb download to PytorchWildlife.

The old approach required manually downloading md_v4.1.0.pb from
Azure blob storage (now dead). The new approach uses PytorchWildlife which
auto-downloads MegaDetectorV6 weights on first use.
"""

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestDetectorWrapper:
    """Verify the detector module wraps PytorchWildlife correctly."""

    def _import_create_detector(self):
        # Force re-import so the mock takes effect.
        if "grunz.detector" in sys.modules:
            del sys.modules["grunz.detector"]

        mock_pw_detection = MagicMock()
        mock_model = MagicMock()
        mock_pw_detection.MegaDetectorV6.return_value = mock_model

        mock_pw_models = MagicMock()
        mock_pw_models.detection = mock_pw_detection

        sys.modules["PytorchWildlife"] = MagicMock()
        sys.modules["PytorchWildlife.models"] = mock_pw_models
        sys.modules["PytorchWildlife.models.detection"] = mock_pw_detection

        from grunz.detector import create_detector

        return create_detector, mock_pw_detection, mock_model

    def test_detector_module_exists(self):
        create_detector, _, _ = self._import_create_detector()
        assert callable(create_detector)

    def test_create_detector_returns_object_with_single_image_detection(self):
        create_detector, _, mock_model = self._import_create_detector()
        detector = create_detector()
        assert hasattr(detector, "single_image_detection")

    def test_create_detector_calls_megadetector_v6_with_version(self):
        create_detector, mock_pw, _ = self._import_create_detector()
        create_detector()
        mock_pw.MegaDetectorV6.assert_called_once_with(version="MDV6-yolov9-c")


class TestMainNoLongerUsesTensorflow:
    """Verify main.py no longer references the old TF-based detector."""

    def test_main_does_not_import_cameratraps(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        assert "from cameratraps" not in source
        assert "import cameratraps" not in source

    def test_main_does_not_glob_for_pb_files(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        assert "*.pb" not in source

    def test_main_imports_detector_from_grunz(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        assert "from grunz.detector" in source or "import grunz.detector" in source


class TestDetectionResultFormat:
    """Verify PytorchWildlife results convert to the format JSONParser expects.

    post_pro relies on each image dict having:
      - "file": str
      - "max_detection_conf": float
      - "detections": [{"category": str, "conf": float, "bbox": list}]
    """

    def _import_convert(self):
        if "grunz.detector" in sys.modules:
            del sys.modules["grunz.detector"]

        mock_pw_detection = MagicMock()
        mock_pw_models = MagicMock()
        mock_pw_models.detection = mock_pw_detection
        sys.modules["PytorchWildlife"] = MagicMock()
        sys.modules["PytorchWildlife.models"] = mock_pw_models
        sys.modules["PytorchWildlife.models.detection"] = mock_pw_detection

        from grunz.detector import convert_result

        return convert_result

    def _make_supervision_result(self):
        """Simulate what PytorchWildlife single_image_detection returns."""
        detections = MagicMock()
        detections.xyxy = np.array([[10.0, 20.0, 100.0, 200.0]])
        detections.confidence = np.array([0.92])
        detections.class_id = np.array([1])
        return {"img_id": "test/image.jpeg", "detections": detections}

    def test_converted_result_has_file_key(self):
        convert = self._import_convert()
        result = convert(self._make_supervision_result())
        assert "file" in result
        assert result["file"] == "test/image.jpeg"

    def test_converted_result_has_max_detection_conf(self):
        convert = self._import_convert()
        result = convert(self._make_supervision_result())
        assert "max_detection_conf" in result
        assert abs(result["max_detection_conf"] - 0.92) < 1e-6

    def test_converted_detections_have_category_conf_bbox(self):
        convert = self._import_convert()
        result = convert(self._make_supervision_result())
        assert len(result["detections"]) == 1
        detection = result["detections"][0]
        assert "category" in detection
        assert "conf" in detection
        assert "bbox" in detection

    def test_category_is_string(self):
        convert = self._import_convert()
        result = convert(self._make_supervision_result())
        assert isinstance(result["detections"][0]["category"], str)
        assert result["detections"][0]["category"] == "1"

    def test_empty_detections_produce_empty_list(self):
        convert = self._import_convert()
        empty = MagicMock()
        empty.xyxy = np.array([]).reshape(0, 4)
        empty.confidence = np.array([])
        empty.class_id = np.array([])
        result = convert({"img_id": "empty.jpeg", "detections": empty})
        assert result["detections"] == []
        assert result["max_detection_conf"] == 0.0
