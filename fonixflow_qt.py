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
from PySide6.QtCore import QTranslator, QLocale  # type: ignore

from gui.main_window import FonixFlowQt

# Configure logging to ensure output is visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


def load_translations(app):
    """
    Load translation files based on system locale.

    Automatically detects the system language and loads the appropriate
    translation file. Falls back to English if translation not available.

    Args:
        app: QApplication instance

    Returns:
        tuple: (translator, locale_name) or (None, 'en_US') if no translation loaded
    """
    # Get system locale
    system_locale = QLocale.system()
    locale_name = system_locale.name()  # e.g., 'en_US', 'es_ES', 'fr_FR', 'zh_CN'

    # Extract language code (e.g., 'es' from 'es_ES')
    lang_code = locale_name.split('_')[0]

    logger.info(f"System locale detected: {locale_name} (language: {lang_code})")

    # If English, no translation needed
    if lang_code == 'en':
        logger.info("English locale detected, using default strings")
        return None, locale_name

    # Look for translation file
    # Try specific locale first (e.g., zh_CN.qm), then language code (e.g., zh.qm)
    i18n_dir = os.path.join(os.path.dirname(__file__), 'i18n')
    translation_files = [
        os.path.join(i18n_dir, f"fonixflow_{locale_name}.qm"),  # Specific: es_ES.qm
        os.path.join(i18n_dir, f"fonixflow_{lang_code}.qm"),    # General: es.qm
    ]

    translator = None
    for translation_file in translation_files:
        if os.path.exists(translation_file):
            translator = QTranslator()
            if translator.load(translation_file):
                app.installTranslator(translator)
                logger.info(f"Translation loaded: {translation_file}")
                return translator, locale_name
            else:
                logger.warning(f"Failed to load translation: {translation_file}")

    # No translation found, fall back to English
    logger.info(f"No translation found for {locale_name}, using English")
    return None, locale_name


def main():
    """Main entry point for Qt application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern cross-platform style

    # Set application metadata
    app.setApplicationName("FonixFlow")
    app.setOrganizationName("FonixFlow")

    # Load translations based on system locale
    load_translations(app)

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
