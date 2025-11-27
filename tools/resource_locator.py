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

    if getattr(sys, 'frozen', False):
        # PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # One-file mode
            base_path = sys._MEIPASS
            logger.debug(f"[RESOURCE_LOCATOR] Running in PyInstaller one-file mode, _MEIPASS={base_path}")
        else:
            # One-dir mode (e.g. macOS .app)
            # Resources are typically next to the executable
            base_path = os.path.dirname(os.path.abspath(sys.executable))
            logger.debug(f"[RESOURCE_LOCATOR] Running in PyInstaller one-dir mode, base_path={base_path}")
    else:
        # Running in development mode
        # Assume this file is in tools/ and we want the project root (parent of tools/)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    import shutil
    logger = logging.getLogger(__name__)

    # For macOS .app bundles, check relative to executable location first
    # sys.executable points to Contents/MacOS/FonixFlow in a .app bundle
    possible_paths = []
    
    try:
        if hasattr(sys, 'executable') and sys.executable:
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            # In .app bundle: Contents/MacOS/ffmpeg
            possible_paths.append(os.path.join(exe_dir, 'ffmpeg'))
            # In .app bundle: Contents/Frameworks/ffmpeg
            frameworks_ffmpeg = os.path.join(exe_dir, '..', 'Frameworks', 'ffmpeg')
            possible_paths.append(os.path.abspath(frameworks_ffmpeg))
            # In .app bundle: Contents/Resources/ffmpeg
            resources_ffmpeg = os.path.join(exe_dir, '..', 'Resources', 'ffmpeg')
            possible_paths.append(os.path.abspath(resources_ffmpeg))
            # In .app bundle: Contents/MacOS/bin/ffmpeg
            possible_paths.append(os.path.join(exe_dir, 'bin', 'ffmpeg'))
    except Exception as e:
        logger.debug(f"Could not check executable-relative paths: {e}")

    # Check PyInstaller bundled locations
    possible_paths.extend([
        get_resource_path('ffmpeg'),  # Root of bundle (PyInstaller default - same dir as executable)
        get_resource_path('bin/ffmpeg'),  # Standard location
    ])

    logger.info(f"Searching for ffmpeg in bundled locations...")
    for bundled_ffmpeg in possible_paths:
        exists = os.path.exists(bundled_ffmpeg)
        executable = exists and os.access(bundled_ffmpeg, os.X_OK)
        logger.debug(f"  Checking: {bundled_ffmpeg} (exists={exists}, executable={executable})")
        if exists and executable:
            logger.info(f"✓ Found bundled ffmpeg at: {bundled_ffmpeg}")
            return bundled_ffmpeg

    # Fall back to system ffmpeg
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        logger.warning(f"⚠ Bundled ffmpeg not found, using system ffmpeg at: {system_ffmpeg}")
        logger.warning("  This is normal if ffmpeg is installed system-wide, but bundled version is preferred.")
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
    import shutil
    logger = logging.getLogger(__name__)

    # For macOS .app bundles, check relative to executable location first
    # sys.executable points to Contents/MacOS/FonixFlow in a .app bundle
    possible_paths = []
    
    try:
        if hasattr(sys, 'executable') and sys.executable:
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            # In .app bundle: Contents/MacOS/ffprobe
            possible_paths.append(os.path.join(exe_dir, 'ffprobe'))
            # In .app bundle: Contents/Frameworks/ffprobe
            frameworks_ffprobe = os.path.join(exe_dir, '..', 'Frameworks', 'ffprobe')
            possible_paths.append(os.path.abspath(frameworks_ffprobe))
            # In .app bundle: Contents/Resources/ffprobe
            resources_ffprobe = os.path.join(exe_dir, '..', 'Resources', 'ffprobe')
            possible_paths.append(os.path.abspath(resources_ffprobe))
            # In .app bundle: Contents/MacOS/bin/ffprobe
            possible_paths.append(os.path.join(exe_dir, 'bin', 'ffprobe'))
    except Exception as e:
        logger.debug(f"Could not check executable-relative paths: {e}")

    # Check PyInstaller bundled locations
    possible_paths.extend([
        get_resource_path('ffprobe'),  # Root of bundle (PyInstaller default - same dir as executable)
        get_resource_path('bin/ffprobe'),  # Standard location
    ])

    logger.info(f"Searching for ffprobe in bundled locations...")
    for bundled_ffprobe in possible_paths:
        exists = os.path.exists(bundled_ffprobe)
        executable = exists and os.access(bundled_ffprobe, os.X_OK)
        logger.debug(f"  Checking: {bundled_ffprobe} (exists={exists}, executable={executable})")
        if exists and executable:
            logger.info(f"✓ Found bundled ffprobe at: {bundled_ffprobe}")
            return bundled_ffprobe

    # Fall back to system ffprobe
    system_ffprobe = shutil.which('ffprobe')
    if system_ffprobe:
        logger.warning(f"⚠ Bundled ffprobe not found, using system ffprobe at: {system_ffprobe}")
        logger.warning("  This is normal if ffmpeg is installed system-wide, but bundled version is preferred.")
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
