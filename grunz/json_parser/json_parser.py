"""This module handles parsing the JSON output file after camera traps have been processed."""

import json
import re
from enum import Enum
from pathlib import Path
from typing import Dict, List


class ConfidenceRating(Enum):
    """Confidence rating value of model."""

    MINIMUM = 0.850


class Categories(Enum):
    """Categories available for detection."""

    ANIMAL = 1
    PERSON = 2
    VEHICLE = 3


class JSONParser:
    """This class is responsible for parsing JSON to distinguish + and - detection results."""

    def __init__(self, path_to_json):

        self.path_to_json = path_to_json

    def read(self) -> Dict:
        """
        :return: deserialized JSON object.
        """
        with open(self.path_to_json, "r") as source:
            return json.load(source)

    @staticmethod
    def is_confidence_rating_minimum_or_above(confidence_rating: float) -> bool:
        """
        :param confidence_rating: 85% is the default.
        :return: A bool representing if the confidence value of a detection is >= percentage.
        """
        return confidence_rating >= ConfidenceRating.MINIMUM.value

    @staticmethod
    def is_category_of_type_animal(category: str) -> bool:
        """
        :param category: One of three values listed in the `Categories` enum.
        Please note: Despite each category being represented as an int,
        each category is a string in the JSON itself. This is why we cast before comparison.
        :return: A bool representing if the category, i.e the image is of type "Animal".
        """
        return int(category) == Categories.ANIMAL.value

    def filter_json_for_detection_results(self) -> List[Dict]:
        """
        :return: A list of detection results.
        """
        animals = []
        mega_detector_json = JSONParser.read(self)
        images = mega_detector_json["images"]

        for image in images:
            detections = image["detections"]

            if detections:
                has_animal = any(
                    JSONParser.is_category_of_type_animal(d["category"])
                    and JSONParser.is_confidence_rating_minimum_or_above(d["conf"])
                    for d in detections
                )
                if has_animal:
                    animals.append(image)
        return animals

    @staticmethod
    def extract_file_paths(detection_results: List[Dict]) -> List[str]:
        """
        :param detection_results: A list of dicts, i.e image objects containing animals.
        :return: A list of file paths for each positive result.
        """
        return [d["file"] for d in detection_results]

    @staticmethod
    def __convert_jpeg_path_to_original_avi(jpeg_path: str) -> Path:
        """
        :param jpeg_path: Path to positive jpeg.
        :return: The path to the video from which the jpeg derives.
        """
        original_dir = f"{Path(jpeg_path).parent}"
        filename = jpeg_path.split("/")[-1]
        match = re.search(r"PICT\d*\.AVI", filename)
        if match is None:
            raise ValueError(
                f"Cannot extract AVI filename from '{jpeg_path}': "
                f"expected pattern PICT<digits>.AVI"
            )
        return Path(f"{original_dir}/{match.group(0)}")

    @staticmethod
    def convert_jpeg_paths_to_avi_paths(jpeg_paths: List[str]) -> List[Path]:
        """
        :param jpeg_paths: A list of positive jpeg detection result paths.
        :return: A list of paths which correspond to the AVI file each jpeg was taken from.
        """
        return [JSONParser.__convert_jpeg_path_to_original_avi(p) for p in jpeg_paths]
