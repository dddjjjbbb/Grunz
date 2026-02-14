"""Tests for grunz/json_parser/json_parser.py — JSON parsing and filtering."""

import json

from grunz.json_parser.json_parser import JSONParser


class TestFilterDetectionResults:
    """filter_json_for_detection_results must not accumulate state across calls."""

    def test_second_call_does_not_include_first_call_results(self, tmp_path):
        images_a = [
            {
                "file": "a.jpeg",
                "max_detection_conf": 0.95,
                "detections": [{"category": "1", "conf": 0.95, "bbox": [0, 0, 1, 1]}],
            }
        ]
        images_b = [
            {
                "file": "b.jpeg",
                "max_detection_conf": 0.90,
                "detections": [{"category": "1", "conf": 0.90, "bbox": [0, 0, 1, 1]}],
            }
        ]

        path_a = tmp_path / "a.json"
        path_a.write_text(json.dumps({"images": images_a}))
        path_b = tmp_path / "b.json"
        path_b.write_text(json.dumps({"images": images_b}))

        parser = JSONParser(str(path_a))
        result_a = parser.filter_json_for_detection_results()
        assert len(result_a) == 1

        parser.path_to_json = str(path_b)
        result_b = parser.filter_json_for_detection_results()

        assert len(result_b) == 1, (
            f"Expected 1 result from second call, got {len(result_b)}. "
            "filter_json_for_detection_results is accumulating state across calls."
        )
