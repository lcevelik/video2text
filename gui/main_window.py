"""
Main window for the FonixFlow Qt GUI.
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
    QComboBox, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QEvent  # type: ignore
from PySide6.QtGui import QPalette  # type: ignore

from gui.theme import Theme
from gui.widgets import ModernButton, Card, DropZone
from gui.workers import RecordingWorker, TranscriptionWorker
from gui.dialogs import MultiLanguageChoiceDialog, RecordingDialog
from gui.utils import check_audio_input_devices, get_platform, get_platform_audio_setup_help
from transcriber import Transcriber

logger = logging.getLogger(__name__)

class FonixFlowQt(QMainWindow):
    """Modern Qt-based main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FonixFlow - Whisper Transcription")
        self.setMinimumSize(1000, 700)

        # Config file location
        self.config_file = Path.home() / ".fonixflow_config.json"

        # Load settings
        self.settings = self.load_settings()

        # State
        self.video_path = None
        self.transcription_result = None
        self.transcription_worker = None  # QThread worker for transcription
        self.theme_mode = self.settings.get("theme_mode", "auto")  # auto, light, dark
        self.is_dark_mode = self.get_effective_theme()

        self.transcription_start_time = None
        self.performance_overlay = None

        self.setup_ui()
        self.apply_theme()
        # Ensure ffmpeg is available to pydub across the app
        try:
            self._configure_ffmpeg_converter()
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

    # Early stub to guarantee existence even if later method definition changes order
    def cancel_transcription(self):
        """Cancel active transcription if running (early stub)."""
        if getattr(self, 'transcription_worker', None):
            try:
                self.transcription_worker.cancel()
            except Exception as e:
                logger.warning(f"Cancel request failed: {e}")
        if hasattr(self, 'cancel_transcription_btn'):
            try:
                self.cancel_transcription_btn.setEnabled(False)
            except Exception:
                pass
        try:
            self.statusBar().showMessage("Cancel requested…")
        except Exception:
            pass

    def center_window(self):
        """Center the main window on the primary screen."""
        try:
            frame_geom = self.frameGeometry()
            screen_center = QApplication.primaryScreen().availableGeometry().center()
            frame_geom.moveCenter(screen_center)
            self.move(frame_geom.topLeft())
        except Exception as e:
            logger.warning(f"Could not center window: {e}")

    def load_settings(self):
        """Load settings from config file."""
        default_settings = {
            "recordings_dir": str(Path.home() / "FonixFlow" / "Recordings"),
            "theme_mode": "auto"  # auto, light, dark
        }

        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    # Migrate old dark_mode setting to theme_mode
                    if "dark_mode" in settings and "theme_mode" not in settings:
                        settings["theme_mode"] = "dark" if settings["dark_mode"] else "light"
                        del settings["dark_mode"]
                    # Merge with defaults for any missing keys
                    return {**default_settings, **settings}
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")

        return default_settings

    def save_settings(self):
        """Save settings to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Settings saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Could not save settings: {e}")

    def check_runtime_compat(self):
        """Warn users on Python 3.13 if pyaudioop is missing (needed for recording)."""

    def detect_system_theme(self):
        """Detect if system is in dark mode."""
        try:
            # Use Qt's palette to detect system theme
            palette = QApplication.palette()
            # Updated for PySide6: use QPalette.ColorRole.Window instead of deprecated attribute
            bg_color = palette.color(QPalette.ColorRole.Window)
            # If background is dark (luminance < 128), system is in dark mode
            is_dark = bg_color.lightness() < 128
            return is_dark
        except Exception as e:
            logger.warning(f"Could not detect system theme: {e}")
            return False  # Default to light

    def get_effective_theme(self):
        """Get the effective theme based on mode setting."""
        if self.theme_mode == "auto":
            return self.detect_system_theme()
        elif self.theme_mode == "dark":
            return True
        else:  # light
            return False

    def apply_theme(self):
        """Apply the current theme to all UI elements."""
        # Get theme colors
        bg = Theme.get('bg_primary', self.is_dark_mode)
        text = Theme.get('text_primary', self.is_dark_mode)
        border = Theme.get('border', self.is_dark_mode)
        accent = Theme.get('accent', self.is_dark_mode)

        # Main window stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg};
                color: {text};
            }}
            QWidget {{
                background-color: {bg};
                color: {text};
            }}
            QLabel {{
                color: {text};
            }}
            QPushButton {{
                background-color: {Theme.get('button_bg', self.is_dark_mode)};
                color: {Theme.get('button_text', self.is_dark_mode)};
                border: 2px solid {border};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {accent};
                background-color: {Theme.get('bg_secondary', self.is_dark_mode)};
            }}
            QTextEdit {{
                background-color: {Theme.get('input_bg', self.is_dark_mode)};
                color: {text};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QProgressBar {{
                border: 2px solid {border};
                border-radius: 8px;
                text-align: center;
                background-color: {Theme.get('bg_secondary', self.is_dark_mode)};
                color: {text};
            }}
            QProgressBar::chunk {{
                background-color: {accent};
                border-radius: 6px;
            }}
            QComboBox {{
                background-color: {Theme.get('input_bg', self.is_dark_mode)};
                color: {text};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 5px;
            }}
            QRadioButton {{
                color: {text};
            }}
        """)

        # Update sidebar if it exists
        if hasattr(self, 'basic_sidebar'):
            self.update_sidebar_theme(self.basic_sidebar)

        # Update DropZone theme
        if hasattr(self, 'drop_zone'):
            self.drop_zone.set_theme(self.is_dark_mode)

        # Update all Card widgets
        self.update_all_cards_theme()

        logger.info(f"Applied {'dark' if self.is_dark_mode else 'light'} theme")

    def closeEvent(self, event):
        """Ensure background threads stop cleanly on window close."""
        try:
            # Stop recording worker if running
            if hasattr(self, 'recording_worker') and self.recording_worker and self.recording_worker.isRunning():
                try:
                    self.recording_worker.stop()
                except Exception:
                    pass
                self.recording_worker.wait(1500)
                self.recording_worker = None
        except Exception as e:
            logger.warning(f"Error while shutting down workers: {e}")
        super().closeEvent(event)

    def _configure_ffmpeg_converter(self):
        """Configure pydub to use an available ffmpeg binary without requiring shell restart."""
        try:
            import shutil as _shutil
            from pathlib import Path as _Path
            from pydub import AudioSegment  # type: ignore
        except Exception:
            return

        # If ffmpeg is on PATH, set converter and return
        if _shutil.which('ffmpeg'):
            try:
                AudioSegment.converter = 'ffmpeg'
                logger.info("pydub configured to use ffmpeg from PATH")
            except Exception:
                pass
            return

        # Try common install locations, including winget default cache
        candidates = [
            r"C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            r"C:\\Program Files\\FFmpeg\\bin\\ffmpeg.exe",
            str(_Path.home() / "scoop" / "apps" / "ffmpeg" / "current" / "bin" / "ffmpeg.exe"),
            str(_Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "WinGet" / "Packages" / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe" / "ffmpeg-8.0-full_build" / "bin" / "ffmpeg.exe"),
        ]
        for p in candidates:
            try:
                if _Path(p).exists():
                    try:
                        AudioSegment.converter = p
                        logger.info(f"pydub configured to use ffmpeg at: {p}")
                    except Exception:
                        os.environ['FFMPEG_BINARY'] = p
                        logger.info(f"Set FFMPEG_BINARY for pydub: {p}")
                    break
            except Exception:
                continue

    def update_all_cards_theme(self):
        """Update theme for all Card widgets."""
        for widget in self.findChildren(Card):
            widget.update_theme(self.is_dark_mode)

    def eventFilter(self, obj, event):
        """No-op, was for device refresh."""
        return super().eventFilter(obj, event)

    def changeEvent(self, event):
        """No-op, was for device refresh."""
        return super().changeEvent(event)

    def update_sidebar_theme(self, sidebar):
        """Update sidebar theme colors."""
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

    def setup_ui(self):
        """Setup the main UI."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Main content - just the basic mode (no mode switching)
        basic_mode = self.create_basic_mode()
        layout.addWidget(basic_mode, 1)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("background-color: #F5F5F5; color: #666; padding: 5px;")

        central.setLayout(layout)

        # Apply global style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #333;
            }
        """)

    def create_header(self):
        """Create application header with hamburger menu."""
        header = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addStretch()

        # Hamburger menu button
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setMinimumWidth(50)
        self.menu_btn.setMinimumHeight(40)
        self.menu_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 24px;
                border: none;
                background-color: transparent;
                color: {Theme.get('text_primary', self.is_dark_mode)};
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                border-radius: 8px;
            }}
        """)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.clicked.connect(self.show_menu)
        layout.addWidget(self.menu_btn)

        header.setLayout(layout)
        return header

    def show_menu(self):
        """Show hamburger menu with settings."""
        menu = QMenu(self)

        # Settings submenu
        settings_menu = menu.addMenu("⚙️ Settings")

        # Theme submenu under Settings
        theme_menu = settings_menu.addMenu("🎨 Theme")

        # Theme options
        auto_action = theme_menu.addAction("🔄 Auto (System)")
        auto_action.setCheckable(True)
        auto_action.setChecked(self.theme_mode == "auto")
        auto_action.triggered.connect(lambda: self.set_theme_mode("auto"))

        light_action = theme_menu.addAction("☀️ Light")
        light_action.setCheckable(True)
        light_action.setChecked(self.theme_mode == "light")
        light_action.triggered.connect(lambda: self.set_theme_mode("light"))

        dark_action = theme_menu.addAction("🌙 Dark")
        dark_action.setCheckable(True)
        dark_action.setChecked(self.theme_mode == "dark")
        dark_action.triggered.connect(lambda: self.set_theme_mode("dark"))

        # Deep scan toggle (global multi-language chunk reanalysis)
        settings_menu.addSeparator()
        deep_scan_action = settings_menu.addAction("🔍 Enable Deep Scan (Slower)")
        deep_scan_action.setCheckable(True)
        if not hasattr(self, 'enable_deep_scan'):
            self.enable_deep_scan = False
        deep_scan_action.setChecked(self.enable_deep_scan)
        def toggle_deep_scan():
            self.enable_deep_scan = not self.enable_deep_scan
            deep_scan_action.setChecked(self.enable_deep_scan)
            logger.info(f"Deep scan toggled: {self.enable_deep_scan}")
        deep_scan_action.triggered.connect(toggle_deep_scan)

        # Recording Settings under Settings
        settings_menu.addSeparator()
        rec_dir_action = settings_menu.addAction("📁 Change Recording Directory")
        rec_dir_action.triggered.connect(self.change_recordings_directory)

        open_dir_action = settings_menu.addAction("🗂️ Open Recording Directory")
        open_dir_action.triggered.connect(self.open_recordings_folder)

        # New Transcription
        menu.addSeparator()
        new_trans_action = menu.addAction("🔄 New Transcription")
        new_trans_action.triggered.connect(self.clear_for_new_transcription)

        # Show menu at button position
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def set_theme_mode(self, mode):
        """Set theme mode (auto/light/dark)."""
        self.theme_mode = mode
        self.settings["theme_mode"] = mode
        self.save_settings()

        # Update effective theme
        self.is_dark_mode = self.get_effective_theme()
        self.apply_theme()

        logger.info(f"Theme mode set to: {mode} (effective: {'dark' if self.is_dark_mode else 'light'})")

    def create_settings_card(self):
        """Create settings card for recordings directory."""
        card = Card("⚙️ Recordings Settings", self.is_dark_mode)

        # Current directory display
        dir_label = QLabel("Recordings save to:")
        dir_label.setStyleSheet("font-size: 12px; color: #666;")
        card.content_layout.addWidget(dir_label)

        # Create or update the display label (instance variable)
        if not hasattr(self, 'recordings_dir_display'):
            self.recordings_dir_display = QLabel(self.settings["recordings_dir"])
            self.recordings_dir_display.setStyleSheet(
                "font-size: 13px; color: #2196F3; padding: 8px; "
                "background-color: #E3F2FD; border-radius: 4px;"
            )
            self.recordings_dir_display.setWordWrap(True)
        else:
            # Update the text in case it changed
            self.recordings_dir_display.setText(self.settings["recordings_dir"])

        card.content_layout.addWidget(self.recordings_dir_display)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        # Change directory button
        change_dir_btn = ModernButton("📂 Change Folder")
        change_dir_btn.clicked.connect(self.change_recordings_directory)
        btn_row.addWidget(change_dir_btn)

        # Open folder button
        open_folder_btn = ModernButton("🗂️ Open Folder")
        open_folder_btn.clicked.connect(self.open_recordings_folder)
        btn_row.addWidget(open_folder_btn)

        card.content_layout.addLayout(btn_row)

        return card

    def create_basic_mode(self):
        """Create basic mode interface with sidebar navigation."""
        # State for recording
        self.is_recording = False
        self.recording_start_time = None
        self.recording_worker = None  # QThread worker for recording
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_duration)
        self.selected_mic_device = None  # User-selected microphone device
        self.selected_speaker_device = None  # User-selected speaker device

        # Main container
        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.basic_sidebar = self.create_sidebar()
        main_layout.addWidget(self.basic_sidebar)

        # Tab content stack - order: Record, Upload, Transcript
        self.basic_tab_stack = QStackedWidget()
        self.basic_tab_stack.addWidget(self.create_basic_record_tab())  # Index 0
        self.basic_tab_stack.addWidget(self.create_basic_upload_tab())  # Index 1
        self.basic_tab_stack.addWidget(self.create_basic_transcript_tab())  # Index 2
        main_layout.addWidget(self.basic_tab_stack, 1)

        # Connect sidebar to tab switching
        self.basic_sidebar.currentRowChanged.connect(self.basic_tab_stack.setCurrentIndex)

        return container

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
        record_item = QListWidgetItem("🎙️ Record")
        upload_item = QListWidgetItem("📁 Upload")
        transcript_item = QListWidgetItem("📄 Transcript")

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
        self.basic_upload_progress_label = QLabel("Ready to transcribe")
        self.basic_upload_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_upload_progress_label)

        self.basic_upload_progress_bar = QProgressBar()
        self.basic_upload_progress_bar.setMinimumHeight(25)
        self.basic_upload_progress_bar.hide()  # Hide until processing starts
        layout.addWidget(self.basic_upload_progress_bar)

        # Info tip
        info = QLabel("💡 Files automatically transcribe when dropped or selected")
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
        info_label = QLabel("Recording will use the system's default microphone and audio output.")
        info_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch(1)

        # Record toggle button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignCenter)

        self.basic_record_btn = ModernButton("Start Recording", primary=True)
        self.basic_record_btn.setMinimumHeight(50)
        self.basic_record_btn.setMinimumWidth(220)
        self.basic_record_btn.clicked.connect(self.toggle_basic_recording)
        button_layout.addWidget(self.basic_record_btn)

        layout.addWidget(button_container)
        layout.addSpacing(10)

        # Recording duration (shown during recording, hidden otherwise)
        self.recording_duration_label = QLabel("Duration: 0:00")
        self.recording_duration_label.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {Theme.get('error', self.is_dark_mode)};"
        )
        self.recording_duration_label.setAlignment(Qt.AlignCenter)
        self.recording_duration_label.hide()
        layout.addWidget(self.recording_duration_label)

        layout.addStretch(1)

        # Progress section
        self.basic_record_progress_label = QLabel("Ready to record")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_record_progress_label)

        self.basic_record_progress_bar = QProgressBar()
        self.basic_record_progress_bar.setMinimumHeight(25)
        self.basic_record_progress_bar.hide()  # Hide until processing starts
        layout.addWidget(self.basic_record_progress_bar)

        # Info tip
        info = QLabel("💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click 'Transcribe Recording' to manually start transcription")
        info.setStyleSheet(f"font-size: 12px; color: {Theme.get('info', self.is_dark_mode)};")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Manual transcription button (appears after a recording completes)
        self.transcribe_recording_btn = ModernButton("Transcribe Recording", primary=True)
        self.transcribe_recording_btn.setMinimumHeight(42)
        self.transcribe_recording_btn.hide()
        def _start_transcribe_recording():
            if not self.video_path:
                QMessageBox.information(self, "No Recording", "No recording available. Please record first.")
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
        self.basic_result_text.setPlaceholderText("Transcription text will appear here...")
        self.basic_result_text.setStyleSheet(
            f"QTextEdit {{ background-color: {Theme.get('input_bg', self.is_dark_mode)}; "
            f"color: {Theme.get('text_primary', self.is_dark_mode)}; "
            f"border: 1px solid {Theme.get('border', self.is_dark_mode)}; "
            "border-radius: 8px; padding: 15px; font-family: 'Consolas', 'Monaco', monospace; "
            "font-size: 13px; line-height: 1.6; }}"
        )
        layout.addWidget(self.basic_result_text, 1)

        # Save button
        self.basic_save_btn = ModernButton("💾 Save Transcription", primary=True)
        self.basic_save_btn.setEnabled(False)
        self.basic_save_btn.clicked.connect(self.save_transcription)
        layout.addWidget(self.basic_save_btn)

        # Cancel transcription button (shown only while active)
        self.cancel_transcription_btn = ModernButton("✖ Cancel Transcription")
        self.cancel_transcription_btn.setEnabled(False)
        self.cancel_transcription_btn.hide()
        self.cancel_transcription_btn.clicked.connect(self.cancel_transcription)
        layout.addWidget(self.cancel_transcription_btn)

        widget.setLayout(layout)
        return widget

    def on_file_dropped_basic(self, file_path):
        """Handle file drop - auto-start transcription."""
        self.load_file(file_path)
        QTimer.singleShot(150, self.prompt_multi_language_and_transcribe)

    def browse_file(self):
        """Browse for video/audio file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video or Audio File",
            "",
            "Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)"
        )

        if file_path:
            self.load_file(file_path)
            QTimer.singleShot(150, self.prompt_multi_language_and_transcribe)

    def load_file(self, file_path):
        """Load a video or audio file."""
        self.video_path = file_path
        # Reset language mode so dialog appears for each new file
        self.multi_language_mode = None
        filename = Path(file_path).name

        # Update UI
        self.drop_zone.set_file(filename)
        # Transcription will start after user chooses language mode

        self.statusBar().showMessage(f"File selected: {filename}")
        logger.info(f"Selected file: {file_path}")

    def refresh_audio_devices(self):
        """No-op. Device selection removed."""
        pass

    def update_recording_duration(self):
        """Update recording duration display."""
        if hasattr(self, 'recording_start_time') and self.recording_start_time:
            import time
            elapsed = int(time.time() - self.recording_start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            if hasattr(self, 'recording_duration_label'):
                self.recording_duration_label.setText(f"🔴 Recording: {mins}:{secs:02d}")

