"""Tests for main.py — CLI entry point and pipeline orchestration."""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestArgparseContract:
    """main() should parse args as strings, not execute functions via type=."""

    def test_pre_is_not_used_as_type_callable(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "add_argument":
                    for keyword in node.keywords:
                        if keyword.arg == "type":
                            if isinstance(keyword.value, ast.Name):
                                assert keyword.value.id not in (
                                    "pre_pro",
                                    "post_pro",
                                ), "argparse type= should not be a pipeline function"

    def test_post_is_not_used_as_type_callable(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        assert "type=post_pro" not in source, "post_pro should not be an argparse type="


class TestPreProAnnotation:
    """pre_pro should be annotated as returning str, not None."""

    def test_pre_pro_annotation_is_str(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "pre_pro":
                assert node.returns is not None, "pre_pro has no return annotation"
                if isinstance(node.returns, ast.Constant):
                    assert node.returns.value is not None, (
                        "pre_pro return annotation is None"
                    )
                elif isinstance(node.returns, ast.Name):
                    assert node.returns.id == "str", (
                        f"pre_pro return annotation is {node.returns.id}, expected str"
                    )
                break
