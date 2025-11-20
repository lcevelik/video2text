"""
Modern Qt-based GUI for FonixFlow

A beautiful, user-friendly interface built with PySide6/Qt.
Features modern design, smooth animations, and excellent cross-platform support.

This is now a simple launcher that imports from the refactored gui package.
"""

import sys
import logging
import os

from PySide6.QtWidgets import QApplication  # type: ignore
from PySide6.QtGui import QIcon  # type: ignore

from gui.main_window import FonixFlowQt

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
    app.setApplicationName("FonixFlow")
    app.setOrganizationName("FonixFlow")

    # Set application icon globally (for taskbar, alt-tab, etc.)
    icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonixflow_icon.png')
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

        # Windows-specific: Set app user model ID for proper taskbar grouping
        try:
            import ctypes
            myappid = 'fonixflow.transcription.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass  # Not on Windows or failed, continue anyway

    window = FonixFlowQt()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
