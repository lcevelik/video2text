"""
Main window for the Video2Text Qt GUI.
"""

import sys
import os
import logging
import json
import time
import subprocess
import platform
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (  # type: ignore
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QFileDialog,
    QMessageBox, QStackedWidget, QListWidget, QListWidgetItem, QMenu, QDialog,
    QComboBox, QCheckBox, QGroupBox, QSystemTrayIcon, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QEvent, QCoreApplication, QThread, Signal  # type: ignore
from PySide6.QtGui import QPalette, QIcon, QAction  # type: ignore

from gui.theme import Theme
from gui.widgets import ModernButton, Card, DropZone, VUMeter, ModernTabBar, CollapsibleSidebar
from gui.workers import RecordingWorker, TranscriptionWorker, AudioPreviewWorker
from gui.dialogs import MultiLanguageChoiceDialog, RecordingDialog, LogsDialog, LicenseLimitationsDialog
from gui.utils import check_audio_input_devices, get_platform, get_platform_audio_setup_help, has_gpu_available
from gui.managers import SettingsManager, ThemeManager, FileManager
from gui.icons import get_icon
from gui.update_manager import UpdateScheduler
from gui.update_dialog import UpdateDialog
from gui.controllers import LicenseController, RecordingController, TranscriptionController
from app.version import __version__
# Note: Transcriber is imported locally where needed to speed up app startup

logger = logging.getLogger(__name__)

# Helper function to set icon with proper sizing — imported from gui.utils (single source of truth)
from gui.utils import set_icon


class DependencyLoaderThread(QThread):
    """Background thread to preload heavy dependencies (torch/whisper) after GUI startup."""

    loading_complete = Signal()  # Signal emitted when loading is done

    def run(self):
        """Load torch and whisper in background to warm up the imports."""
        try:
            logger.info("Background dependency loader: Starting to preload torch and whisper...")

            # Import torch
            import torch
            logger.info(f"Background loader: torch loaded (CUDA available: {torch.cuda.is_available()})")

            # Import whisper
            import whisper
            logger.info("Background loader: whisper loaded")

            logger.info("Background dependency loader: Preloading complete!")
            self.loading_complete.emit()
        except Exception as e:
            logger.warning(f"Background dependency loader failed (non-critical): {e}")


class FonixFlowQt(LicenseController, RecordingController, TranscriptionController, QMainWindow):
    """Modern Qt-based main window."""

    def __init__(self):
        super().__init__()
        # Initialize license_valid to False first (will be updated after license check)
        self.license_valid = False
        self.setWindowTitle(self.tr("FonixFlow Free - Whisper Transcription"))
        self.setMinimumSize(1000, 700)

        # Set application icon
        from PySide6.QtGui import QIcon
        from tools.resource_locator import get_resource_path
        icon_path = get_resource_path('assets/fonixflow_icon.png')
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.instance().setWindowIcon(app_icon)

        # Initialize managers
        # Initialize path manager and migrate old files
        from gui.managers.path_manager import PathManager
        PathManager.migrate_old_files()
        
        # Initialize settings manager (uses PathManager for config location)
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings  # Keep for backward compatibility
        self.theme_manager = ThemeManager(self, self.settings_manager.get("theme_mode", "dark"))
        self.file_manager = FileManager(self)

        # License key state
        _lk = self.settings_manager.get('license_key', None)
        logger.info(f"License: loading key from settings: {_lk[:8]}..." if _lk else "License: no key in settings")
        self.license_key = self.settings_manager.get("license_key", None)
        self.license_valid = False
        self.check_license_key_on_startup()
        
        # Show license limitations dialog if no valid license
        if not self.license_valid:
            self.show_license_limitations_dialog()

        # Audio processing settings
        self.enable_audio_filters = self.settings_manager.get("enable_audio_filters", False)

        # Transcription settings
        self.enable_deep_scan = self.settings_manager.get("enable_deep_scan", False)

        # State
        self.video_path = None
        self.transcription_result = None
        self.transcription_worker = None  # QThread worker for transcription
        self.theme_mode = self.theme_manager.theme_mode
        self.is_dark_mode = self.theme_manager.is_dark_mode

        self.transcription_start_time = None
        self.performance_overlay = None
        self.model_name_label = None

        # Multi-language dialog state
        self.multi_language_mode = None
        self.allowed_languages = []
        self.single_language_type = None
        # Ensure settings widgets are always initialized
        self.audio_options_widget = QWidget()
        audio_options_layout = QVBoxLayout(self.audio_options_widget)
        audio_options_layout.setContentsMargins(0, 0, 0, 0)
        audio_options_layout.setSpacing(2)
        audio_filter_btn = self.create_toggle_option_btn(
            "sliders", "Enhance Audio",
            self.enable_audio_filters,
            self.toggle_audio_filters,
            indent=32
        )
        audio_filter_btn.setToolTip("Removes noise, boosts clarity")
        audio_options_layout.addWidget(audio_filter_btn)

        self.transcription_options_widget = QWidget()
        transcription_options_layout = QVBoxLayout(self.transcription_options_widget)
        transcription_options_layout.setContentsMargins(0, 0, 0, 0)
        transcription_options_layout.setSpacing(2)
        deep_scan_btn = self.create_toggle_option_btn(
            "search", "Deep Scan",
            self.enable_deep_scan,
            self.toggle_deep_scan,
            indent=32
        )
        deep_scan_btn.setToolTip("Segments audio into chunks for accurate multi-language detection (slower but more accurate)")
        transcription_options_layout.addWidget(deep_scan_btn)

        logger.info("Calling setup_ui() in FonixFlowQt __init__")
        self.setup_ui()
        logger.info("setup_ui() completed in FonixFlowQt __init__")
        self.theme_manager.apply_theme()
        # Ensure ffmpeg is available to pydub across the app
        try:
            from app.audio_extractor import AudioExtractor
            AudioExtractor.configure_ffmpeg_converter()
        except Exception as _fferr:
            logger.debug(f"FFmpeg configuration skipped: {_fferr}")
        self.center_window()

        # Runtime compatibility checks (Python 3.13 audio stack)
        try:
            self.check_runtime_compat()
        except Exception as _compat_err:
            logger.debug(f"Compat check skipped: {_compat_err}")
        # Removed eager Whisper model preloading: models now load on-demand
        # when transcription actually starts (single-language loads 1 model;
        # multi-language path path loads detection+transcription models lazily).

        # Start background dependency loader to preload torch/whisper
        # This improves responsiveness when user clicks transcribe
        self.dependency_loader = DependencyLoaderThread()
        self.dependencies_loaded = False

        def on_dependencies_loaded():
            self.dependencies_loaded = True
            logger.info("Heavy dependencies preloaded - transcription will start faster!")

        self.dependency_loader.loading_complete.connect(on_dependencies_loaded)
        # Start loading after a short delay to let the GUI render first
        QTimer.singleShot(500, self.dependency_loader.start)

        # Setup system tray for background operation
        self.setup_system_tray()

        # Start audio preview worker for VU meters
        self.audio_preview_worker = None
        self.start_audio_preview()

        # Initialize update scheduler
        self.update_scheduler = UpdateScheduler(__version__)
        # Check for updates after app is fully loaded (after 3 seconds)
        QTimer.singleShot(3000, self.check_for_updates)

    def _load_encoded_licenses(self, filepath):
        """
        Decode an encoded license file.

        Args:
            filepath: Path to encoded licenses.dat file

        Returns:
            List of valid license keys
        """
        import base64

        # Read encoded file
        with open(filepath, 'rb') as f:
            encoded = f.read()

        # Base64 decode
        xor_bytes = base64.b64decode(encoded)

        # XOR with key to decode
        from app.transcriber import LICENSE_XOR_KEY
        key = LICENSE_XOR_KEY
        content_bytes = bytearray()
        for i, byte in enumerate(xor_bytes):
            content_bytes.append(byte ^ key[i % len(key)])

        # Decode to string and split into lines
        content = bytes(content_bytes).decode('utf-8')
        valid_keys = [line.strip() for line in content.split('\n') if line.strip()]

        return valid_keys

    def check_license_key_on_startup(self):
        """Check license key validity on startup."""
        logger.info(f"check_license_key_on_startup: key={self.license_key}")
        if self.license_key:
            self.license_valid = self.validate_license_key(self.license_key)
            logger.info(f"License key checked: valid={self.license_valid}")
        else:
            self.license_valid = False
            logger.info("No license key found on startup.")
        # Update window title based on license status
        self.update_window_title()
    
    def update_window_title(self):
        """Update window title to reflect license status."""
        if hasattr(self, 'license_valid') and self.license_valid:
            self.setWindowTitle(self.tr("FonixFlow - Whisper Transcription"))
        else:
            self.setWindowTitle(self.tr("FonixFlow Free - Whisper Transcription"))
    
    def show_license_limitations_dialog(self):
        """Show dialog explaining limitations for unlicensed users."""
        logger.info("Showing license limitations dialog")
        dialog = LicenseLimitationsDialog(self)
        dialog.exec()

    def validate_license_key(self, key):
        """Validate license key using local file first, then LemonSqueezy API."""
        from pathlib import Path
        import base64

        fonixflow_dir = Path.home() / ".fonixflow"
        license_file_encoded = fonixflow_dir / "licenses.dat"
        license_file_plain = fonixflow_dir / "licenses.txt"

        # Try encoded file first
        if license_file_encoded.exists():
            logger.info(f"validate_license_key: checking key={key[:8]}... in {license_file_encoded} (encoded)")
            try:
                valid_keys = self._load_encoded_licenses(license_file_encoded)
                if key.strip() in valid_keys:
                    logger.info("License key valid (encoded file)")
                    return True
            except Exception as e:
                logger.error(f"Error reading encoded license file: {e}")

        # Fall back to plaintext file (for development)
        if license_file_plain.exists():
            logger.info(f"validate_license_key: checking key={key[:8]}... in {license_file_plain}")
            try:
                with open(license_file_plain, "r") as f:
                    valid_keys = [line.strip() for line in f if line.strip()]
                if key.strip() in valid_keys:
                    logger.info("License key valid (plaintext file)")
                    return True
            except Exception as e:
                logger.error(f"Error reading plaintext license file: {e}")
        # If not found locally, check LemonSqueezy API
        try:
            import requests
            url = "https://api.lemonsqueezy.com/v1/licenses/validate"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"license_key": key}
            resp = requests.post(url, headers=headers, data=data, timeout=10)
            result = resp.json()
            logger.info(f"License API response: {result}")
            return result.get("status") == "active"
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return False

    def prompt_for_license_key(self, force=False):
        """Prompt user for license key and validate.
        
        Args:
            force: If True, allow prompting even during transcription (default: False)
        """
        from gui.dialogs import LicenseKeyDialog
        import traceback
        import inspect
        
        # Safety check: Don't prompt during active transcription unless forced
        if not force and hasattr(self, 'transcription_worker') and self.transcription_worker and self.transcription_worker.isRunning():
            logger.warning("License dialog blocked: Transcription is in progress")
            return False
        
        logger.info("Prompting for license key dialog...")
        # Get full call stack for debugging
        try:
            stack = traceback.extract_stack()
            logger.info("=== CALL STACK ===")
            for frame in stack[-8:-1]:  # Show last 7 frames
                logger.info(f"  File: {frame.filename}, Line: {frame.lineno}, Function: {frame.name}, Code: {frame.line}")
            logger.info("==================")
        except Exception as e:
            logger.error(f"Error getting call stack: {e}")
        
        dlg = LicenseKeyDialog(self, current_key=self.license_key)
        result = dlg.exec()
        logger.info(f"License dialog result: {result}, valid={dlg.valid}, key={dlg.license_key}")
        if result == QDialog.Accepted and dlg.valid:
            self.license_key = dlg.license_key
            self.license_valid = True
            self.settings_manager.save_settings(license_key=self.license_key)
            logger.info("License key accepted and saved.")
            # Update window title when license becomes valid
            self.update_window_title()
            return True
        else:
            # Don't deactivate existing license if user just cancelled
            if self.license_valid and self.license_key:
                logger.info(f"License dialog cancelled - preserving existing valid license (key: {self.license_key})")
            else:
                logger.info("License dialog cancelled or key not validated - no existing license to preserve.")
            return False

    def show_activation_dialog(self):
        """Show activation dialog for entering license key."""
        logger.info("Activate button clicked - showing activation dialog")
        result = self.prompt_for_license_key(force=True)  # Force=True allows from Settings button
        if result:
            # Re-validate to ensure license is still valid
            self.check_license_key_on_startup()
            # Update window title (check_license_key_on_startup already calls update_window_title)
            QMessageBox.information(
                self,
                self.tr("Activation Successful"),
                self.tr("Your license key has been activated successfully! More features are now available.")
            )
        return result

    def is_license_active(self):
        """Check if license is currently active and valid."""
        return self.license_valid and self.license_key is not None

    def show_logs_dialog(self):
        """Show the logs dialog."""
        logger.info("Opening logs dialog")
        dialog = LogsDialog(self)
        dialog.exec()

    def check_for_updates(self):
        """Check for app updates asynchronously."""
        if not self.update_scheduler.should_check_for_updates():
            logger.debug("Skipping update check (checked recently)")
            return

        try:
            logger.info("Checking for updates...")
            result = self.update_scheduler.manager.check_for_updates()
            self.update_scheduler.mark_check_complete()

            if result.get('available'):
                logger.info(f"Update available: {result.get('version')}")

                # Show update dialog
                dialog = UpdateDialog(result, __version__, self)
                dialog.exec()
            else:
                logger.info("No updates available")
        except Exception as e:
            logger.warning(f"Update check failed: {e}")

    def center_window(self):
        """Center the main window on the primary screen."""
        try:
            frame_geom = self.frameGeometry()
            screen_center = QApplication.primaryScreen().availableGeometry().center()
            frame_geom.moveCenter(screen_center)
            self.move(frame_geom.topLeft())
        except Exception as e:
            logger.warning(f"Error centering window: {e}")

    def setup_system_tray(self):
        """Setup system tray icon for background operation."""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray not available on this system")
            self.tray_icon = None
            return

        # Create tray icon using the app icon
        from tools.resource_locator import get_resource_path
        icon_path = get_resource_path('assets/fonixflow_icon.png')

        if os.path.exists(icon_path):
            tray_icon_image = QIcon(icon_path)
        else:
            # Fallback to app icon
            tray_icon_image = self.windowIcon()

        self.tray_icon = QSystemTrayIcon(tray_icon_image, self)

        # Create tray menu
        tray_menu = QMenu()

        # Show/Restore action
        show_action = QAction("Show FonixFlow", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        # Exit action (truly closes the app)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # Double-click to restore
        self.tray_icon.activated.connect(self.tray_icon_activated)

        # Show the tray icon
        self.tray_icon.show()

        logger.info("System tray icon initialized")

    def tray_icon_activated(self, reason):
        """Handle tray icon activation (double-click, etc.)."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()

    def show_from_tray(self):
        """Restore window from system tray."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        self.raise_()
        logger.info("Window restored from system tray")

    def quit_application(self):
        """Truly quit the application (cleanup and exit)."""
        logger.info("Application exit requested")

        # Hide tray icon
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.hide()

        # Stop audio preview worker
        if self.audio_preview_worker:
            try:
                self.audio_preview_worker.stop()
                self.audio_preview_worker.wait(1000)
            except Exception as e:
                logger.debug(f"Error stopping audio preview: {e}")

        # Stop transcription worker if running
        if self.transcription_worker and self.transcription_worker.isRunning():
            try:
                self.transcription_worker.cancel()
                self.transcription_worker.wait(1000)
            except Exception as e:
                logger.debug(f"Error stopping transcription: {e}")

        # Stop dependency loader if running
        if hasattr(self, 'dependency_loader') and self.dependency_loader.isRunning():
            try:
                self.dependency_loader.wait(1000)
            except Exception as e:
                logger.debug(f"Error stopping dependency loader: {e}")

        # Save settings
        self.save_settings()

        # Quit application
        QApplication.quit()

    def load_settings(self):
        """Load settings from config file (delegated to SettingsManager)."""
        return self.settings_manager.load_settings()

    def save_settings(self):
        """Save settings to config file (delegated to SettingsManager)."""
        self.settings_manager.save_settings(
            theme_mode=self.theme_mode,
            enable_audio_filters=self.enable_audio_filters,
            enable_deep_scan=self.enable_deep_scan
        )

    def check_runtime_compat(self):
        """Warn users on Python 3.13 if pyaudioop is missing (needed for recording)."""
        if sys.version_info >= (3, 13):
            try:
                import audioop
            except ImportError:
                try:
                    import pyaudioop
                except ImportError:
                    logger.critical("Python 3.13+ detected but 'audioop' and 'pyaudioop' are missing.")
                    QMessageBox.critical(
                        self,
                        self.tr("Missing Dependency"),
                        self.tr("Python 3.13 removed the 'audioop' module required for audio recording.\n\n"
                                "Please install 'pyaudioop' to restore functionality:\n"
                                "pip install pyaudioop")
                    )

    def detect_system_theme(self):
        """Detect if system is in dark mode (delegated to ThemeManager)."""
        return self.theme_manager.detect_system_theme()

    def get_effective_theme(self):
        """Get the effective theme based on mode setting (delegated to ThemeManager)."""
        return self.theme_manager.get_effective_theme()

    def apply_theme(self):
        """Apply the current theme to all UI elements (delegated to ThemeManager)."""
        self.theme_manager.apply_theme()

    def cleanup_all_workers(self):
        """Clean up all worker threads before app exit."""
        logger.info("Cleaning up all workers...")
        try:
            # Stop audio preview worker if running
            if hasattr(self, 'audio_preview_worker') and self.audio_preview_worker:
                try:
                    if self.audio_preview_worker.isRunning():
                        logger.info("Stopping audio preview worker...")
                        self.audio_preview_worker.stop()
                        if not self.audio_preview_worker.wait(3000):
                            logger.warning("Audio preview worker did not stop gracefully, terminating...")
                            self.audio_preview_worker.terminate()
                            self.audio_preview_worker.wait(1000)
                except Exception as e:
                    logger.warning(f"Error stopping audio preview worker: {e}")
                finally:
                    try:
                        self.audio_preview_worker.deleteLater()
                    except Exception:
                        pass
                    self.audio_preview_worker = None

            # Stop recording worker if running
            if hasattr(self, 'recording_worker') and self.recording_worker:
                try:
                    if self.recording_worker.isRunning():
                        logger.info("Stopping recording worker...")
                        self.recording_worker.stop()
                        if not self.recording_worker.wait(3000):
                            logger.warning("Recording worker did not stop gracefully, terminating...")
                            self.recording_worker.terminate()
                            self.recording_worker.wait(1000)
                except Exception as e:
                    logger.warning(f"Error stopping recording worker: {e}")
                finally:
                    try:
                        self.recording_worker.deleteLater()
                    except Exception:
                        pass
                    self.recording_worker = None

            # Stop transcription worker if running
            if hasattr(self, 'transcription_worker') and self.transcription_worker:
                try:
                    if self.transcription_worker.isRunning():
                        logger.info("Stopping transcription worker...")
                        self.transcription_worker.cancel()
                        if not self.transcription_worker.wait(5000):
                            logger.warning("Transcription worker did not stop gracefully, terminating...")
                            self.transcription_worker.terminate()
                            self.transcription_worker.wait(1000)
                except Exception as e:
                    logger.warning(f"Error stopping transcription worker: {e}")
                finally:
                    try:
                        self.transcription_worker.deleteLater()
                    except Exception:
                        pass
                    self.transcription_worker = None
        except Exception as e:
            logger.error(f"Error during worker cleanup: {e}")

    def closeEvent(self, event):
        """Handle window close - minimize to tray or fully quit."""
        # Check if we should minimize to tray instead of closing
        if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
            # Minimize to tray instead of closing
            event.ignore()
            self.hide()

            # Show a notification on first minimize
            if not hasattr(self, '_tray_notification_shown'):
                self.tray_icon.showMessage(
                    "FonixFlow",
                    "FonixFlow is running in the background. Double-click the tray icon to restore.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000  # 2 seconds
                )
                self._tray_notification_shown = True

            logger.info("Window minimized to system tray")
            return

        # If no tray or user chose to exit, do full cleanup
        try:
            self.cleanup_all_workers()
        except Exception as e:
            logger.warning(f"Error while shutting down workers: {e}")

        # Save settings
        self.save_settings()

        # Accept the event to allow closing
        event.accept()

    def update_all_cards_theme(self):
        """Update theme for all Card widgets (delegated to ThemeManager)."""
        self.theme_manager.update_all_cards_theme()

    def eventFilter(self, obj, event):
        """No-op, was for device refresh."""
        return super().eventFilter(obj, event)

    def changeEvent(self, event):
        """No-op, was for device refresh."""
        return super().changeEvent(event)

    def update_sidebar_theme(self, sidebar):
        """Update sidebar theme colors (delegated to ThemeManager)."""
        self.theme_manager.update_sidebar_theme(sidebar)

    def setup_ui(self):
        """Setup the main UI with modern navigation."""
        logger.info("setup_ui() started")
        central = QWidget()
        self.setCentralWidget(central)

        # Main vertical layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)



        # Top bar with logo
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Content area with sidebar + tabs (tabs moved to right side)
        try:
            content_area = self.create_content_area()
            main_layout.addWidget(content_area, 1)
            logger.info("create_content_area() succeeded")
        except Exception as e:
            logger.error(f"create_content_area() failed: {e}")

        # Status bar
        self.statusBar().showMessage(self.tr("Ready"))
        self.statusBar().setStyleSheet("background-color: #F5F5F5; color: #666; padding: 5px;")
        logger.info("setup_ui() finished")

    def create_top_bar(self):
        """Create top bar with title."""
        from PySide6.QtGui import QPixmap
        top_bar = QWidget()

        # Set background color to match logo background
        top_bar.setStyleSheet("background-color: #22262F;")

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(0, 0, 0, 0)

        # Logo - scale down to 1/3 of original size
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        from tools.resource_locator import get_resource_path
        logo_path = get_resource_path('assets/logo.png')
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            # Scale logo down to 1/3 of original size
            scaled_width = pixmap.width() // 3
            scaled_height = pixmap.height() // 3
            scaled_pixmap = pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            # Adjust top bar height to match scaled logo height
            top_bar.setMinimumHeight(scaled_height)
            top_bar.setMaximumHeight(scaled_height)
        layout.addWidget(logo_label)

        return top_bar

    def create_settings_card(self):
        """Create settings card for recordings directory."""
        card = Card(self.tr("Recordings Settings"), self.is_dark_mode)

        # Current directory display
        dir_label = QLabel(self.tr("Recordings save to:"))
        dir_label.setStyleSheet(f"font-size: 12px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        card.content_layout.addWidget(dir_label)

        # Create or update the display label (instance variable)
        if not hasattr(self, 'recordings_dir_display'):
            self.recordings_dir_display = QLabel(self.settings["recordings_dir"])
            self.recordings_dir_display.setStyleSheet(
                f"font-size: 13px; color: {Theme.get('accent', self.is_dark_mode)}; padding: 8px; "
                f"background-color: {Theme.get('bg_secondary', self.is_dark_mode)}; border-radius: 6px; border: 1px solid {Theme.get('border', self.is_dark_mode)};"
            )
            self.recordings_dir_display.setWordWrap(True)
        else:
            # Update the text in case it changed
            self.recordings_dir_display.setText(self.settings["recordings_dir"])

        card.content_layout.addWidget(self.recordings_dir_display)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        def style_settings_btn(btn):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                    color: {Theme.get('text_primary', self.is_dark_mode)};
                    border: 2px solid {Theme.get('border', self.is_dark_mode)};
                    border-radius: 12px;
                    padding: 15px 10px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:focus {{
                    outline: none;
                }}
                QPushButton:hover {{
                    background-color: {Theme.get('accent', self.is_dark_mode)};
                    color: white;
                    border-color: {Theme.get('accent', self.is_dark_mode)};
                }}
            """)

        # Removed Change Folder and Open Folder buttons as requested

        card.content_layout.addLayout(btn_row)

        return card

    def create_content_area(self):
        """Create content area with tab stack, including new Settings tab."""
        # State for recording
        self.is_recording = False
        self.recording_start_time = None
        self.recording_worker = None  # QThread worker for recording
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_duration)
        self.selected_mic_device = None  # User-selected microphone device
        self.selected_speaker_device = None  # User-selected speaker device
        
        self.recording_time_limit = None

        # Main container
        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Tab content stack - order: Record, Upload, Transcript, Settings
        self.basic_tab_stack = QStackedWidget()
        self.basic_tab_stack.addWidget(self.create_basic_record_tab())  # Index 0
        self.basic_tab_stack.addWidget(self.create_basic_upload_tab())  # Index 1
        self.basic_tab_stack.addWidget(self.create_basic_transcript_tab())  # Index 2
        self.basic_tab_stack.addWidget(self.create_settings_tab())  # Index 3 (Settings)
        main_layout.addWidget(self.basic_tab_stack, 1)

        # Right side - vertical tab bar
        self.tab_bar = self.create_vertical_tab_bar()
        main_layout.addWidget(self.tab_bar)

        return container
    def create_settings_tab(self):
        """Create the new Settings tab with all sidebar widgets/settings."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Quick actions
        quick_actions_label = QLabel(self.tr("Quick Actions"))
        quick_actions_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {Theme.get('text_primary', self.is_dark_mode)};
        """)

        def style_settings_btn(btn):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Theme.get('text_primary', self.is_dark_mode)};
                    border: 2px solid {Theme.get('border', self.is_dark_mode)};
                    border-radius: 12px;
                    padding: 10px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                    border-color: {Theme.get('accent', self.is_dark_mode)};
                }}
            """)

        quick_actions_row = QHBoxLayout()
        new_trans_btn = ModernButton(self.tr("New Transcription"))
        set_icon(new_trans_btn, 'file')
        new_trans_btn.clicked.connect(self.clear_for_new_transcription)
        style_settings_btn(new_trans_btn)
        quick_actions_row.addWidget(new_trans_btn)
        change_folder_btn = ModernButton(self.tr("Change Folder"))
        set_icon(change_folder_btn, 'folder')
        change_folder_btn.clicked.connect(self.change_recordings_directory)
        style_settings_btn(change_folder_btn)
        quick_actions_row.addWidget(change_folder_btn)
        open_folder_btn = ModernButton(self.tr("Open Folder"))
        set_icon(open_folder_btn, 'folder-open')
        open_folder_btn.clicked.connect(self.open_recordings_folder)
        style_settings_btn(open_folder_btn)
        quick_actions_row.addWidget(open_folder_btn)
        layout.addLayout(quick_actions_row)

        # Recordings directory card
        layout.addWidget(self.create_settings_card())

        # Settings sections (Audio, Transcription, Activation) - all in one row
        settings_sections_label = QLabel(self.tr("Settings"))
        settings_sections_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {Theme.get('text_primary', self.is_dark_mode)};
        """)
        layout.addWidget(settings_sections_label)

        # Create horizontal layout for all settings buttons
        settings_buttons_row = QHBoxLayout()
        settings_buttons_row.setSpacing(15)
        
        # Extract and add Audio button (Enhance Audio)
        audio_buttons = self.audio_options_widget.findChildren(QPushButton)
        if audio_buttons:
            self.audio_filter_btn = audio_buttons[0]  # Store reference for icon updates
            style_settings_btn(self.audio_filter_btn)
            # Set consistent sizing - must be after stylesheet to override any CSS
            self.audio_filter_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.audio_filter_btn.setMinimumSize(180, 50)
            self.audio_filter_btn.setMaximumSize(180, 50)
            self.audio_filter_btn.setFixedSize(180, 50)
            self.audio_filter_btn.setMinimumHeight(50)
            self.audio_filter_btn.setMaximumHeight(50)
            # Ensure icon shows correct initial state
            checkmark_icon = "check-circle" if self.enable_audio_filters else "square"
            self.audio_filter_btn.setIcon(get_icon(checkmark_icon))
            settings_buttons_row.addWidget(self.audio_filter_btn)
        
        # Extract and add Transcription button (Deep Scan)
        transcription_buttons = self.transcription_options_widget.findChildren(QPushButton)
        if transcription_buttons:
            self.deep_scan_btn = transcription_buttons[0]  # Store reference for icon updates
            style_settings_btn(self.deep_scan_btn)
            # Set consistent sizing - must be after stylesheet to override any CSS
            self.deep_scan_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.deep_scan_btn.setMinimumSize(180, 50)
            self.deep_scan_btn.setMaximumSize(180, 50)
            self.deep_scan_btn.setFixedSize(180, 50)
            self.deep_scan_btn.setMinimumHeight(50)
            self.deep_scan_btn.setMaximumHeight(50)
            # Ensure icon shows correct initial state
            checkmark_icon = "check-circle" if self.enable_deep_scan else "square"
            self.deep_scan_btn.setIcon(get_icon(checkmark_icon))
            settings_buttons_row.addWidget(self.deep_scan_btn)
        
        # Add Activation button
        self.activate_btn = ModernButton(self.tr("Activate"))
        set_icon(self.activate_btn, 'award')
        self.activate_btn.clicked.connect(self.show_activation_dialog)
        style_settings_btn(self.activate_btn)
        # Override ModernButton's default minimum height and set consistent sizing - must be after stylesheet
        self.activate_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.activate_btn.setMinimumSize(180, 50)
        self.activate_btn.setMaximumSize(180, 50)
        self.activate_btn.setFixedSize(180, 50)
        self.activate_btn.setMinimumHeight(50)
        self.activate_btn.setMaximumHeight(50)
        settings_buttons_row.addWidget(self.activate_btn)
        
        # Add stretch to push buttons to the left
        settings_buttons_row.addStretch()

        layout.addLayout(settings_buttons_row)

        # Logs section
        logs_section_label = QLabel(self.tr("Logs"))
        logs_section_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {Theme.get('text_primary', self.is_dark_mode)};
            margin-top: 20px;
        """)
        layout.addWidget(logs_section_label)

        # View Logs button
        view_logs_btn = ModernButton(self.tr("View Logs"))
        set_icon(view_logs_btn, 'file-text')
        view_logs_btn.clicked.connect(self.show_logs_dialog)
        style_settings_btn(view_logs_btn)
        view_logs_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        view_logs_btn.setMinimumSize(180, 50)
        view_logs_btn.setMaximumSize(180, 50)
        view_logs_btn.setFixedSize(180, 50)
        view_logs_btn.setMinimumHeight(50)
        view_logs_btn.setMaximumHeight(50)
        
        logs_btn_layout = QHBoxLayout()
        logs_btn_layout.addWidget(view_logs_btn)
        logs_btn_layout.addStretch()
        layout.addLayout(logs_btn_layout)

        layout.addStretch()
        return widget

    def _add_settings_to_sidebar(self, sidebar):
        """Add settings sections to the left sidebar."""
        from PySide6.QtWidgets import QPushButton

        # Settings section header (clickable to expand/collapse)
        self.settings_section_expanded = True
        self.settings_section_btn = QPushButton(self.tr("▼ Settings"))
        self.settings_section_btn.setIcon(get_icon('settings'))
        self.settings_section_btn.setCursor(Qt.PointingHandCursor)
        self.settings_section_btn.setMinimumHeight(40)
        self.settings_section_btn.clicked.connect(self.toggle_settings_section)
        self.settings_section_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.get('text_primary', self.is_dark_mode)};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
        """)
        sidebar.content_layout.insertWidget(sidebar.content_layout.count() - 1, self.settings_section_btn)

        # Settings content container
        self.settings_content_widget = QWidget()
        settings_content_layout = QVBoxLayout(self.settings_content_widget)
        settings_content_layout.setContentsMargins(0, 0, 0, 0)
        settings_content_layout.setSpacing(2)

        # Audio Processing section (nested under Settings)
        self.audio_section_expanded = True
        self.audio_section_btn = QPushButton(self.tr("  ▼ Audio Processing"))
        self.audio_section_btn.setIcon(get_icon('mic'))
        self.audio_section_btn.setCursor(Qt.PointingHandCursor)
        self.audio_section_btn.setMinimumHeight(36)
        self.audio_section_btn.clicked.connect(self.toggle_audio_section)
        self.audio_section_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.get('text_secondary', self.is_dark_mode)};
                border: none;
                border-radius: 6px;
                padding: 6px 12px 6px 16px;
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
        """)
        settings_content_layout.addWidget(self.audio_section_btn)

        # Audio options container
        self.audio_options_widget = QWidget()
        audio_options_layout = QVBoxLayout(self.audio_options_widget)
        audio_options_layout.setContentsMargins(0, 0, 0, 0)
        audio_options_layout.setSpacing(2)

        # Audio filters toggle
        audio_filter_btn = self.create_toggle_option_btn(
            "sliders", "Enhance Audio",
            self.enable_audio_filters,
            self.toggle_audio_filters,
            indent=32
        )
        audio_filter_btn.setToolTip("Removes noise, boosts clarity")
        audio_options_layout.addWidget(audio_filter_btn)

        settings_content_layout.addWidget(self.audio_options_widget)

        # Add spacing
        settings_content_layout.addSpacing(8)

        # Transcription section (nested under Settings)
        self.transcription_section_expanded = True
        self.transcription_section_btn = QPushButton(self.tr("  ▼ Transcription"))
        self.transcription_section_btn.setIcon(get_icon('file-text'))
        self.transcription_section_btn.setCursor(Qt.PointingHandCursor)
        self.transcription_section_btn.setMinimumHeight(36)
        self.transcription_section_btn.clicked.connect(self.toggle_transcription_section)
        self.transcription_section_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.get('text_secondary', self.is_dark_mode)};
                border: none;
                border-radius: 6px;
                padding: 6px 12px 6px 16px;
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
        """)
        settings_content_layout.addWidget(self.transcription_section_btn)

        # Transcription options container
        self.transcription_options_widget = QWidget()
        transcription_options_layout = QVBoxLayout(self.transcription_options_widget)
        transcription_options_layout.setContentsMargins(0, 0, 0, 0)
        transcription_options_layout.setSpacing(2)

        # Deep scan toggle
        deep_scan_btn = self.create_toggle_option_btn(
            "search", "Deep Scan",
            self.enable_deep_scan,
            self.toggle_deep_scan,
            indent=32
        )
        deep_scan_btn.setToolTip("Segments audio into chunks for accurate multi-language detection (slower but more accurate)")
        transcription_options_layout.addWidget(deep_scan_btn)

        settings_content_layout.addWidget(self.transcription_options_widget)

        sidebar.content_layout.insertWidget(sidebar.content_layout.count() - 1, self.settings_content_widget)

    def create_vertical_tab_bar(self):
        """Create vertical tab bar on the right side, now with Settings tab."""
        from PySide6.QtWidgets import QPushButton

        tab_bar = QWidget()
        tab_bar.setMinimumWidth(260)  # Increased to accommodate button width + margins
        tab_bar.setMaximumWidth(260)

        layout = QVBoxLayout(tab_bar)
        layout.setContentsMargins(10, 20, 20, 20)  # Increased right margin for buffer from edge
        layout.setSpacing(10)

        # Store current tab index
        self.current_tab_index = 0
        self.tab_buttons = []

        # Create tab buttons
        tabs = [
            ("mic", self.tr("Record"), 0),
            ("folder", self.tr("Upload"), 1),
            ("file", self.tr("Transcript"), 2),
            ("settings", self.tr("Settings"), 3)
        ]

        for icon_name, label, index in tabs:
            btn = QPushButton(self.tr(label))
            set_icon(btn, icon_name, size=32)  # Larger icons for tab bar
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(220)  # Double width for tab buttons
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("tab_index", index)
            btn.clicked.connect(lambda checked=False, idx=index: self.on_tab_changed(idx))

            self.tab_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Apply theme
        self.update_vertical_tab_styles()

        return tab_bar

    def update_vertical_tab_styles(self):
        """Update styling for vertical tab buttons (delegated to ThemeManager)."""
        self.theme_manager.update_vertical_tab_styles()

    def on_tab_changed(self, index):
        """Handle tab switching."""
        # Update current tab index
        self.current_tab_index = index

        # Update tab button styles
        self.update_vertical_tab_styles()

        # Switch content
        self.basic_tab_stack.setCurrentIndex(index)
        logger.info(f"Switched to tab index {index}")

    def toggle_settings_section(self):
        """Toggle settings section visibility."""
        self.settings_section_expanded = not self.settings_section_expanded

        if self.settings_section_expanded:
            self.settings_section_btn.setText(self.tr("▼ Settings"))
            self.settings_section_btn.setIcon(get_icon('settings'))
            self.settings_content_widget.show()
        else:
            self.settings_section_btn.setText(self.tr("▶ Settings"))
            self.settings_section_btn.setIcon(get_icon('settings'))
            self.settings_content_widget.hide()

        logger.info(f"Settings section {'expanded' if self.settings_section_expanded else 'collapsed'}")

    def toggle_audio_section(self):
        """Toggle audio processing section visibility."""
        self.audio_section_expanded = not self.audio_section_expanded

        if self.audio_section_expanded:
            self.audio_options_widget.show()
        else:
            self.audio_options_widget.hide()

        logger.info(f"Audio section {'expanded' if self.audio_section_expanded else 'collapsed'}")

    def toggle_transcription_section(self):
        """Toggle transcription section visibility."""
        self.transcription_section_expanded = not self.transcription_section_expanded

        if self.transcription_section_expanded:
            self.transcription_options_widget.show()
        else:
            self.transcription_options_widget.hide()

        logger.info(f"Transcription section {'expanded' if self.transcription_section_expanded else 'collapsed'}")

    def create_toggle_option_btn(self, icon, label, is_enabled, callback, indent=24):
        """Create a toggle option button with checkmark indicator."""
        from PySide6.QtWidgets import QPushButton
        checkmark_icon = "check-circle" if is_enabled else "square"
        translated_label = self.tr(label)
        btn = QPushButton(f"  {translated_label}")
        btn.setIcon(get_icon(checkmark_icon))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(36)
        btn.setProperty("callback", callback)  # Store callback
        btn.setProperty("icon", icon)  # Store icon name
        btn.setProperty("label", label)  # Store label
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                color: {Theme.get('text_primary', self.is_dark_mode)};
                border: 2px solid {Theme.get('border', self.is_dark_mode)};
                border-radius: 12px;
                padding: 15px 10px 15px {indent}px;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('accent', self.is_dark_mode)};
                color: white;
                border-color: {Theme.get('accent', self.is_dark_mode)};
            }}
        """)
        return btn

    def toggle_audio_filters(self):
        """Toggle audio filters on/off."""
        self.enable_audio_filters = not self.enable_audio_filters
        self.save_settings()

        # Update button visual - use stored reference if available
        checkmark_icon = "check-circle" if self.enable_audio_filters else "square"
        if hasattr(self, 'audio_filter_btn') and self.audio_filter_btn:
            label = self.audio_filter_btn.property("label") or "Enhance Audio"
            self.audio_filter_btn.setText(f"  {self.tr(label)}")
            self.audio_filter_btn.setIcon(get_icon(checkmark_icon))
        else:
            # Fallback to widget search if button not stored
            for child in self.audio_options_widget.findChildren(QPushButton):
                if "Enhance Audio" in child.text():
                    label = child.property("label") or "Enhance Audio"
                    child.setText(f"  {self.tr(label)}")
                    child.setIcon(get_icon(checkmark_icon))
                    break

        logger.info(f"Audio filters {'enabled' if self.enable_audio_filters else 'disabled'}")

    def toggle_deep_scan(self):
        """Toggle deep scan on/off."""
        self.enable_deep_scan = not self.enable_deep_scan
        self.save_settings()

        # Update button visual - use stored reference if available
        checkmark_icon = "check-circle" if self.enable_deep_scan else "square"
        if hasattr(self, 'deep_scan_btn') and self.deep_scan_btn:
            label = self.deep_scan_btn.property("label") or "Deep Scan"
            self.deep_scan_btn.setText(f"  {self.tr(label)}")
            self.deep_scan_btn.setIcon(get_icon(checkmark_icon))
        else:
            # Fallback to widget search if button not stored
            for child in self.transcription_options_widget.findChildren(QPushButton):
                if "Deep Scan" in child.text():
                    label = child.property("label") or "Deep Scan"
                    child.setText(f"  {self.tr(label)}")
                    child.setIcon(get_icon(checkmark_icon))
                    break

        logger.info(f"Deep scan {'enabled' if self.enable_deep_scan else 'disabled'}")

    def create_sidebar(self):
        """Create sidebar navigation widget."""
        sidebar = QListWidget()
        sidebar.setMaximumWidth(180)
        sidebar.setMinimumWidth(180)
        sidebar.setSpacing(5)
        sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.get('bg_secondary', self.is_dark_mode)};
                border: none;
                border-right: 1px solid {Theme.get('border', self.is_dark_mode)};
                padding: 10px;
                outline: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                color: {Theme.get('text_primary', self.is_dark_mode)};
                border-radius: 8px;
                padding: 12px 15px;
                margin: 2px 0px;
                font-size: 14px;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.get('accent', self.is_dark_mode)};
                color: white;
            }}
        """)

        # Add tab items - order: Record, Upload, Transcript
        from PySide6.QtCore import QSize
        record_item = QListWidgetItem(get_icon('mic'), "Record")
        upload_item = QListWidgetItem(get_icon('folder'), "Upload")
        transcript_item = QListWidgetItem(get_icon('file'), "Transcript")

        sidebar.addItem(record_item)  # Index 0
        sidebar.addItem(upload_item)  # Index 1
        sidebar.addItem(transcript_item)  # Index 2

        # Set first item as selected
        sidebar.setCurrentRow(0)

        return sidebar

    def create_basic_upload_tab(self):
        """Create Upload tab for Basic mode."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Drop zone
        self.drop_zone = DropZone(self.is_dark_mode)
        self.drop_zone.file_dropped.connect(self.on_file_dropped_basic)
        self.drop_zone.clicked.connect(self.browse_file)
        layout.addWidget(self.drop_zone)

        # Progress section
        self.basic_upload_progress_label = QLabel(self.tr("Ready to transcribe"))
        self.basic_upload_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_upload_progress_label)

        self.basic_upload_progress_bar = QProgressBar()
        self.basic_upload_progress_bar.setMinimumHeight(25)
        self.basic_upload_progress_bar.hide()  # Hide until processing starts
        layout.addWidget(self.basic_upload_progress_bar)

        # Info tip
        info = QLabel(self.tr("ℹ️ Files automatically transcribe when dropped or selected"))
        info.setStyleSheet(f"font-size: 12px; color: {Theme.get('info', self.is_dark_mode)};")
        layout.addWidget(info)



        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_basic_record_tab(self):
        """Create Record tab for Basic mode."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Simplified UI: No device selection, just a record button.
        # The worker will use the system's default devices.
        info_label = QLabel(self.tr("Recording will use the system's default microphone and audio output."))
        info_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # VU Meters (horizontal, stacked vertically)
        vu_container = QWidget()
        vu_layout = QVBoxLayout(vu_container)
        vu_layout.setSpacing(10)
        vu_layout.setContentsMargins(20, 10, 20, 10)

        self.mic_vu_meter = VUMeter(label=self.tr("Microphone"))
        self.speaker_vu_meter = VUMeter(label=self.tr("Speaker"))
        vu_layout.addWidget(self.mic_vu_meter)
        vu_layout.addWidget(self.speaker_vu_meter)

        layout.addWidget(vu_container)
        layout.addSpacing(10)

        # Record toggle button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignCenter)

        self.basic_record_btn = ModernButton(self.tr("Start Recording"), primary=True)
        self.basic_record_btn.setMinimumHeight(50)
        self.basic_record_btn.setMinimumWidth(220)
        self.basic_record_btn.clicked.connect(self.toggle_basic_recording)
        button_layout.addWidget(self.basic_record_btn)

        layout.addWidget(button_container)
        layout.addSpacing(10)

        # Recording timer (HH:MM:SS format only, no "Duration:" label)
        self.recording_time_label = QLabel(self.tr("00:00:00"))
        self.recording_time_label.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {Theme.get('error', self.is_dark_mode)};"
        )
        self.recording_time_label.setAlignment(Qt.AlignCenter)
        self.recording_time_label.hide()
        layout.addWidget(self.recording_time_label)

        layout.addStretch(1)

        # Progress section
        self.basic_record_progress_label = QLabel(self.tr("Ready to record"))
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_record_progress_label)

        self.basic_record_progress_bar = QProgressBar()
        self.basic_record_progress_bar.setMinimumHeight(25)
        self.basic_record_progress_bar.hide()  # Hide until processing starts
        layout.addWidget(self.basic_record_progress_bar)

        # Info tip
        info = QLabel(self.tr("ℹ️ After stopping, the recording is saved but NOT automatically transcribed\nℹ️ Click 'Transcribe Recording' to manually start transcription"))
        info.setStyleSheet(f"font-size: 12px; color: {Theme.get('info', self.is_dark_mode)};")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Manual transcription button (appears after a recording completes)
        self.transcribe_recording_btn = ModernButton(self.tr("Transcribe Recording"), primary=True)
        self.transcribe_recording_btn.setMinimumHeight(42)
        self.transcribe_recording_btn.hide()
        def _start_transcribe_recording():
            if not self.video_path:
                QMessageBox.information(self, self.tr("No Recording"), self.tr("No recording available. Please record first."))
                return
            # Reset multi-language choice so dialog appears for each manual transcription
            self.multi_language_mode = None
            self.prompt_multi_language_and_transcribe(from_start=True)
        self.transcribe_recording_btn.clicked.connect(_start_transcribe_recording)
        layout.addWidget(self.transcribe_recording_btn)



        layout.addStretch(2)
        widget.setLayout(layout)
        return widget

    def create_basic_transcript_tab(self):
        """Create Transcript tab for Basic mode."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Language info (shown after transcription)
        self.basic_transcript_desc = QLabel("")
        self.basic_transcript_desc.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_transcript_desc)

        # Multi-language mode now chosen via dialog only; checkbox removed.

        # Result text
        self.basic_result_text = QTextEdit()
        self.basic_result_text.setPlaceholderText(self.tr("Transcription text will appear here..."))
        self.basic_result_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.get('input_bg', self.is_dark_mode)};
                color: {Theme.get('text_primary', self.is_dark_mode)};
                border: 1px solid {Theme.get('border', self.is_dark_mode)};
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.6;
            }}
        """)
        layout.addWidget(self.basic_result_text, 1)

        # Save button
        self.basic_save_btn = ModernButton(self.tr("Save Transcription"), primary=True)
        set_icon(self.basic_save_btn, 'save')
        self.basic_save_btn.setEnabled(False)
        self.basic_save_btn.clicked.connect(self.save_transcription)
        layout.addWidget(self.basic_save_btn)

        # Cancel transcription button (shown only while active)
        self.cancel_transcription_btn = ModernButton(self.tr("Cancel Transcription"))
        set_icon(self.cancel_transcription_btn, 'x-circle')
        self.cancel_transcription_btn.setEnabled(False)
        self.cancel_transcription_btn.hide()
        self.cancel_transcription_btn.clicked.connect(self.cancel_transcription)
        layout.addWidget(self.cancel_transcription_btn)

        widget.setLayout(layout)
        return widget

    def on_file_dropped_basic(self, file_path):
        """Handle file drop - auto-start transcription (delegated to FileManager)."""
        self.file_manager.on_file_dropped(file_path, self.prompt_multi_language_and_transcribe)

    def browse_file(self):
        """Browse for video/audio file (delegated to FileManager)."""
        self.file_manager.browse_file(self.prompt_multi_language_and_transcribe)

    def load_file(self, file_path):
        """Load a video or audio file (delegated to FileManager)."""
        self.file_manager.load_file(file_path)

    def refresh_audio_devices(self):
        """No-op. Device selection removed."""
        pass

    def on_mic_device_changed(self, index):
        """No-op. Device selection removed."""
        pass

    def on_speaker_device_changed(self, index):
        """No-op. Device selection removed."""
        pass

    def show_audio_setup_guide(self):
        """Show platform-specific audio setup guide."""
        current_platform = get_platform()
        platform_help = get_platform_audio_setup_help()

        platform_names = {
            'macos': 'macOS',
            'windows': 'Windows',
            'linux': 'Linux'
        }

        platform_display = platform_names.get(current_platform, current_platform.upper())

        # Build help message
        help_text = f"# Audio Setup Guide for {platform_display}\n\n"

        # Microphone permissions
        help_text += "## Microphone Setup\n\n"
        help_text += "\n".join(platform_help.get('permissions', []))
        help_text += "\n\n"

        # System audio setup
        help_text += "## System Audio / YouTube Capture Setup\n\n"
        help_text += "\n".join(platform_help.get('loopback_install', []))

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Audio Setup Guide - {platform_display}")
        dialog.setMinimumSize(650, 500)

        layout = QVBoxLayout()

        # Title
        title = QLabel(self.tr(f"Audio Setup Guide for {platform_display}"))
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Help text
        help_display = QTextEdit()
        help_display.setPlainText(help_text)
        help_display.setReadOnly(True)
        help_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(help_display)

        # Close button
        close_btn = ModernButton(self.tr("Close"), primary=True)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()


    def retranslate_ui(self):
        # Update Microphone and Speaker labels
        if hasattr(self, 'mic_vu_meter') and hasattr(self.mic_vu_meter, 'label'):
            self.mic_vu_meter.label.setText(self.tr("Microphone"))
        if hasattr(self, 'speaker_vu_meter') and hasattr(self.speaker_vu_meter, 'label'):
            self.speaker_vu_meter.label.setText(self.tr("Speaker"))
        # Update Enhance Audio toggle
        if hasattr(self, 'audio_options_widget'):
            for child in self.audio_options_widget.findChildren(QPushButton):
                if "Enhance Audio" in child.text():
                    label = self.tr("Enhance Audio")
                    checkmark_icon = "check-circle" if self.enable_audio_filters else "square"
                    child.setText(f"  {label}")
                    child.setIcon(get_icon(checkmark_icon))
        # Update Deep Scan toggle
        if hasattr(self, 'transcription_options_widget'):
            for child in self.transcription_options_widget.findChildren(QPushButton):
                if "Deep Scan" in child.text():
                    label = self.tr("Deep Scan")
                    checkmark_icon = "check-circle" if self.enable_deep_scan else "square"
                    child.setText(f"  {label}")
                    child.setIcon(get_icon(checkmark_icon))
        # Update info label in record tab
        if hasattr(self, 'info_label'):
            self.info_label.setText(self.tr("Recording will use the system's default microphone and audio output."))
        # Update info label in record tab (after stopping)
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(self.tr("Ready to record"))
        # Update info label in record tab (after stopping)
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(self.tr("Ready to transcribe"))
        # Update after stopping info
        if hasattr(self, 'drop_zone') and hasattr(self.drop_zone, 'text_label'):
            self.drop_zone.text_label.setText(self.tr("Drag and drop video/audio file"))
        # Update after stopping info (manual transcription)
        if hasattr(self, 'transcribe_recording_btn'):
            self.transcribe_recording_btn.set_label(self.tr("Transcribe Recording"))
        # Update info tip in record tab
        if hasattr(self, 'basic_result_text'):
            self.basic_result_text.setPlaceholderText(self.tr("Transcription text will appear here..."))
        """Retranslate all UI elements after installing a translator."""
        # Record button
        if hasattr(self, 'basic_record_btn'):
            self.basic_record_btn.set_label(self.tr("Start Recording"))
        # Recording time label
        if hasattr(self, 'recording_time_label'):
            self.recording_time_label.setText(self.tr("00:00:00"))
        # Window title
        self.setWindowTitle(self.tr("FonixFlow - Whisper Transcription"))
        # Status bar
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage(self.tr("Ready"))
        # Main tab bar (vertical tab buttons)
        if hasattr(self, 'tab_buttons'):
            tab_labels = [self.tr("Record"), self.tr("Upload"), self.tr("Transcript"), self.tr("Settings")]
            tab_icons = ["mic", "folder", "file", "settings"]
            for i, btn in enumerate(self.tab_buttons):
                btn.setText(tab_labels[i])
                set_icon(btn, tab_icons[i], size=32)
        # Sidebar
        if hasattr(self, 'collapsible_sidebar'):
            self.collapsible_sidebar.update_action_label("New Transcription", self.tr("New Transcription"))
            self.collapsible_sidebar.update_action_label("Change Folder", self.tr("Change Folder"))
            self.collapsible_sidebar.update_action_label("Open Folder", self.tr("Open Folder"))
        # Settings section
        if hasattr(self, 'settings_section_btn'):
            self.settings_section_btn.setText(self.tr("▼ Settings"))
            self.settings_section_btn.setIcon(get_icon('settings'))
        # Audio section
        if hasattr(self, 'audio_section_btn'):
            self.audio_section_btn.setText(self.tr("  ▼ Audio Processing"))
            self.audio_section_btn.setIcon(get_icon('mic'))
        # Transcription section
        if hasattr(self, 'transcription_section_btn'):
            self.transcription_section_btn.setText(self.tr("  ▼ Transcription"))
            self.transcription_section_btn.setIcon(get_icon('file-text'))
        # Drop zone
        if hasattr(self, 'drop_zone'):
            self.drop_zone.setText(self.tr("Drag and drop video/audio file"))
        # Progress labels
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(self.tr("Ready to transcribe"))
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(self.tr("Ready to record"))
        # Recording labels
        if hasattr(self, 'mic_vu_meter'):
            self.mic_vu_meter.label.setText(self.tr("Microphone"))
        if hasattr(self, 'speaker_vu_meter'):
            self.speaker_vu_meter.label.setText(self.tr("Speaker"))
        # Directory label
        if hasattr(self, 'recordings_dir_display'):
            self.recordings_dir_display.setText(self.settings["recordings_dir"])
        # Change folder button
        if hasattr(self, 'change_dir_btn'):
            self.change_dir_btn.set_label(self.tr("Change Folder"))
            self.change_dir_btn.setIcon(get_icon('folder'))
        # Open folder button
        if hasattr(self, 'open_folder_btn'):
            self.open_folder_btn.set_label(self.tr("Open Folder"))
            self.open_folder_btn.setIcon(get_icon('folder-open'))
        # Info labels
        if hasattr(self, 'info_label'):
            self.info_label.setText(self.tr("Recording will use the system's default microphone and audio output."))
        # Add more widget retranslation logic here as needed
        # Add more widget retranslation logic here as needed


        self.start_audio_preview()

    # ---------- Tab activation management ----------
    def on_basic_tab_changed(self, index: int):
        """Handle sidebar tab changes."""
        try:
            # Switch stacked widget
            if hasattr(self, 'basic_tab_stack'):
                self.basic_tab_stack.setCurrentIndex(index)
        except Exception as e:
            logger.warning(f"Could not switch tab index: {e}")

        # If recording is ongoing and user navigates away, stop recording gracefully
        if index != 0 and getattr(self, 'is_recording', False):
            logger.info("Leaving Record tab while recording; stopping recording")
            try:
                self.stop_basic_recording()
            except Exception as e:
                logger.warning(f"Failed to stop recording on tab change: {e}")
        # Update status bar
        try:
            tab_names = {0: self.tr("Record"), 1: self.tr("Upload"), 2: self.tr("Transcript")}
            self.statusBar().showMessage(self.tr(f"Switched to {tab_names.get(index, self.tr('Unknown'))} tab"))
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")

    # Override refresh_audio_devices to avoid auto preview start when not on Record tab
    def refresh_audio_devices(self):
        """No-op. Device selection removed."""
        pass