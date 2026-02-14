"""Tests for grunz/file_utils/file_utils.py — file management utilities."""

import inspect

from grunz.file_utils.file_utils import FileUtils


class TestTypeAnnotations:
    """Type annotations must match actual runtime types."""

    def test_find_files_recursively_returns_list_of_str(self):
        sig = inspect.signature(FileUtils.find_files_recursively)
        ret = sig.return_annotation

        origin = getattr(ret, "__origin__", None)
        assert origin is list, (
            f"Return annotation origin is {origin}, expected list. "
            f"Full annotation: {ret}"
        )
