"""
Unit tests for app.version module.
"""
import pytest


class TestVersion:
    """Tests for version module."""

    def test_version_format(self):
        from app.version import __version__
        parts = __version__.split(".")
        assert len(parts) == 3  # major.minor.patch
        for part in parts:
            assert part.isdigit()

    def test_version_is_1_1_0(self):
        from app.version import __version__, __build__
        assert __version__ == "1.1.0"
        assert __build__ == "110"

    def test_get_version(self):
        from app.version import get_version
        assert get_version() == "1.1.0"

    def test_get_version_string(self):
        from app.version import get_version_string
        result = get_version_string()
        assert "1.1.0" in result
        assert "110" in result
