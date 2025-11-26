"""
Version information for FonixFlow.

This is the single source of truth for the application version.
Update this file before creating a release.
"""

# Semantic versioning: MAJOR.MINOR.PATCH
__version__ = "1.0.0"
__build__ = "100"  # Build number (increment with each build)

# Human-readable version string
VERSION_NAME = f"{__version__}"
VERSION_WITH_BUILD = f"{__version__} (build {__build__})"

def get_version():
    """Return the current application version."""
    return __version__

def get_version_string():
    """Return the full version string including build number."""
    return VERSION_WITH_BUILD
