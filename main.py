"""
Main Entry Point

Video to Text Transcription Application
Transcribes audio from video files using OpenAI Whisper.
"""

import sys
import logging
import tkinter as tk
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcription.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        import whisper
    except ImportError:
        missing.append("openai-whisper")
    
    try:
        import torch
    except ImportError:
        missing.append("torch")
    
    try:
        import ffmpeg
    except ImportError:
        # ffmpeg-python is optional, we use subprocess instead
        pass
    
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        logger.error("Please install dependencies: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main application entry point."""
    logger.info("Starting Video to Text Transcription Application")
    
    # Check dependencies
    if not check_dependencies():
        print("\n" + "="*60)
        print("ERROR: Missing required dependencies!")
        print("Please install dependencies by running:")
        print("  pip install -r requirements.txt")
        print("="*60 + "\n")
        sys.exit(1)
    
    # Check ffmpeg
    import subprocess
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n" + "="*60)
        print("WARNING: ffmpeg is not installed or not in PATH!")
        print("Please install ffmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("           Or use: winget install ffmpeg")
        print("  Mac:     brew install ffmpeg")
        print("  Linux:   sudo apt install ffmpeg")
        print("="*60 + "\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Import GUI after dependency checks
    try:
        from gui import TranscriptionApp
    except ImportError as e:
        logger.error(f"Failed to import GUI module: {e}")
        sys.exit(1)
    
    # Create and run GUI
    try:
        root = tk.Tk()
        app = TranscriptionApp(root)
        logger.info("Application started successfully")
        root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

