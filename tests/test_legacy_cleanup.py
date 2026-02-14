"""Tests for removal of legacy artefacts and unused code."""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestLegacySubmodules:
    """Legacy cameratraps and ai4eutils submodules should be removed."""

    def test_gitmodules_does_not_exist(self):
        gitmodules = PROJECT_ROOT / ".gitmodules"
        assert not gitmodules.exists(), ".gitmodules still exists with legacy submodule entries"

    def test_cameratraps_directory_does_not_exist(self):
        assert not (PROJECT_ROOT / "cameratraps").exists(), "Legacy cameratraps directory still exists"

    def test_ai4eutils_directory_does_not_exist(self):
        assert not (PROJECT_ROOT / "ai4eutils").exists(), "Legacy ai4eutils directory still exists"


class TestUnusedEnumValue:
    """OneMinuteVideo.FOUR_IMAGES is unused and should be removed."""

    def test_four_images_not_in_source(self):
        source = (PROJECT_ROOT / "main.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "OneMinuteVideo":
                member_names = [
                    target.id
                    for stmt in node.body
                    if isinstance(stmt, ast.Assign)
                    for target in stmt.targets
                    if isinstance(target, ast.Name)
                ]
                assert "FOUR_IMAGES" not in member_names, (
                    "OneMinuteVideo.FOUR_IMAGES is defined but never used"
                )
                break


class TestSplitterFileUtils:
    """Splitter should not instantiate FileUtils just to call a static method."""

    def test_splitter_does_not_instantiate_file_utils(self):
        source = (PROJECT_ROOT / "grunz" / "splitter" / "splitter.py").read_text()
        assert "self.file_utils = FileUtils" not in source, (
            "Splitter unnecessarily instantiates FileUtils"
        )
