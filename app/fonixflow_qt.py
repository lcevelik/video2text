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

# Add parent directory to sys.path to ensure 'gui' and 'transcription' modules are found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        # Draw Background
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
    """
    # Get system locale or use override
    if override_lang:
        locale_name = override_lang
        lang_code = override_lang.split('_')[0]
        logger.info(f"Language override: {override_lang} (using --lang flag)")
    else:
        system_locale = QLocale.system()
        locale_name = system_locale.name()
        lang_code = locale_name.split('_')[0]
        logger.info(f"System locale detected: {locale_name} (language: {lang_code})")

    # If English, no translation needed
    if lang_code == 'en':
        logger.info("English locale detected, using default strings")
        return None, locale_name

    # Look for translation file
    i18n_dir = os.path.join(os.path.dirname(__file__), '..', 'i18n')
    translation_files = [
        os.path.join(i18n_dir, f"fonixflow_{locale_name}.qm"),
        os.path.join(i18n_dir, f"fonixflow_{lang_code}.qm"),
        os.path.join(i18n_dir, f"fonixflow_{locale_name}.ts"),
        os.path.join(i18n_dir, f"fonixflow_{lang_code}.ts"),
    ]

    translator = None
    for translation_file in translation_files:
        if os.path.exists(translation_file):
            translator = QTranslator()
            if translator.load(translation_file):
                app.installTranslator(translator)
                file_type = "compiled (.qm)" if translation_file.endswith('.qm') else "source (.ts)"
                logger.info(f"Translation loaded: {translation_file} [{file_type}]")
                return translator, locale_name
            else:
                logger.warning(f"Failed to load translation: {translation_file}")

    logger.info(f"No translation found for {locale_name}, using English")
    return None, locale_name


def check_single_instance():
    """
    Check if another instance is already running using a lock file.
    """
    lock_file_path = os.path.join(tempfile.gettempdir(), 'fonixflow.lock')
    
    try:
        lock_file = open(lock_file_path, 'w')
        try:
            if HAS_FCNTL:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif HAS_MSVCRT:
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                if os.path.exists(lock_file_path):
                    try:
                        with open(lock_file_path, 'r') as f:
                            old_pid = int(f.read().strip())
                        if platform.system() != 'Windows':
                            try:
                                os.kill(old_pid, 0)
                                lock_file.close()
                                logger.warning("Another instance of FonixFlow is already running (PID check)")
                                return None
                            except OSError:
                                pass
                    except (ValueError, FileNotFoundError):
                        pass
            
            lock_file.write(str(os.getpid()))
            lock_file.flush()
            return lock_file
        except (IOError, OSError) as e:
            lock_file.close()
            logger.warning(f"Another instance of FonixFlow is already running: {e}")
            return None
    except Exception as e:
        logger.debug(f"Could not create lock file: {e}")
        return None


def main():
    """Main entry point for Qt application."""
    # Required for PyInstaller to handle multiprocessing correctly
    multiprocessing.freeze_support()

    # SINGLE-INSTANCE CHECK: Use lock file to prevent multiple instances
    lock_file = check_single_instance()
    
    if lock_file is None:
        logger.info("Exiting - another instance is already running")
        sys.exit(0)
    
    # Parse command-line arguments BEFORE creating QApplication
    parser = argparse.ArgumentParser(description='FonixFlow - Audio Transcription Tool')
    parser.add_argument('--lang', type=str, help='Override system language (e.g., es, fr, de, zh_CN)')

    # Parse only known args to allow Qt args to pass through
    args, remaining = parser.parse_known_args()

    # Create QApplication with remaining args
    app_name_for_qt = 'FonixFlow'
    if hasattr(sys, 'frozen') and sys.frozen:
        app = QApplication([app_name_for_qt] + remaining)
    else:
        app = QApplication([sys.argv[0]] + remaining)
    app.setStyle("Fusion")

    app.setApplicationName("FonixFlow")
    app.setOrganizationName("FonixFlow")

    # Setup paths for splash
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(sys.executable))
        assets_dir = os.path.join(base_dir, 'assets')
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, '..', 'assets')

    icon_path = os.path.join(assets_dir, 'fonixflow_icon.png')
    logo_path = os.path.join(assets_dir, 'logo.png')

    # --- SHOW SPLASH SCREEN ---
    splash = FonixFlowSplash(icon_path, logo_path)
    splash.show()
    splash.update_progress(10, "Starting application...")
    
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
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
    
    try:
        from gui.main_window import FonixFlowQt
    except ImportError as e:
        logger.error(f"Failed to import main window: {e}")
        # We can't show QMessageBox if app isn't ready? 
        # Actually we have QApplication now, so we can.
        # But let's just print/log and exit
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

    splash.update_progress(80, "Initializing user interface...")
    
    # Initialize main window
    window = FonixFlowQt()
    
    if hasattr(window, 'retranslate_ui'):
        window.retranslate_ui()
    
    splash.update_progress(100, "Ready!")
    
    # Show main window and finish splash
    window.show()
    splash.finish(window)

    try:
        exit_code = app.exec()
    finally:
        if lock_file:
            try:
                lock_file.close()
                lock_file_path = os.path.join(tempfile.gettempdir(), 'fonixflow.lock')
                if os.path.exists(lock_file_path):
                    os.remove(lock_file_path)
            except Exception as e:
                logger.debug(f"Could not remove lock file: {e}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
