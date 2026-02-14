"""Tests for grunz/file_utils/file_utils.py — file discovery, copying, and path handling."""

from filecmp import cmp
from pathlib import Path

from grunz.file_utils.file_utils import FileUtils


class TestFindFilesRecursively:
    """find_files_recursively must filter by extension and return sorted results."""

    def test_matching_extension_returns_only_those_files(self, tmp_path):
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        (tmp_path / "file3.AVI").touch()
        (tmp_path / "file4.AVI").touch()

        file_utils = FileUtils(tmp_path)
        result = file_utils.find_files_recursively("AVI")

        expected = sorted(
            str(p.resolve()) for p in tmp_path.glob("*.AVI")
        )
        assert result == expected

    def test_results_are_sorted_alphabetically(self, tmp_path):
        (tmp_path / "charlie.jpeg").touch()
        (tmp_path / "alpha.jpeg").touch()
        (tmp_path / "bravo.jpeg").touch()

        file_utils = FileUtils(tmp_path)
        result = file_utils.find_files_recursively("jpeg")

        assert result == sorted(result)

    def test_no_matching_files_returns_empty_list(self, tmp_path):
        (tmp_path / "file.txt").touch()

        file_utils = FileUtils(tmp_path)
        result = file_utils.find_files_recursively("AVI")

        assert result == []

    def test_nested_files_are_found(self, tmp_path):
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.AVI").touch()
        (tmp_path / "top.AVI").touch()

        file_utils = FileUtils(tmp_path)
        result = file_utils.find_files_recursively("AVI")

        assert len(result) == 2
        assert any("nested.AVI" in p for p in result)
        assert any("top.AVI" in p for p in result)


class TestCreateDirectory:
    """create_directory must create one or more directories, including parents."""

    def test_single_directory_is_created(self, tmp_path):
        target = tmp_path / "new_dir"

        FileUtils.create_directory(target)

        assert target.exists()
        assert target.is_dir()

    def test_nested_parents_are_created(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"

        FileUtils.create_directory(target)

        assert target.exists()

    def test_multiple_directories_are_created(self, tmp_path):
        dir_a = tmp_path / "dir_a"
        dir_b = tmp_path / "dir_b"

        FileUtils.create_directory(dir_a, dir_b)

        assert dir_a.exists()
        assert dir_b.exists()

    def test_existing_directory_does_not_raise(self, tmp_path):
        target = tmp_path / "existing"
        target.mkdir()

        FileUtils.create_directory(target)

        assert target.exists()


class TestCopyFile:
    """copy_file must produce an identical copy at the destination."""

    def test_copied_file_is_identical_to_source(self, tmp_path):
        source = tmp_path / "source.txt"
        source.write_text("camera trap data")
        destination = tmp_path / "destination.txt"

        FileUtils.copy_file(str(source), str(destination))

        assert cmp(source, destination)

    def test_destination_file_exists_after_copy(self, tmp_path):
        source = tmp_path / "source.bin"
        source.write_bytes(b"\x00\x01\x02")
        destination = tmp_path / "copy.bin"

        FileUtils.copy_file(str(source), str(destination))

        assert destination.exists()


class TestConvertPathName:
    """convert_path_name must replace path separators with dashes for flat filenames."""

    def test_unix_path_converts_separators_to_dashes(self):
        result = FileUtils.convert_path_name("/data/videos/PICT0001.AVI")

        assert "/" not in result
        assert result == "data-videos-PICT0001.AVI"

    def test_strips_leading_component_and_joins_rest(self):
        result = FileUtils.convert_path_name("data/videos/PICT0001.AVI")

        assert result == "videos-PICT0001.AVI"

    def test_preserves_file_extension(self):
        result = FileUtils.convert_path_name("/a/b/file.jpeg")

        assert result.endswith(".jpeg")
