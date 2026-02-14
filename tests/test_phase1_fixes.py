"""Tests for Phase 1 code review fixes.

Each test targets a specific finding from the code review.
Tests are written to FAIL against the current code, then the fix makes them pass.
"""

import ast
import inspect
import json
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# --- C1: argparse type= misuse ---


class TestArgparseFixC1:
    """main() should parse args as strings, not execute functions via type=."""

    def test_pre_is_not_used_as_type_callable(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "add_argument":
                    for keyword in node.keywords:
                        if keyword.arg == "type":
                            # type= should be a builtin like str, not pre_pro/post_pro
                            if isinstance(keyword.value, ast.Name):
                                assert keyword.value.id not in (
                                    "pre_pro",
                                    "post_pro",
                                ), "argparse type= should not be a pipeline function"

    def test_post_is_not_used_as_type_callable(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        assert "type=post_pro" not in source, "post_pro should not be an argparse type="


# --- C2: filter_json_for_detection_results mutation bug ---


class TestFilterMutationBugC2:
    """Calling filter_json_for_detection_results twice must not accumulate results."""

    def test_second_call_does_not_include_first_call_results(self, tmp_path):
        from grunz.json_parser.json_parser import JSONParser

        images_a = [
            {
                "file": "a.jpeg",
                "max_detection_conf": 0.95,
                "detections": [{"category": "1", "conf": 0.95, "bbox": [0, 0, 1, 1]}],
            }
        ]
        images_b = [
            {
                "file": "b.jpeg",
                "max_detection_conf": 0.90,
                "detections": [{"category": "1", "conf": 0.90, "bbox": [0, 0, 1, 1]}],
            }
        ]

        path_a = tmp_path / "a.json"
        path_a.write_text(json.dumps({"images": images_a}))
        path_b = tmp_path / "b.json"
        path_b.write_text(json.dumps({"images": images_b}))

        parser = JSONParser(str(path_a))
        result_a = parser.filter_json_for_detection_results()
        assert len(result_a) == 1

        # Re-point parser to second file and call again
        parser.path_to_json = str(path_b)
        result_b = parser.filter_json_for_detection_results()

        # This MUST be 1, not 2. The old code appends to self.animals across calls.
        assert len(result_b) == 1, (
            f"Expected 1 result from second call, got {len(result_b)}. "
            "filter_json_for_detection_results is accumulating state across calls."
        )


# --- C3: pre_pro return type annotation ---


class TestPreProReturnTypeC3:
    """pre_pro should be annotated as returning str, not None."""

    def test_pre_pro_annotation_is_str(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "pre_pro":
                assert node.returns is not None, "pre_pro has no return annotation"
                # Should be 'str', not 'None'
                if isinstance(node.returns, ast.Constant):
                    assert node.returns.value is not None, (
                        "pre_pro return annotation is None"
                    )
                elif isinstance(node.returns, ast.Name):
                    assert node.returns.id == "str", (
                        f"pre_pro return annotation is {node.returns.id}, expected str"
                    )
                break


# --- M2: confidence_rating type hint ---


class TestConfidenceTypeHintM2:
    """is_confidence_rating_minimum_or_above should accept float, not int."""

    def test_parameter_type_is_float(self):
        from grunz.json_parser.json_parser import JSONParser

        sig = inspect.signature(JSONParser.is_confidence_rating_minimum_or_above)
        param = sig.parameters["confidence_rating"]
        assert param.annotation is float, (
            f"confidence_rating annotation is {param.annotation}, expected float"
        )


# --- M3: find_files_recursively return type ---


class TestFindFilesReturnTypeM3:
    """find_files_recursively should have a proper return type annotation."""

    def test_return_annotation_is_list_of_str(self):
        from grunz.file_utils.file_utils import FileUtils

        sig = inspect.signature(FileUtils.find_files_recursively)
        ret = sig.return_annotation

        # Accept list[str] or List[str]
        origin = getattr(ret, "__origin__", None)
        assert origin is list, (
            f"Return annotation origin is {origin}, expected list. "
            f"Full annotation: {ret}"
        )


# --- L2: Remove if not detections: pass ---


class TestRemovePassL2:
    """filter_json_for_detection_results should not contain 'if not detections: pass'."""

    def test_no_pass_statement_in_filter(self):
        source = (PROJECT_ROOT / "grunz" / "json_parser" / "json_parser.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "filter_json_for_detection_results":
                for child in ast.walk(node):
                    if isinstance(child, ast.Pass):
                        pytest.fail(
                            "filter_json_for_detection_results still contains a 'pass' statement"
                        )


# --- M1: Simplify boolean returns ---


class TestSimplifyBooleansM1:
    """Boolean predicate methods should return expressions directly, not if/return True/return False."""

    def _has_if_return_true_return_false(self, func_node):
        """Check if a function has the pattern: if X: return True; return False."""
        body = func_node.body
        for i, stmt in enumerate(body):
            if isinstance(stmt, ast.If):
                if_body = stmt.body
                if (
                    len(if_body) == 1
                    and isinstance(if_body[0], ast.Return)
                    and isinstance(if_body[0].value, ast.Constant)
                    and if_body[0].value.value is True
                ):
                    # Check if next statement is return False
                    if i + 1 < len(body):
                        next_stmt = body[i + 1]
                        if (
                            isinstance(next_stmt, ast.Return)
                            and isinstance(next_stmt.value, ast.Constant)
                            and next_stmt.value.value is False
                        ):
                            return True
        return False

    def test_is_confidence_rating_uses_direct_return(self):
        source = (PROJECT_ROOT / "grunz" / "json_parser" / "json_parser.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "is_confidence_rating_minimum_or_above":
                assert not self._has_if_return_true_return_false(node), (
                    "is_confidence_rating_minimum_or_above uses if/return True/return False pattern"
                )

    def test_is_category_of_type_animal_uses_direct_return(self):
        source = (PROJECT_ROOT / "grunz" / "json_parser" / "json_parser.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "is_category_of_type_animal":
                assert not self._has_if_return_true_return_false(node), (
                    "is_category_of_type_animal uses if/return True/return False pattern"
                )


# --- L1: Duplicate pathlib import ---


class TestDuplicateImportL1:
    """json_parser.py should not have both 'import pathlib' and 'from pathlib import Path'."""

    def test_no_bare_import_pathlib(self):
        source = (PROJECT_ROOT / "grunz" / "json_parser" / "json_parser.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "pathlib":
                        pytest.fail(
                            "json_parser.py has 'import pathlib' alongside 'from pathlib import Path'"
                        )


# --- H1: Missing __init__.py files ---


class TestInitFilesH1:
    """All grunz packages must have __init__.py files."""

    @pytest.mark.parametrize(
        "package_dir",
        [
            "grunz",
            "grunz/file_utils",
            "grunz/json_parser",
            "grunz/splitter",
        ],
    )
    def test_init_file_exists(self, package_dir):
        init_path = PROJECT_ROOT / package_dir / "__init__.py"
        assert init_path.exists(), f"Missing {package_dir}/__init__.py"
