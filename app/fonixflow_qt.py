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
import tempfile
import platform
import multiprocessing

# Cross-platform file locking
try:
    import fcntl  # Unix/macOS
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False
    try:
        import msvcrt  # Windows
        HAS_MSVCRT = True
    except ImportError:
        HAS_MSVCRT = False

from PySide6.QtWidgets import QApplication, QSplashScreen, QProgressBar, QVBoxLayout, QWidget, QLabel  # type: ignore
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont  # type: ignore
from PySide6.QtCore import QTranslator, QLocale, Qt, QTimer  # type: ignore

# Configure logging to ensure output is visible
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)


class FonixFlowSplash(QSplashScreen):
    """Custom splash screen with logo and progress bar."""
    def __init__(self, app_icon_path, logo_path):
        # Create a pixmap for the background
        pixmap = QPixmap(450, 300)
        pixmap.fill(QColor("#22262F"))  # Dark background matching app theme
        super().__init__(pixmap)
        
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        # Main layout logic
        # We use direct drawing for text/logo to ensure it works on the splash pixmap surface
        # But for the progress bar, we can overlay a widget
        
        self.logo_path = logo_path
        self.app_icon_path = app_icon_path
        self.progress = 0
        self.status_text = "Initializing..."
        
        # Add Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 240, 350, 6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #333;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

    def drawContents(self, painter):
        """Draw the splash screen contents."""
        # Draw Background (already filled in __init__ but good to be safe)
        painter.fillRect(self.rect(), QColor("#22262F"))
        
        # Draw Logo
        if os.path.exists(self.logo_path):
            logo = QPixmap(self.logo_path)
            if not logo.isNull():
                # Scale logo to fit nicely
                target_w = 200
                logo_scaled = logo.scaledToWidth(target_w, Qt.SmoothTransformation)
                x = (self.width() - logo_scaled.width()) // 2
                y = (self.height() - logo_scaled.height()) // 2 - 20
                painter.drawPixmap(x, y, logo_scaled)
        
        # Draw Status Text
        painter.setPen(QColor("#a1a1aa"))
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        
        text_rect = self.rect()
        text_rect.setTop(255) # Below progress bar
        text_rect.setHeight(30)
        painter.drawText(text_rect, Qt.AlignCenter, self.status_text)

    def update_progress(self, value, message=None):
        if message:
            self.status_text = message
        self.progress = value
        self.progress_bar.setValue(value)
        self.repaint() # Trigger drawContents
        QApplication.processEvents()


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


def check_single_instance():
    """
    Check if another instance is already running using a lock file.
    Returns lock file handle if successful, None if another instance is running.
    """
    lock_file_path = os.path.join(tempfile.gettempdir(), 'fonixflow.lock')
    
    try:
        # Try to create and lock the lock file
        lock_file = open(lock_file_path, 'w')
        try:
            # Try to acquire exclusive lock (non-blocking)
            if HAS_FCNTL:
                # Unix/macOS
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif HAS_MSVCRT:
                # Windows
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                # Fallback: check if file is already locked by checking if PID is still running
                if os.path.exists(lock_file_path):
                    try:
                        with open(lock_file_path, 'r') as f:
                            old_pid = int(f.read().strip())
                        # Check if process is still running (Unix/macOS)
                        if platform.system() != 'Windows':
                            try:
                                os.kill(old_pid, 0)  # Signal 0 just checks if process exists
                                # Process exists, another instance is running
                                lock_file.close()
                                logger.warning("Another instance of FonixFlow is already running (PID check)")
                                return None
                            except OSError:
                                # Process doesn't exist, remove stale lock file
                                pass
                    except (ValueError, FileNotFoundError):
                        pass
            
            # Write PID to lock file
            lock_file.write(str(os.getpid()))
            lock_file.flush()
            logger.debug(f"Acquired single-instance lock: {lock_file_path}")
            return lock_file
        except (IOError, OSError) as e:
            # Lock failed - another instance is running
            lock_file.close()
            logger.warning(f"Another instance of FonixFlow is already running: {e}")
            return None
    except Exception as e:
        logger.debug(f"Could not create lock file: {e}")
        # If we can't create lock file, continue anyway (might be permission issue)
        return None


