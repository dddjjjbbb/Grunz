"""Tests for hardcoded path removal in post_pro and create_json_output_file."""

import ast
import inspect
from pathlib import Path

from grunz.file_utils.file_utils import FileUtils

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestCreateJsonOutputFile:
    """create_json_output_file should write to a configurable directory, not a hardcoded one."""

    def test_accepts_output_dir_parameter(self):
        sig = inspect.signature(FileUtils.create_json_output_file)
        assert "output_dir" in sig.parameters, (
            "create_json_output_file should accept an output_dir parameter"
        )

    def test_creates_file_in_specified_directory(self, tmp_path):
        file_utils = FileUtils(tmp_path)
        result = file_utils.create_json_output_file(output_dir=tmp_path)
        result_path = Path(result)

        assert result_path.exists()
        assert result_path.parent == tmp_path

    def test_is_not_a_static_method(self):
        """Should be a regular method or accept output_dir, not a static method with hardcoded path."""
        source = (PROJECT_ROOT / "grunz" / "file_utils" / "file_utils.py").read_text()
        assert 'grunz/output/' not in source, (
            "file_utils.py still contains hardcoded 'grunz/output/' path"
        )


class TestPostProPaths:
    """post_pro should not contain hardcoded path strings."""

    def test_no_hardcoded_grunz_output_path(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "post_pro":
                func_source = ast.get_source_segment(source, node)
                assert 'grunz/output/positive_detection' not in func_source, (
                    "post_pro contains hardcoded 'grunz/output/positive_detection' path"
                )
                assert 'grunz/data/output' not in func_source, (
                    "post_pro contains hardcoded 'grunz/data/output' path"
                )
                break

    def test_post_pro_accepts_output_dir_parameter(self):
        from main import post_pro

        sig = inspect.signature(post_pro)
        assert "output_dir" in sig.parameters, (
            "post_pro should accept an output_dir parameter"
        )
