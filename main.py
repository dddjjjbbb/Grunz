"""This is the main entry point for managing the pre and post processing
MegaDetector pipeline."""

import os
import argparse

from enum import Enum

from grunz.file_utils.file_utils import FileUtils
from grunz.splitter.splitter import Splitter
from grunz.json_parser.json_parser import JSONParser

from cameratraps.detection.run_tf_detector_batch import load_and_run_detector_batch, \
                                                        write_results_to_file

from pathlib import Path


class OneMinuteVideo(Enum):
    """Enum used to avoid magic number. This is slightly less obtuse."""

    FOUR_IMAGES = 0.3
    FIVE_IMAGES = 0.4


def pre_pro(root_video_directory: str) -> None:
    """
    This is the procedural glue for pre pro. It includes:
        - Recursively returning AVI files.
        - Splitting the resultant files into component JPEGs.
        - Formatting JPEG filenames for retrieval during post.
        - Running MegaDetector model against resultant JPEGs.
        - Producing a JSON representing the detection results.
    Running this function will result in an output.json file here: `grunz/output`.
    :param root_video_directory: Top level directory containing video files.
    :return: None.
    """
    file_utils = FileUtils(root_video_directory)
    avi_file_paths = file_utils.find_files_recursively("AVI")

    [
        Splitter(str(avi_file_path)).export_frames_to_jpeg(OneMinuteVideo.FIVE_IMAGES.value)
        for avi_file_path in avi_file_paths
    ]

    model = "".join([str(f) for f in Path(".").rglob("*.pb")])
    jpeg_file_paths = file_utils.find_files_recursively("jpeg")
    output_json = file_utils.create_json_output_file()
    results = load_and_run_detector_batch(model_file=model,
                                          image_file_names=jpeg_file_paths,
                                          checkpoint_path=output_json,
                                          checkpoint_frequency=1,
                                          confidence_threshold=0.850)
    return write_results_to_file(results, output_json)


def post_pro(mega_detector_json) -> None:
    """
    This is the procedural glue for post pro. It includes:
        - Parsing MegaDetector JSON to ascertain positive results.
        - Finding the AVI from which the JPEG derives.
        - Sorting positive results from negative.
    :return: None.
    """
    positive_detection_path = "grunz/output/positive_detection/"

    file_utils = FileUtils(Path("grunz/data/output"))
    file_utils.create_directory(Path("grunz/output/positive_detection"))

    json_parser = JSONParser(mega_detector_json)

    positive_detection_results = json_parser.filter_json_for_detection_results()
    positive_jpeg_file_paths = json_parser.get_file_paths_for_sort(positive_detection_results)
    positive_avi_paths = json_parser.get_list_for_sort(positive_jpeg_file_paths)
    avi_paths_set = file_utils.remove_duplicates_from_list(positive_avi_paths)

    for f in avi_paths_set:
        file_name = Path(f.name)
        original_path_to_file = Path("/".join(Path(f).parts[1:-1]))
        file_utils.create_directory(Path(f"{positive_detection_path}/{original_path_to_file}"))
        file_utils.copy_file(f, Path(f"{positive_detection_path}/{original_path_to_file}/{file_name}"))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--pre", help="Run pre pro steps. Switch expects the root path containing AVI files.",
                        type=pre_pro,
                        action="store")

    parser.add_argument("--post", help="Run post pro steps. Switch expects path to MegaDetector JSON.",
                        type=post_pro,
                        action="store")

    args = parser.parse_args()


if __name__ == "__main__":
    main()
