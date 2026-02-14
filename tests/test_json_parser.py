"""Tests for grunz/json_parser/json_parser.py — JSON parsing and filtering."""

import ast
import inspect
import json
from pathlib import Path

import pytest

from grunz.json_parser.json_parser import JSONParser

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSON_PARSER_SOURCE = PROJECT_ROOT / "grunz" / "json_parser" / "json_parser.py"


class TestFilterDetectionResults:
    """filter_json_for_detection_results must not accumulate state across calls."""

    def test_second_call_does_not_include_first_call_results(self, tmp_path):
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

        parser.path_to_json = str(path_b)
        result_b = parser.filter_json_for_detection_results()

        assert len(result_b) == 1, (
            f"Expected 1 result from second call, got {len(result_b)}. "
            "filter_json_for_detection_results is accumulating state across calls."
        )

    def test_no_pass_statement_in_filter(self):
        source = JSON_PARSER_SOURCE.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "filter_json_for_detection_results":
                for child in ast.walk(node):
                    if isinstance(child, ast.Pass):
                        pytest.fail(
                            "filter_json_for_detection_results contains a dead 'pass' branch"
                        )


class TestTypeAnnotations:
    """Type annotations must match actual runtime types."""

    def test_confidence_rating_parameter_is_float(self):
        sig = inspect.signature(JSONParser.is_confidence_rating_minimum_or_above)
        param = sig.parameters["confidence_rating"]
        assert param.annotation is float, (
            f"confidence_rating annotation is {param.annotation}, expected float"
        )


class TestBooleanPredicates:
    """Boolean predicate methods should return expressions directly."""

    def _has_if_return_true_return_false(self, func_node):
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
        source = JSON_PARSER_SOURCE.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "is_confidence_rating_minimum_or_above":
                assert not self._has_if_return_true_return_false(node), (
                    "is_confidence_rating_minimum_or_above uses if/return True/return False pattern"
                )

    def test_is_category_of_type_animal_uses_direct_return(self):
        source = JSON_PARSER_SOURCE.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "is_category_of_type_animal":
                assert not self._has_if_return_true_return_false(node), (
                    "is_category_of_type_animal uses if/return True/return False pattern"
                )


class TestImportHygiene:
    """No duplicate or unnecessary imports."""

    def test_no_bare_pathlib_import(self):
        source = JSON_PARSER_SOURCE.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "pathlib":
                        pytest.fail(
                            "json_parser.py has 'import pathlib' alongside 'from pathlib import Path'"
                        )
