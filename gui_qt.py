"""
Modern Qt-based GUI for Video2Text

A beautiful, user-friendly interface built with PySide6/Qt.
Features modern design, smooth animations, and excellent cross-platform support.

This is now a simple launcher that imports from the refactored gui package.
"""

import sys
import logging

from PySide6.QtWidgets import QApplication  # type: ignore

from gui.main_window import Video2TextQt

# Configure logging to ensure output is visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for Qt application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern cross-platform style

    # Set application metadata
    app.setApplicationName("Video2Text")
    app.setOrganizationName("Video2Text")

    window = Video2TextQt()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
