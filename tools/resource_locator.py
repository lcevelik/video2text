"""
Resource Locator for FonixFlow

Handles finding bundled resources (ffmpeg, Whisper models) both in:
- Development mode (running from source)
- Bundled mode (running as .app via PyInstaller)
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller bundle.

    Args:
        relative_path: Relative path to resource

    Returns:
        str: Absolute path to resource
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        logger.info(f"[RESOURCE_LOCATOR] Running in PyInstaller bundle mode, _MEIPASS={base_path}")
    except AttributeError:
        # Running in development mode
        base_path = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"[RESOURCE_LOCATOR] Running in development mode, base_path={base_path}")

    full_path = os.path.join(base_path, relative_path)
    logger.debug(f"[RESOURCE_LOCATOR] Resolving '{relative_path}' to '{full_path}'")
    return full_path


def get_ffmpeg_path():
    """
    Get path to ffmpeg binary.

    Returns:
        str: Path to ffmpeg executable

    Raises:
        RuntimeError: If ffmpeg not found
    """
    import logging
    logger = logging.getLogger(__name__)

    # Check multiple possible bundled locations
    # PyInstaller places binaries in the same directory as the executable
    # In macOS .app bundles, this is Contents/MacOS/
    possible_paths = [
        get_resource_path('ffmpeg'),  # Root of bundle (PyInstaller default - same dir as executable)
        get_resource_path('bin/ffmpeg'),  # Standard location
    ]

    # For macOS .app bundles, also check relative to executable location
    # sys.executable points to Contents/MacOS/FonixFlow in a .app bundle
    try:
        if hasattr(sys, 'executable') and sys.executable:
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            # Check in same directory as executable
            possible_paths.append(os.path.join(exe_dir, 'ffmpeg'))
            # Check in Frameworks (if PyInstaller placed it there)
            frameworks_ffmpeg = os.path.join(exe_dir, '..', 'Frameworks', 'ffmpeg')
            possible_paths.append(os.path.abspath(frameworks_ffmpeg))
    except Exception as e:
        logger.debug(f"Could not check executable-relative paths: {e}")

    logger.info(f"Searching for ffmpeg in bundled locations...")
    for bundled_ffmpeg in possible_paths:
        exists = os.path.exists(bundled_ffmpeg)
        executable = exists and os.access(bundled_ffmpeg, os.X_OK)
        logger.debug(f"  Checking: {bundled_ffmpeg} (exists={exists}, executable={executable})")
        if exists and executable:
            logger.info(f"✓ Found bundled ffmpeg at: {bundled_ffmpeg}")
            return bundled_ffmpeg

    # Fall back to system ffmpeg
    import shutil
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        logger.info(f"✓ Using system ffmpeg at: {system_ffmpeg}")
        return system_ffmpeg

    logger.error("ERROR: ffmpeg not found in any location!")
    raise RuntimeError(
        "ffmpeg not found. "
        "Please install ffmpeg: https://ffmpeg.org/download.html"
    )


def get_ffprobe_path():
    """
    Get path to ffprobe binary.

    Returns:
        str: Path to ffprobe executable

    Raises:
        RuntimeError: If ffprobe not found
    """
    import logging
    logger = logging.getLogger(__name__)

    # Check multiple possible bundled locations
    # PyInstaller places binaries in the same directory as the executable
    # In macOS .app bundles, this is Contents/MacOS/
    possible_paths = [
        get_resource_path('ffprobe'),  # Root of bundle (PyInstaller default - same dir as executable)
        get_resource_path('bin/ffprobe'),  # Standard location
    ]

    # For macOS .app bundles, also check relative to executable location
    # sys.executable points to Contents/MacOS/FonixFlow in a .app bundle
    try:
        if hasattr(sys, 'executable') and sys.executable:
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            # Check in same directory as executable
            possible_paths.append(os.path.join(exe_dir, 'ffprobe'))
            # Check in Frameworks (if PyInstaller placed it there)
            frameworks_ffprobe = os.path.join(exe_dir, '..', 'Frameworks', 'ffprobe')
            possible_paths.append(os.path.abspath(frameworks_ffprobe))
    except Exception as e:
        logger.debug(f"Could not check executable-relative paths: {e}")

    logger.info(f"Searching for ffprobe in bundled locations...")
    for bundled_ffprobe in possible_paths:
        exists = os.path.exists(bundled_ffprobe)
        executable = exists and os.access(bundled_ffprobe, os.X_OK)
        logger.debug(f"  Checking: {bundled_ffprobe} (exists={exists}, executable={executable})")
        if exists and executable:
            logger.info(f"✓ Found bundled ffprobe at: {bundled_ffprobe}")
            return bundled_ffprobe

    # Fall back to system ffprobe
    import shutil
    system_ffprobe = shutil.which('ffprobe')
    if system_ffprobe:
        logger.info(f"✓ Using system ffprobe at: {system_ffprobe}")
        return system_ffprobe

    logger.error("ERROR: ffprobe not found in any location!")
    raise RuntimeError(
        "ffprobe not found. "
        "Please install ffmpeg: https://ffmpeg.org/download.html"
    )


def get_whisper_cache_dir():
    """
    Get path to bundled Whisper cache directory (parent of 'whisper' folder).

    Returns:
        str: Path to cache directory (containing 'whisper/' subdirectory), or None if not bundled
    """
    # Check multiple possible bundled locations
    # Whisper expects models in {cache_dir}/whisper/*.pt
    possible_paths = [
        get_resource_path('cache'),  # Standard location: cache/whisper/*.pt
        get_resource_path('../Resources/cache'),  # macOS bundle: Resources/cache/whisper/*.pt
    ]

    for cache_dir in possible_paths:
        whisper_dir = os.path.join(cache_dir, 'whisper')
        if os.path.exists(whisper_dir) and os.path.isdir(whisper_dir):
            # Check if there are actually model files
            model_files = [f for f in os.listdir(whisper_dir) if f.endswith('.pt')]
            if model_files:
                return cache_dir

    return None
