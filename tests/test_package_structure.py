"""Tests for project packaging — __init__.py files and importability."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestInitFiles:
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