def main():
    """Main entry point for Qt application."""
    # Required for PyInstaller to handle multiprocessing correctly
    multiprocessing.freeze_support()

    # SINGLE-INSTANCE CHECK: Use lock file to prevent multiple instances
    lock_file = check_single_instance()
    # Note: Import of FonixFlowQt moved to later to prevent early checking
    # We need to import it to check instance type if we were doing the "bring to front" logic
    # But since we want to delay imports, we'll just rely on the lock file for now.
    # If we really need the raise_() logic, we'd need a lightweight way to find the window.
    
    if lock_file is None:
        logger.info("Exiting - another instance is already running")
        # Simple exit for now as we can't easily get the QWindow without importing heavy stuff
        sys.exit(0)
    
    # Parse command-line arguments BEFORE creating QApplication
    parser = argparse.ArgumentParser(description='FonixFlow - Audio Transcription Tool')
    parser.add_argument('--lang', type=str, help='Override system language (e.g., es, fr, de, zh_CN)')

    # Parse only known args to allow Qt args to pass through
    args, remaining = parser.parse_known_args()

    # Create QApplication with remaining args
    app_name_for_qt = 'FonixFlow'
    if hasattr(sys, 'frozen') and sys.frozen:
        # Running as bundled app
        app = QApplication([app_name_for_qt] + remaining)
    else:
        # Running from source
        app = QApplication([sys.argv[0]] + remaining)
    app.setStyle("Fusion")  # Modern cross-platform style

    # Set application metadata
    app.setApplicationName("FonixFlow")
    app.setOrganizationName("FonixFlow")

    # Setup paths for splash
    base_dir = os.path.dirname(__file__)
    assets_dir = os.path.join(base_dir, '..', 'assets')
    icon_path = os.path.join(assets_dir, 'fonixflow_icon.png')
    logo_path = os.path.join(assets_dir, 'fonixflow_logo.png')

    # --- SHOW SPLASH SCREEN ---
    splash = FonixFlowSplash(icon_path, logo_path)
    splash.show()
    splash.update_progress(10, "Starting application...")
    
    # Set application icon globally
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        # Windows-specific taskbar grouping
        try:
            import ctypes
            myappid = 'fonixflow.transcription.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Load translations
    splash.update_progress(30, "Loading translations...")
    translator, _ = load_translations(app, override_lang=args.lang)
    app._translator = translator

    # --- HEAVY IMPORTS START ---
    splash.update_progress(50, "Loading core modules...")
    
    # Import the main window (this triggers imports of torch, whisper, ffmpeg utils, etc.)
    # We wrap it in a try/except to catch import errors and show them
    try:
        from gui.main_window import FonixFlowQt
    except ImportError as e:
        logger.error(f"Failed to import main window: {e}")
        QMessageBox.critical(None, "Startup Error", f"Failed to load application modules:\n{e}")
        sys.exit(1)

    splash.update_progress(80, "Initializing user interface...")
    
    # Initialize main window
    window = FonixFlowQt()
    
    # Call retranslate_ui after translation is installed
    if hasattr(window, 'retranslate_ui'):
        window.retranslate_ui()
    
    splash.update_progress(100, "Ready!")
    
    # Show main window and finish splash
    window.show()
    splash.finish(window)

    try:
        exit_code = app.exec()
    finally:
        # Release lock file when app exits
        if lock_file:
            try:
                lock_file.close()
                lock_file_path = os.path.join(tempfile.gettempdir(), 'fonixflow.lock')
                if os.path.exists(lock_file_path):
                    os.remove(lock_file_path)
            except Exception as e:
                logger.debug(f"Could not remove lock file: {e}")
    
    sys.exit(exit_code)
