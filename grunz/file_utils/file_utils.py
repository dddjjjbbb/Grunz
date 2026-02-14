"""This module handles local file management during pre and post-processing."""

import time
from pathlib import Path
from shutil import copy2
from typing import List


class FileUtils:
    """This class is responsible for finding, renaming and sorting file inputs and outputs."""

    def __init__(self, directory: Path):

        self.directory = directory

    def find_files_recursively(self, extension: str) -> list[str]:
        """
        :param extension: A file extension. This is case dependent.
        :return: A sorted list of file paths matching the extension argument.
        """
        return sorted(
            [
                str(file_path.resolve())
                for file_path in Path(self.directory).rglob(f"*.{extension}")
            ]
        )

    @staticmethod
    def convert_path_name(file_path: str) -> str:
        """
        This value is used to preserve the original file path of a component JPEG.
        This way we can easily trace a positive detection to its correspondent video.
        :return: compliant path. i.e. replace '/' with '-'.
        """
        return "-".join(Path(file_path).parts[1:])

    @staticmethod
    def create_directory(*file_paths: Path) -> List:
        """
        Method to be used to create `detections` directory.
        :param file_paths: file path or path(s).
        :return: List.
        """
        return [
            Path(file_path).mkdir(parents=True, exist_ok=True)
            for file_path in file_paths
        ]

    @staticmethod
    def copy_file(source_path: str, destination_path: str) -> None:
        """
        :param source_path: Path to file to copy.
        :param destination_path: Path to destination dir, including filename.
        :return: None.
        """
        return copy2(source_path, destination_path)

    @staticmethod
    def create_json_output_file(output_dir: Path) -> str:
        """Create a timestamped JSON output file in the given directory.
        :param output_dir: Directory to create the file in.
        :return: Path to the created file as a string.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        time_stamp = time.strftime("%Y%m%d-%H%M")
        filename = Path(output_dir) / f"{time_stamp}.json"
        filename.touch(exist_ok=True)
        return str(filename)

    @staticmethod
    def remove_duplicates_from_list(_list: list) -> list:
        """
        :param _list: List with duplicates.
        :return: List without duplicates.
        """
        return list(set(_list))
