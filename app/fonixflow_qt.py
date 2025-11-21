"""
Modern Qt-based GUI for FonixFlow

A beautiful, user-friendly interface built with PySide6/Qt.
Features modern design, smooth animations, and excellent cross-platform support.

This is now a simple launcher that imports from the refactored gui package.
"""

import sys
import logging
import os
import argparse

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


def load_translations(app, override_lang=None):
    """
    Load translation files based on system locale or override.

    Automatically detects the system language and loads the appropriate
    translation file. Falls back to English if translation not available.

    Args:
        app: QApplication instance
        override_lang: Optional language code to override system detection (e.g., 'es', 'fr', 'de')
                      Useful for testing without changing system language.

    Returns:
        tuple: (translator, locale_name) or (None, 'en_US') if no translation loaded
    """
    # Get system locale or use override
    if override_lang:
        locale_name = override_lang
        lang_code = override_lang.split('_')[0]
        logger.info(f"Language override: {override_lang} (using --lang flag)")
    else:
        system_locale = QLocale.system()
        locale_name = system_locale.name()  # e.g., 'en_US', 'es_ES', 'fr_FR', 'zh_CN'
        lang_code = locale_name.split('_')[0]
        logger.info(f"System locale detected: {locale_name} (language: {lang_code})")

    # If English, no translation needed
    if lang_code == 'en':
        logger.info("English locale detected, using default strings")
        return None, locale_name

    # Look for translation file
    # Try specific locale first (e.g., zh_CN.qm), then language code (e.g., zh.qm)
    # Also try .ts files as fallback for testing
    i18n_dir = os.path.join(os.path.dirname(__file__), '..', 'i18n')
    translation_files = [
        os.path.join(i18n_dir, f"fonixflow_{locale_name}.qm"),  # Specific: es_ES.qm
        os.path.join(i18n_dir, f"fonixflow_{lang_code}.qm"),    # General: es.qm
        os.path.join(i18n_dir, f"fonixflow_{locale_name}.ts"),  # Fallback: es_ES.ts
        os.path.join(i18n_dir, f"fonixflow_{lang_code}.ts"),    # Fallback: es.ts
    ]

    translator = None
    for translation_file in translation_files:
        if os.path.exists(translation_file):
            translator = QTranslator()
            # QTranslator can load both .qm and .ts files
            if translator.load(translation_file):
                app.installTranslator(translator)
                file_type = "compiled (.qm)" if translation_file.endswith('.qm') else "source (.ts)"
                logger.info(f"Translation loaded: {translation_file} [{file_type}]")
                return translator, locale_name
            else:
                logger.warning(f"Failed to load translation: {translation_file}")

    # No translation found, fall back to English
    logger.info(f"No translation found for {locale_name}, using English")
    return None, locale_name


def main():
    """Main entry point for Qt application."""
    # Parse command-line arguments BEFORE creating QApplication
    # QApplication will consume Qt-specific args, so we parse first
    parser = argparse.ArgumentParser(description='FonixFlow - Audio Transcription Tool')
    parser.add_argument('--lang', type=str, help='Override system language (e.g., es, fr, de, zh_CN)')

    # Parse only known args to allow Qt args to pass through
    args, remaining = parser.parse_known_args()

    # Create QApplication with remaining args
    app = QApplication([sys.argv[0]] + remaining)
    app.setStyle("Fusion")  # Modern cross-platform style

    # Set application metadata
    app.setApplicationName("FonixFlow")
    app.setOrganizationName("FonixFlow")

    # Load translations based on system locale or override
    # Store translator to prevent garbage collection
    translator, _ = load_translations(app, override_lang=args.lang)
    app._translator = translator  # Keep reference on QApplication

    # Set application icon globally (for taskbar, alt-tab, etc.)
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonixflow_icon.png')
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
    # Call retranslate_ui after translation is installed
    if hasattr(window, 'retranslate_ui'):
        window.retranslate_ui()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
