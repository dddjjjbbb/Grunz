"""Integration test: full detection pipeline with real PytorchWildlife model.

Requires PytorchWildlife installed and ~500MB model download on first run.
Run with: pytest tests/test_integration.py -m integration
"""

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def sample_image(tmp_path_factory):
    path = tmp_path_factory.mktemp("images") / "test.jpg"
    img = Image.fromarray(
        np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    )
    img.save(path)
    return str(path)


@pytest.fixture(scope="module")
def detector():
    from grunz.detector import create_detector

    return create_detector()


class TestFullPipeline:

    def test_single_image_detection_returns_dict(self, detector, sample_image):
        result = detector.single_image_detection(sample_image)
        assert isinstance(result, dict)
        assert "img_id" in result
        assert "detections" in result

    def test_convert_result_produces_valid_json(self, detector, sample_image):
        from grunz.detector import convert_result

        pw_result = detector.single_image_detection(sample_image)
        converted = convert_result(pw_result)

        assert "file" in converted
        assert "max_detection_conf" in converted
        assert "detections" in converted
        assert isinstance(converted["detections"], list)

        # Must be JSON-serializable
        json_str = json.dumps(converted)
        parsed = json.loads(json_str)
        assert parsed["file"] == converted["file"]

    def test_json_output_parseable_by_post_pro(self, detector, sample_image):
        from grunz.detector import convert_result

        pw_result = detector.single_image_detection(sample_image)
        converted = convert_result(pw_result)

        output = {"images": [converted]}
        json_str = json.dumps(output)
        parsed = json.loads(json_str)

        image = parsed["images"][0]
        assert isinstance(image["file"], str)
        assert isinstance(image["max_detection_conf"], (int, float))
        assert isinstance(image["detections"], list)

        for detection in image["detections"]:
            assert isinstance(detection["category"], str)
            assert isinstance(detection["conf"], (int, float))
            assert isinstance(detection["bbox"], list)
            assert len(detection["bbox"]) == 4
            # category must be castable to int (JSONParser does int(category))
            int(detection["category"])
