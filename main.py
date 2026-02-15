"""This is the main entry point for managing the pre and post-processing
MegaDetector pipeline."""

import argparse
import json
import logging
from enum import Enum
from pathlib import Path

from grunz.detector import convert_result, create_detector
from grunz.file_utils.file_utils import FileUtils
from grunz.json_parser.json_parser import JSONParser
from grunz.splitter.splitter import Splitter


logger = logging.getLogger(__name__)


class OneMinuteVideo(Enum):
    FIVE_IMAGES = 0.4


def pre_pro(root_video_directory: str) -> str:
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
    file_utils = FileUtils(Path(root_video_directory))
    avi_file_paths = file_utils.find_files_recursively("AVI")

    for avi_file_path in avi_file_paths:
        try:
            Splitter(str(avi_file_path)).export_frames_to_jpeg(
                OneMinuteVideo.FIVE_IMAGES.value
            )
        except IOError:
            logger.error("%s could not be read", avi_file_path, exc_info=True)
            continue

    detector = create_detector()
    jpeg_file_paths = file_utils.find_files_recursively("jpeg")
    output_dir = Path(root_video_directory).parent / "output"
    output_json = file_utils.create_json_output_file(output_dir)

    results = []
    for image_path in jpeg_file_paths:
        pw_result = detector.single_image_detection(image_path)
        results.append(convert_result(pw_result))

    with open(output_json, "w") as output_file:
        json.dump({"images": results}, output_file)

    return output_json


def post_pro(mega_detector_json, output_dir: Path = None) -> None:
    """
    This is the procedural glue for post pro. It includes:
        - Parsing MegaDetector JSON to ascertain positive results.
        - Finding the AVI from which the JPEG derives.
        - Sorting positive results from negative.
    :param mega_detector_json: Path to the MegaDetector JSON output file.
    :param output_dir: Base directory for positive detection output.
        Defaults to the parent directory of the JSON file.
    :return: None.
    """
    if output_dir is None:
        output_dir = Path(mega_detector_json).parent

    positive_detection_path = Path(output_dir) / "positive_detection"

    file_utils = FileUtils(positive_detection_path)
    file_utils.create_directory(positive_detection_path)

    json_parser = JSONParser(mega_detector_json)

    positive_detection_results = json_parser.filter_json_for_detection_results()
    positive_jpeg_file_paths = json_parser.extract_file_paths(
        positive_detection_results
    )
    positive_avi_paths = json_parser.convert_jpeg_paths_to_avi_paths(positive_jpeg_file_paths)
    avi_paths_set = file_utils.remove_duplicates_from_list(positive_avi_paths)

    for f in avi_paths_set:
        file_name = Path(f.name)
        parts = Path(f).parts[1:-1]
        if parts:
            original_path_to_file = Path(*parts)
        else:
            original_path_to_file = Path(".")
        dest_dir = positive_detection_path / original_path_to_file
        file_utils.create_directory(dest_dir)
        file_utils.copy_file(f, str(dest_dir / file_name))


def _configure_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "grunz.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pre",
        help="Run pre pro steps. Switch expects the root path containing AVI files.",
        type=str,
    )

    parser.add_argument(
        "--post",
        help="Run post pro steps. Switch expects path to MegaDetector JSON.",
        type=str,
    )

    args = parser.parse_args()

    log_dir = Path(args.pre or args.post or ".").parent / "logs"
    _configure_logging(log_dir)

    if args.pre:
        pre_pro(args.pre)
    if args.post:
        post_pro(args.post)


if __name__ == "__main__":
    main()
