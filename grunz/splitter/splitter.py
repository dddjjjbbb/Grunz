"""This module handles splitting video into component JPEGs for passing to MegaDetector."""

from pathlib import Path

from moviepy.editor import VideoFileClip

from grunz.file_utils.file_utils import FileUtils


class Splitter:
    """This class splits videos into component JPEGs."""

    def __init__(self, file_path):

        self.file_path = file_path
        self.file_utils = FileUtils(self.file_path)

    def export_frames_to_jpeg(self, fps_value: float) -> None:
        """
        :param fps_value: Number of frames per second to consider when writing the
          clip. 0.4 loosely corresponds to 5 images per 1 minute clip.
        :return: None.
        """
        clip = VideoFileClip(self.file_path)

        export_parent_path = f"{Path(self.file_path).parent}"
        jpeg_filename = self.file_utils.convert_path_name(self.file_path)
        return clip.write_images_sequence(
            f"{export_parent_path}/{jpeg_filename}-%03d.jpeg", fps=fps_value
        )
