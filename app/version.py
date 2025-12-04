"""
Version information for FonixFlow.
"""
__version__ = "1.0.1"
__build__ = "101"

VERSION_NAME = f"{__version__}"
VERSION_WITH_BUILD = f"{__version__} (build {__build__})"

def get_version():
    return __version__

def get_version_string():
    return VERSION_WITH_BUILD
