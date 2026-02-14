"""Tests for deduplication ordering in FileUtils."""

from pathlib import Path

from grunz.file_utils.file_utils import FileUtils


class TestDeduplicationOrdering:
    """remove_duplicates_from_list must preserve insertion order."""

    def test_preserves_insertion_order(self):
        input_list = [
            Path("c/PICT0003.AVI"),
            Path("a/PICT0001.AVI"),
            Path("b/PICT0002.AVI"),
            Path("a/PICT0001.AVI"),
            Path("c/PICT0003.AVI"),
        ]
        result = FileUtils.remove_duplicates_from_list(input_list)

        assert len(result) == 3
        assert result == [
            Path("c/PICT0003.AVI"),
            Path("a/PICT0001.AVI"),
            Path("b/PICT0002.AVI"),
        ], f"Order not preserved: {result}"
