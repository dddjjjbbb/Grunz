"""Tests for multi-detection image handling in JSONParser."""

import json

from grunz.json_parser.json_parser import JSONParser


class TestMultiDetectionImages:
    """An image with multiple detections should check all of them, not just the first."""

    def test_animal_at_second_detection_is_found(self, tmp_path):
        """If the first detection is a person but the second is an animal, the image should match."""
        image = {
            "file": "data/PICT0001.AVI-001.jpeg",
            "max_detection_conf": 0.95,
            "detections": [
                {"category": "2", "conf": 0.95, "bbox": [0, 0, 1, 1]},
                {"category": "1", "conf": 0.90, "bbox": [2, 2, 3, 3]},
            ],
        }
        json_path = tmp_path / "multi.json"
        json_path.write_text(json.dumps({"images": [image]}))

        parser = JSONParser(str(json_path))
        results = parser.filter_json_for_detection_results()

        assert len(results) == 1, (
            "Image with animal as second detection was not included"
        )

    def test_no_animal_in_any_detection_is_filtered(self, tmp_path):
        """If no detection is an animal, the image should be excluded even with high confidence."""
        image = {
            "file": "data/PICT0002.AVI-001.jpeg",
            "max_detection_conf": 0.99,
            "detections": [
                {"category": "2", "conf": 0.99, "bbox": [0, 0, 1, 1]},
                {"category": "3", "conf": 0.95, "bbox": [2, 2, 3, 3]},
            ],
        }
        json_path = tmp_path / "no_animal.json"
        json_path.write_text(json.dumps({"images": [image]}))

        parser = JSONParser(str(json_path))
        results = parser.filter_json_for_detection_results()

        assert len(results) == 0
