"""Tests for dependency management and import correctness."""

import ast
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestDependencyPinning:
    """requirements.txt must pin dependencies to prevent breakage."""

    def test_all_core_dependencies_are_pinned(self):
        requirements = (PROJECT_ROOT / "requirements.txt").read_text()

        core_packages = [
            "PytorchWildlife",
            "moviepy",
            "numpy",
            "Pillow",
            "matplotlib",
            "pandas",
            "requests",
            "tqdm",
        ]

        for package in core_packages:
            pattern = rf"^{re.escape(package)}\s*[><=~!]"
            assert re.search(pattern, requirements, re.MULTILINE | re.IGNORECASE), (
                f"{package} is not pinned in requirements.txt"
            )


class TestMoviepyImport:
    """splitter.py must not import from the deprecated moviepy.editor namespace."""

    def test_no_moviepy_editor_import(self):
        source = (PROJECT_ROOT / "grunz" / "splitter" / "splitter.py").read_text()
        assert "moviepy.editor" not in source, (
            "splitter.py imports from deprecated moviepy.editor namespace"
        )
