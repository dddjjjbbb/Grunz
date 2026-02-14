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
                max_detection_conf = image["max_detection_conf"]
                category = image["detections"][0]["category"]

                if JSONParser.is_confidence_rating_minimum_or_above(
                    max_detection_conf
                ) and JSONParser.is_category_of_type_animal(category):
                    animals.append(image)
        return animals

    @staticmethod
    def get_file_paths_for_sort(list_of_detection_dicts: [Dict]) -> List:
        """
        :param list_of_detection_dicts: A list of dicts, i.e image objects containing animals..
        :return: A list of file paths for each positive result.
        """
        return [d["file"] for d in list_of_detection_dicts]

    @staticmethod
    def __convert_jpeg_path_to_original_avi(jpeg_path: str) -> str:
        """
        A helper method to be used in `get_list_for_sort`.
        :param jpeg_path: Path to positive jpeg.
        :return: The path to the video from which the jpeg derives.
        """
        original_dir = f"{Path(jpeg_path).parent}"
        jpeg_path = jpeg_path.split("/")[-1]
        avi_path = re.search(r"PICT\d*\.AVI", jpeg_path).group(0)
        return Path(f"{original_dir}/{avi_path}")

    @staticmethod
    def get_list_for_sort(jpeg_paths: List) -> List:
        """
        :param jpeg_paths: A list of positive jpeg detention results.
        :return: A list of paths which correspond to the avi file the jpeg was taken from.
        """
        return [JSONParser.__convert_jpeg_path_to_original_avi(p) for p in jpeg_paths]
