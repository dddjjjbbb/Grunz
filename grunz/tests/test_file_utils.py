import unittest
import tempfile
import os
import time
import hashlib
from pathlib import Path
from filecmp import cmp

from grunz.file_utils.file_utils import FileUtils


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        # Creates a temporary directory for test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.file_utils = FileUtils(Path(self.test_dir.name))

    def tearDown(self):
        # Cleans up the temporary directory and test files
        self.test_dir.cleanup()

    def test_find_files_recursively_returning_matching_files(self):
        """
        Tests that only the file paths matching the submitted extension are returned.
        Paths of expected_files are converted to strings with resolved absolute paths to
        facilitate comparison with result.
        """
        self.create_dummy_files('file1.txt', 'file2.txt', 'file3.AVI', 'file4.AVI')

        result = self.file_utils.find_files_recursively('AVI')

        expected_files = [
            str(Path(self.test_dir.name) / 'file3.AVI'),
            str(Path(self.test_dir.name) / 'file4.AVI')
        ]
        expected_files = [str(Path(p).resolve()) for p in expected_files]

        self.assertEqual(result, expected_files, "Returned files does not match expected files.")

    def test_find_files_recursively_sorting_files(self):
        """
        Tests that the returned list of file paths is correctly sorted.
        Paths of expected_files are converted to strings with resolved absolute
        paths to facilitate comparison with result.
        """
        self.create_dummy_files('file1.txt', 'file4.jpeg', 'file2.jpeg', 'file3.jpeg')

        result = self.file_utils.find_files_recursively('jpeg')

        expected_files = [
            str(Path(self.test_dir.name) / 'file2.jpeg'),
            str(Path(self.test_dir.name) / 'file3.jpeg'),
            str(Path(self.test_dir.name) / 'file4.jpeg')
        ]
        expected_files = [str(Path(p).resolve()) for p in expected_files]

        self.assertEqual(result, expected_files, "Files are not correctly sorted.")

    def test_create_directory(self):
        """
        Tests that a directory is correctly created.
        """
        self.file_utils.create_directory(Path(self.test_dir.name) / 'test_directory')

        new_directory = Path(self.test_dir.name) / 'test_directory'

        self.assertTrue(new_directory.exists(), f"{new_directory} does not exist.")

    def test_copy_file(self):
        """
        Tests that an identical file is created when copy_file is run.
        """
        source_path = Path(self.test_dir.name) / 'source_file.txt'
        source_content = 'This is the source file content.'
        source_path.write_text(source_content)

        destination_path = Path(self.test_dir.name) / 'destination_file.txt'

        self.file_utils.copy_file(str(source_path), str(destination_path))

        self.assertTrue(cmp(source_path, destination_path), "Files are not identical.")

    def test_create_json_output_file_with_new_file(self):
        """
        Tests that a json file is created when one does not already exist.
        Checks both that the file is created and that the file is a json.
        The working directory is changed because create_json_output_file creates files in grunz/output.
        """
        original_cwd = os.getcwd()
        os.chdir(Path(__file__).resolve().parent.parent.parent)
        created_file_path = ""

        try:
            # First checks if file with current timestamp already exists
            time_stamp = time.strftime("%Y%m%d-%H%M")
            existing_file_path = Path(f"grunz/output/{time_stamp}.json")
            self.assertFalse(existing_file_path.exists(),
                             "A file with the same name already exists in the directory.")

            created_file_path = self.file_utils.create_json_output_file()

            self.assertTrue(Path(created_file_path).exists(), "File was not created.")
            self.assertTrue(created_file_path.endswith('.json'), "Created file is not a JSON file.")
        finally:
            self.clean_up_test_files(created_file_path)
            os.chdir(original_cwd)

    def test_create_json_output_file_with_existing_file(self):
        """
        Tests that when a file already exists, a new file is not created.
        The working directory is changed in order to test in grunz/output.
        """
        original_cwd = os.getcwd()
        os.chdir(Path(__file__).resolve().parent.parent.parent)

        # Dummy JSON file is created
        existing_file_timestamp = time.strftime("%Y%m%d-%H%M")
        existing_file_path = Path(f"grunz/output/{existing_file_timestamp}.json")
        existing_file_path.touch()

        existing_file_content_hash = hashlib.md5(existing_file_path.read_bytes()).hexdigest()

        new_file_path_attempt = ""

        try:
            new_file_path_attempt = self.file_utils.create_json_output_file()

            new_file_content_hash = hashlib.md5(Path(new_file_path_attempt).read_bytes()).hexdigest()

            self.assertEqual(existing_file_path, Path(new_file_path_attempt),
                             "Existing filename has been changed or new file has been created.")

            # Asserts that not only the filename, but the content of the file is unchanged
            # (to guard against the replacement of a file with an identically named file)
            self.assertEqual(existing_file_content_hash, new_file_content_hash,
                             "Content of existing file has changed.")
        finally:
            self.clean_up_test_files(new_file_path_attempt, existing_file_path)
            os.chdir(original_cwd)

    def create_dummy_files(self, *file_names):
        """
        Creates dummy files in the temporary test directory.
        """
        for file_name in file_names:
            file_path = Path(self.test_dir.name) / file_name
            file_path.touch()

    def clean_up_test_files(self, *file_paths):
        """
        Deletes files created outside the test directory
        """
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
