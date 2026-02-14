"""Contract tests: does convert_result output flow correctly through JSONParser?

The repo's core purpose is classifying videos containing animals vs those
without. These tests verify that the format produced by convert_result() is
correctly consumed by JSONParser to make that classification decision.
"""

import json
from pathlib import Path

from grunz.json_parser.json_parser import JSONParser


def _write_detection_json(tmp_path, images):
    """Write a detection JSON file in the format pre_pro produces."""
    output_path = tmp_path / "detections.json"
    output_path.write_text(json.dumps({"images": images}))
    return str(output_path)


def _make_image_result(file_path, category, confidence, bbox=None):
    """Build an image result dict matching convert_result() output format."""
    if bbox is None:
        bbox = [10.0, 20.0, 100.0, 200.0]

    return {
        "file": file_path,
        "max_detection_conf": confidence,
        "detections": [
            {
                "category": str(category),
                "conf": confidence,
                "bbox": bbox,
            }
        ],
    }


class TestAnimalClassification:
    """Verify JSONParser correctly identifies animal detections from convert_result output."""

    def test_high_confidence_animal_is_classified_as_positive(self, tmp_path):
        image = _make_image_result("data/PICT0001.AVI-001.jpeg", category=1, confidence=0.92)
        json_path = _write_detection_json(tmp_path, [image])

        parser = JSONParser(json_path)
        results = parser.filter_json_for_detection_results()

        assert len(results) == 1
        assert results[0]["file"] == "data/PICT0001.AVI-001.jpeg"

    def test_animal_at_exact_threshold_is_classified_as_positive(self, tmp_path):
        image = _make_image_result("data/PICT0002.AVI-001.jpeg", category=1, confidence=0.850)
        json_path = _write_detection_json(tmp_path, [image])

        parser = JSONParser(json_path)
        results = parser.filter_json_for_detection_results()

        assert len(results) == 1

    def test_animal_below_threshold_is_filtered_out(self, tmp_path):
        image = _make_image_result("data/PICT0003.AVI-001.jpeg", category=1, confidence=0.80)
        json_path = _write_detection_json(tmp_path, [image])

        parser = JSONParser(json_path)
        results = parser.filter_json_for_detection_results()

        assert len(results) == 0


class TestNonAnimalFiltering:
    """Verify JSONParser rejects non-animal categories."""

    def test_person_detection_is_filtered_out(self, tmp_path):
        image = _make_image_result("data/PICT0004.AVI-001.jpeg", category=2, confidence=0.95)
        json_path = _write_detection_json(tmp_path, [image])

        parser = JSONParser(json_path)
        results = parser.filter_json_for_detection_results()

        assert len(results) == 0

    def test_vehicle_detection_is_filtered_out(self, tmp_path):
        image = _make_image_result("data/PICT0005.AVI-001.jpeg", category=3, confidence=0.99)
        json_path = _write_detection_json(tmp_path, [image])

        parser = JSONParser(json_path)
        results = parser.filter_json_for_detection_results()

        assert len(results) == 0


class TestEmptyDetections:
    """Verify JSONParser handles images with no detections."""

    def test_empty_detections_produce_no_results(self, tmp_path):
        image = {
            "file": "data/PICT0006.AVI-001.jpeg",
            "max_detection_conf": 0.0,
            "detections": [],
        }
        json_path = _write_detection_json(tmp_path, [image])

        parser = JSONParser(json_path)
        results = parser.filter_json_for_detection_results()

        assert len(results) == 0


class TestMixedResults:
    """Verify JSONParser correctly separates animals from non-animals in a batch."""

    def test_only_animals_above_threshold_are_returned(self, tmp_path):
        images = [
            _make_image_result("data/PICT0010.AVI-001.jpeg", category=1, confidence=0.92),
            _make_image_result("data/PICT0011.AVI-001.jpeg", category=2, confidence=0.95),
            _make_image_result("data/PICT0012.AVI-001.jpeg", category=1, confidence=0.50),
            {
                "file": "data/PICT0013.AVI-001.jpeg",
                "max_detection_conf": 0.0,
                "detections": [],
            },
            _make_image_result("data/PICT0014.AVI-001.jpeg", category=1, confidence=0.88),
        ]
        json_path = _write_detection_json(tmp_path, images)

        parser = JSONParser(json_path)
        results = parser.filter_json_for_detection_results()

        assert len(results) == 2
        result_files = [r["file"] for r in results]
        assert "data/PICT0010.AVI-001.jpeg" in result_files
        assert "data/PICT0014.AVI-001.jpeg" in result_files
