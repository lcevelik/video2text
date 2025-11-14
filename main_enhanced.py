"""
Enhanced Video to Text Transcription Application

This is the main entry point for the enhanced version with:
- Basic/Advanced modes
- Audio recording
- Automatic model selection
- Multi-language support

Author: Video2Text Team
License: MIT
"""

import sys
import os
import logging
from pathlib import Path


def setup_logging():
    """Configure logging for the application."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(logs_dir / 'transcription.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Video/Audio to Text Transcription - Enhanced Version")
    logger.info("=" * 60)

    return logger


def check_dependencies():
    """Check if all required dependencies are installed."""
    logger = logging.getLogger(__name__)
    missing_deps = []

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required!")
        logger.error(f"Current version: {sys.version}")
        return False

    # Check core dependencies
    required_modules = {
        'whisper': 'openai-whisper',
        'torch': 'torch',
        'torchaudio': 'torchaudio',
        'ffmpeg': 'ffmpeg-python',
        'numpy': 'numpy',
        'sounddevice': 'sounddevice',
        'scipy': 'scipy'
    }

    logger.info("Checking dependencies...")

    for module, package in required_modules.items():
        try:
            __import__(module)
            logger.debug(f"✓ {module} found")
        except ImportError:
            logger.warning(f"✗ {module} not found")
            missing_deps.append(package)

    if missing_deps:
        logger.error("Missing required dependencies:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        logger.error("\nInstall missing dependencies with:")
        logger.error(f"  pip install {' '.join(missing_deps)}")
        return False

    logger.info("✓ All dependencies found")
    return True


def check_ffmpeg():
    """Check if ffmpeg is available in PATH."""
    logger = logging.getLogger(__name__)

    import subprocess

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✓ FFmpeg found: {version_line}")
            return True
        else:
            logger.warning("FFmpeg not responding correctly")
            return False

    except FileNotFoundError:
        logger.error("✗ FFmpeg not found in PATH")
        logger.error("\nFFmpeg is required for audio extraction.")
        logger.error("Download from: https://ffmpeg.org/download.html")
        logger.error("Or install via package manager:")
        logger.error("  Windows: choco install ffmpeg")
        logger.error("  macOS: brew install ffmpeg")
        logger.error("  Linux: sudo apt install ffmpeg")
        return False
    except Exception as e:
        logger.warning(f"Could not check FFmpeg: {e}")
        return False


def check_gpu():
    """Check GPU availability."""
    logger = logging.getLogger(__name__)

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_count = torch.cuda.device_count()
            logger.info(f"✓ GPU acceleration available: {gpu_name}")
            logger.info(f"  GPU count: {gpu_count}")

            # Check CUDA version
            cuda_version = torch.version.cuda
            logger.info(f"  CUDA version: {cuda_version}")

            return True
        else:
            logger.info("ℹ GPU not available, will use CPU")
            logger.info("  (GPU acceleration significantly speeds up transcription)")
            return False

    except Exception as e:
        logger.warning(f"Could not check GPU: {e}")
        return False


def show_startup_info():
    """Display startup information."""
    logger = logging.getLogger(__name__)

    import platform

    logger.info("\nSystem Information:")
    logger.info(f"  Platform: {platform.system()} {platform.release()}")
    logger.info(f"  Python: {sys.version.split()[0]}")
    logger.info(f"  Working directory: {Path.cwd()}")
    logger.info("")


def main():
    """Main entry point for the enhanced application."""
    # Setup logging
    logger = setup_logging()

    # Show startup info
    show_startup_info()

    # Check dependencies
    logger.info("Starting dependency checks...")

    if not check_dependencies():
        logger.error("\n❌ Dependency check failed!")
        logger.error("Please install missing dependencies and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Check ffmpeg
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        logger.warning("\n⚠️  FFmpeg not found - application may not work correctly")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    # Check GPU
    check_gpu()

    logger.info("\n✓ All checks passed!")
    logger.info("Starting GUI...\n")

    # Import and start GUI
    try:
        import tkinter as tk
        from gui_enhanced import EnhancedTranscriptionApp

        # Create main window
        root = tk.Tk()

        # Set window properties
        root.title("Video/Audio to Text - Whisper Transcription")

        # Create application
        app = EnhancedTranscriptionApp(root)

        logger.info("GUI initialized successfully")
        logger.info("Application ready!")
        logger.info("=" * 60)

        # Start main loop
        root.mainloop()

    except ImportError as e:
        logger.error(f"Failed to import GUI module: {e}")
        logger.error("Make sure gui_enhanced.py is in the same directory")
        input("\nPress Enter to exit...")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
