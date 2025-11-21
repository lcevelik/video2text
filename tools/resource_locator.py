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
        logger.debug(f"Running in PyInstaller bundle mode, _MEIPASS={base_path}")
    except AttributeError:
        # Running in development mode
        base_path = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"Running in development mode, base_path={base_path}")

    full_path = os.path.join(base_path, relative_path)
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
    possible_paths = [
        get_resource_path('bin/ffmpeg'),  # Standard location
        get_resource_path('../Frameworks/bin/ffmpeg'),  # macOS bundle location
    ]

    logger.info(f"Searching for ffmpeg in bundled locations...")
    for bundled_ffmpeg in possible_paths:
        logger.info(f"  Checking: {bundled_ffmpeg} (exists={os.path.exists(bundled_ffmpeg)}, executable={os.path.exists(bundled_ffmpeg) and os.access(bundled_ffmpeg, os.X_OK)})")
        if os.path.exists(bundled_ffmpeg) and os.access(bundled_ffmpeg, os.X_OK):
            logger.info(f"✓ Found bundled ffmpeg at: {bundled_ffmpeg}")
            return bundled_ffmpeg

    # Fall back to system ffmpeg
    import shutil
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        logger.info(f"✓ Using system ffmpeg at: {system_ffmpeg}")
        return system_ffmpeg

    logger.error("ffmpeg not found in any location!")
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
    # Check multiple possible bundled locations
    possible_paths = [
        get_resource_path('bin/ffprobe'),  # Standard location
        get_resource_path('../Frameworks/bin/ffprobe'),  # macOS bundle location
    ]

    for bundled_ffprobe in possible_paths:
        if os.path.exists(bundled_ffprobe) and os.access(bundled_ffprobe, os.X_OK):
            return bundled_ffprobe

    # Fall back to system ffprobe
    import shutil
    system_ffprobe = shutil.which('ffprobe')
    if system_ffprobe:
        return system_ffprobe

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
