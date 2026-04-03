import importlib
import os
import sys

import pytest


def _get_package_module():
    """Import the seedance_comfyui package to access __init__.py exports.

    Adds the parent of the project directory to sys.path so that
    'seedance_comfyui' can be imported as a proper package (required
    for relative imports inside __init__.py to work).
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parent_dir = os.path.dirname(project_root)
    package_name = os.path.basename(project_root)

    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Remove from sys.modules if already loaded to get a fresh import
    if package_name in sys.modules:
        del sys.modules[package_name]
    if f"{package_name}.nodes" in sys.modules:
        del sys.modules[f"{package_name}.nodes"]

    return importlib.import_module(package_name)


class TestNodeClassMappings:
    """Verify NODE_CLASS_MAPPINGS is correctly structured."""

    def test_node_class_mappings(self):
        mod = _get_package_module()
        assert hasattr(mod, "NODE_CLASS_MAPPINGS"), (
            "__init__.py must export NODE_CLASS_MAPPINGS"
        )
        mappings = mod.NODE_CLASS_MAPPINGS
        assert isinstance(mappings, dict), "NODE_CLASS_MAPPINGS must be a dict"

        expected_keys = {"SeedanceApiKey", "SeedanceTextToVideo", "SeedanceImageToVideo"}
        assert set(mappings.keys()) == expected_keys, (
            f"NODE_CLASS_MAPPINGS keys must be {expected_keys}, got {set(mappings.keys())}"
        )

        for key, cls in mappings.items():
            assert isinstance(cls, type), f"Value for '{key}' must be a class, got {type(cls)}"


class TestNodeDisplayNameMappings:
    """Verify NODE_DISPLAY_NAME_MAPPINGS is correctly structured."""

    def test_node_display_name_mappings(self):
        mod = _get_package_module()
        assert hasattr(mod, "NODE_DISPLAY_NAME_MAPPINGS"), (
            "__init__.py must export NODE_DISPLAY_NAME_MAPPINGS"
        )
        mappings = mod.NODE_DISPLAY_NAME_MAPPINGS
        assert isinstance(mappings, dict), "NODE_DISPLAY_NAME_MAPPINGS must be a dict"

        expected_keys = {"SeedanceApiKey", "SeedanceTextToVideo", "SeedanceImageToVideo"}
        assert set(mappings.keys()) == expected_keys, (
            f"NODE_DISPLAY_NAME_MAPPINGS keys must be {expected_keys}, got {set(mappings.keys())}"
        )

        for key, name in mappings.items():
            assert isinstance(name, str) and len(name) > 0, (
                f"Display name for '{key}' must be a non-empty string"
            )


class TestNodeCategories:
    """Verify all node classes have CATEGORY = 'Seedance 2.0'."""

    def test_node_categories(self):
        mod = _get_package_module()
        for name, cls in mod.NODE_CLASS_MAPPINGS.items():
            assert hasattr(cls, "CATEGORY"), (
                f"Node class '{name}' must have a CATEGORY attribute"
            )
            assert cls.CATEGORY == "Seedance 2.0", (
                f"Node class '{name}' CATEGORY must be 'Seedance 2.0', got '{cls.CATEGORY}'"
            )


class TestRequirements:
    """Verify requirements.txt contains expected dependencies."""

    def test_requirements(self):
        # Find requirements.txt relative to this test file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        req_path = os.path.join(project_root, "requirements.txt")
        assert os.path.isfile(req_path), "requirements.txt must exist in project root"

        with open(req_path, "r") as f:
            content = f.read()

        required_packages = [
            "requests>=",
            "Pillow>=",
            "numpy>=",
            "opencv-python>=",
        ]

        for package in required_packages:
            assert package in content, (
                f"requirements.txt must contain '{package}'"
            )

        # Ensure torch is NOT listed (ComfyUI manages its own PyTorch)
        assert "torch" not in [line.split(">=")[0].split("==")[0].strip()
                                for line in content.strip().splitlines()
                                if line.strip() and not line.startswith("#")], (
            "requirements.txt must NOT include torch (ComfyUI manages its own PyTorch)"
        )
