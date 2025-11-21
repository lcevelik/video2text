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
    QComboBox, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QEvent, QCoreApplication  # type: ignore
from PySide6.QtGui import QPalette  # type: ignore

from gui.theme import Theme
from gui.widgets import ModernButton, Card, DropZone, VUMeter, ModernTabBar, CollapsibleSidebar
from gui.workers import RecordingWorker, TranscriptionWorker, AudioPreviewWorker
from gui.dialogs import MultiLanguageChoiceDialog, RecordingDialog
from gui.utils import check_audio_input_devices, get_platform, get_platform_audio_setup_help, has_gpu_available
from gui.managers import SettingsManager, ThemeManager, FileManager
from app.transcriber import Transcriber

logger = logging.getLogger(__name__)

class FonixFlowQt(QMainWindow):
    """Modern Qt-based main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("FonixFlow - Whisper Transcription"))
        self.setMinimumSize(1000, 700)

        # Set application icon
        from PySide6.QtGui import QIcon
        icon_path = os.path.join(os.path.dirname(__file__), '../assets/fonixflow_icon.png')
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.instance().setWindowIcon(app_icon)

        # Initialize managers
        self.settings_manager = SettingsManager(Path.home() / ".fonixflow_config.json")
        self.settings = self.settings_manager.settings  # Keep for backward compatibility
        self.theme_manager = ThemeManager(self, self.settings_manager.get("theme_mode", "dark"))
        self.file_manager = FileManager(self)

        # Audio processing settings
        self.enable_audio_filters = self.settings_manager.get("enable_audio_filters", True)

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

        # Ensure settings widgets are always initialized
        self.audio_options_widget = QWidget()
        audio_options_layout = QVBoxLayout(self.audio_options_widget)
        audio_options_layout.setContentsMargins(0, 0, 0, 0)
        audio_options_layout.setSpacing(2)
        audio_filter_btn = self.create_toggle_option_btn(
            "🎚️", "Enhance Audio",
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
            "🔍", "Deep Scan",
            self.enable_deep_scan,
            self.toggle_deep_scan,
            indent=32
        )
        deep_scan_btn.setToolTip("Re-analyzes audio chunks accurately")
        transcription_options_layout.addWidget(deep_scan_btn)

        self.setup_ui()
        self.theme_manager.apply_theme()
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

        # Start audio preview worker for VU meters
        self.audio_preview_worker = None
        self.start_audio_preview()

    # Early stub to guarantee existence even if later method definition changes order
    def cancel_transcription(self):
        """Cancel active transcription if running (early stub)."""
        if getattr(self, 'transcription_worker', None):
            try:
                self.transcription_worker.cancel()
                self.transcription_worker.quit()
                self.transcription_worker.wait()
                self.transcription_worker = None
            except Exception as e:
                logger.warning(f"Cancel request failed: {e}")
        if hasattr(self, 'cancel_transcription_btn'):
            try:
                self.cancel_transcription_btn.setEnabled(False)
            except Exception as e:
                logger.debug(f"Could not disable cancel button: {e}")
        try:
            self.statusBar().showMessage("Cancel requested…")
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")

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

    def detect_system_theme(self):
        """Detect if system is in dark mode (delegated to ThemeManager)."""
        return self.theme_manager.detect_system_theme()

    def get_effective_theme(self):
        """Get the effective theme based on mode setting (delegated to ThemeManager)."""
        return self.theme_manager.get_effective_theme()

    def apply_theme(self):
        """Apply the current theme to all UI elements (delegated to ThemeManager)."""
        self.theme_manager.apply_theme()

    def closeEvent(self, event):
        """Ensure background threads stop cleanly on window close."""
        try:
            # Stop audio preview worker if running
            if hasattr(self, 'audio_preview_worker') and self.audio_preview_worker and self.audio_preview_worker.isRunning():
                try:
                    self.audio_preview_worker.stop()
                except Exception as e:
                    logger.warning(f"Error stopping audio preview worker: {e}")
                self.audio_preview_worker.wait(1500)
                self.audio_preview_worker = None
            # Stop recording worker if running
            if hasattr(self, 'recording_worker') and self.recording_worker and self.recording_worker.isRunning():
                try:
                    self.recording_worker.stop()
                except Exception as e:
                    logger.warning(f"Error stopping recording worker: {e}")
                self.recording_worker.wait(1500)
                self.recording_worker = None
            # Stop transcription worker if running
            if hasattr(self, 'transcription_worker') and self.transcription_worker and self.transcription_worker.isRunning():
                try:
                    self.transcription_worker.cancel()
                    self.transcription_worker.quit()
                    self.transcription_worker.wait(1500)
                except Exception as e:
                    logger.warning(f"Error stopping transcription worker: {e}")
                self.transcription_worker = None
        except Exception as e:
            logger.warning(f"Error while shutting down workers: {e}")
        super().closeEvent(event)

    def _configure_ffmpeg_converter(self):
        """Configure pydub to use an available ffmpeg binary without requiring shell restart."""
        try:
            import shutil as _shutil
            from pydub import AudioSegment  # type: ignore
        except Exception as e:
            logger.debug(f"Could not import FFmpeg dependencies: {e}")
            return

        # If ffmpeg is on PATH, set converter and return
        if _shutil.which('ffmpeg'):
            try:
                AudioSegment.converter = 'ffmpeg'
                logger.info("pydub configured to use ffmpeg from PATH")
            except Exception as e:
                logger.debug(f"Could not set ffmpeg converter: {e}")
            return

        # Try common install locations, including winget default cache
        candidates = [
            r"C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            r"C:\\Program Files\\FFmpeg\\bin\\ffmpeg.exe",
            str(Path.home() / "scoop" / "apps" / "ffmpeg" / "current" / "bin" / "ffmpeg.exe"),
            str(Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "WinGet" / "Packages" / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe" / "ffmpeg-8.0-full_build" / "bin" / "ffmpeg.exe"),
        ]
        for p in candidates:
            try:
                if Path(p).exists():
                    try:
                        AudioSegment.converter = p
                        logger.info(f"pydub configured to use ffmpeg at: {p}")
                    except Exception as e:
                        logger.debug(f"Could not set AudioSegment.converter, using FFMPEG_BINARY instead: {e}")
                        os.environ['FFMPEG_BINARY'] = p
                        logger.info(f"Set FFMPEG_BINARY for pydub: {p}")
                    break
            except Exception as e:
                logger.debug(f"Could not check path {p}: {e}")
                continue

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
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, 1)

        # Status bar
        self.statusBar().showMessage(self.tr("Ready"))
        self.statusBar().setStyleSheet("background-color: #F5F5F5; color: #666; padding: 5px;")

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
        logo_path = os.path.join(os.path.dirname(__file__), '../assets/fonixflow_logo.png')
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

    def show_menu(self):
        """Show hamburger menu with settings."""
        menu = QMenu(self)

        # Settings submenu
        settings_menu = menu.addMenu(self.tr("⚙️ Settings"))

        # Theme submenu under Settings
        theme_menu = settings_menu.addMenu(self.tr("🎨 Theme"))

        # Theme options
        auto_action = theme_menu.addAction(self.tr("🔄 Auto (System)"))
        auto_action.setCheckable(True)
        auto_action.setChecked(self.theme_mode == "auto")
        auto_action.triggered.connect(lambda: self.set_theme_mode("auto"))

        light_action = theme_menu.addAction(self.tr("☀️ Light"))
        light_action.setCheckable(True)
        light_action.setChecked(self.theme_mode == "light")
        light_action.triggered.connect(lambda: self.set_theme_mode("light"))

        dark_action = theme_menu.addAction(self.tr("🌙 Dark"))
        dark_action.setCheckable(True)
        dark_action.setChecked(self.theme_mode == "dark")
        dark_action.triggered.connect(lambda: self.set_theme_mode("dark"))

        # Recording Settings under Settings
        settings_menu.addSeparator()
        rec_dir_action = settings_menu.addAction(self.tr("📁 Change Recording Directory"))
        rec_dir_action.triggered.connect(self.change_recordings_directory)

        open_dir_action = settings_menu.addAction(self.tr("🗂️ Open Recording Directory"))
        open_dir_action.triggered.connect(self.open_recordings_folder)

        # New Transcription
        menu.addSeparator()
        new_trans_action = menu.addAction(self.tr("🔄 New Transcription"))
        new_trans_action.triggered.connect(self.clear_for_new_transcription)

        # Show menu at button position
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def set_theme_mode(self, mode):
        """Set theme mode (auto/light/dark)."""
        self.theme_mode = mode
        self.theme_manager.set_theme_mode(mode)
        self.is_dark_mode = self.theme_manager.is_dark_mode
        self.settings_manager.set("theme_mode", mode)
        self.save_settings()

    def create_settings_card(self):
        """Create settings card for recordings directory."""
        card = Card(self.tr("⚙️ Recordings Settings"), self.is_dark_mode)

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
                    padding: 15px 10px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                    border-color: {Theme.get('accent', self.is_dark_mode)};
                }}
            """)

        quick_actions_row = QHBoxLayout()
        new_trans_btn = ModernButton(self.tr("🔄 New Transcription"))
        new_trans_btn.clicked.connect(self.clear_for_new_transcription)
        style_settings_btn(new_trans_btn)
        quick_actions_row.addWidget(new_trans_btn)
        change_folder_btn = ModernButton(self.tr("📂 Change Folder"))
        change_folder_btn.clicked.connect(self.change_recordings_directory)
        style_settings_btn(change_folder_btn)
        quick_actions_row.addWidget(change_folder_btn)
        open_folder_btn = ModernButton(self.tr("🗂️ Open Folder"))
        open_folder_btn.clicked.connect(self.open_recordings_folder)
        style_settings_btn(open_folder_btn)
        quick_actions_row.addWidget(open_folder_btn)
        layout.addLayout(quick_actions_row)

        # Recordings directory card
        layout.addWidget(self.create_settings_card())

        # Settings sections (Audio, Transcription)
        settings_sections_label = QLabel(self.tr("Settings Sections"))
        settings_sections_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {Theme.get('text_primary', self.is_dark_mode)};
        """)
        layout.addWidget(settings_sections_label)

        # Audio Processing section
        audio_section_label = QLabel(self.tr("🎙️ Audio Processing"))
        audio_section_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {Theme.get('text_secondary', self.is_dark_mode)};
        """)
        layout.addWidget(audio_section_label)
        for child in self.audio_options_widget.findChildren(QPushButton):
            style_settings_btn(child)
        layout.addWidget(self.audio_options_widget)

        # Transcription section
        transcription_section_label = QLabel(self.tr("📝 Transcription"))
        transcription_section_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {Theme.get('text_secondary', self.is_dark_mode)};
        """)
        layout.addWidget(transcription_section_label)
        for child in self.transcription_options_widget.findChildren(QPushButton):
            style_settings_btn(child)
        layout.addWidget(self.transcription_options_widget)

        layout.addStretch()
        return widget

    def _add_settings_to_sidebar(self, sidebar):
        """Add settings sections to the left sidebar."""
        from PySide6.QtWidgets import QPushButton

        # Settings section header (clickable to expand/collapse)
        self.settings_section_expanded = True
        self.settings_section_btn = QPushButton(self.tr("▼ ⚙️ Settings"))
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
        self.audio_section_btn = QPushButton(self.tr("  ▼ 🎙️ Audio Processing"))
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
            "🎚️", "Enhance Audio",
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
        self.transcription_section_btn = QPushButton(self.tr("  ▼ 📝 Transcription"))
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
            "🔍", "Deep Scan",
            self.enable_deep_scan,
            self.toggle_deep_scan,
            indent=32
        )
        deep_scan_btn.setToolTip("Re-analyzes audio chunks accurately")
        transcription_options_layout.addWidget(deep_scan_btn)

        settings_content_layout.addWidget(self.transcription_options_widget)

        sidebar.content_layout.insertWidget(sidebar.content_layout.count() - 1, self.settings_content_widget)

    def create_vertical_tab_bar(self):
        """Create vertical tab bar on the right side, now with Settings tab."""
        from PySide6.QtWidgets import QPushButton

        tab_bar = QWidget()
        tab_bar.setMinimumWidth(120)
        tab_bar.setMaximumWidth(120)

        layout = QVBoxLayout(tab_bar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)

        # Store current tab index
        self.current_tab_index = 0
        self.tab_buttons = []

        # Create tab buttons
        tabs = [
            ("🎙️", self.tr("Record"), 0),
            ("📁", self.tr("Upload"), 1),
            ("📄", self.tr("Transcript"), 2),
            ("⚙️", self.tr("Settings"), 3)
        ]

        for icon, label, index in tabs:
            translated_label = self.tr(label)
            btn = QPushButton(f"{icon}\n{translated_label}")
            btn.setMinimumHeight(80)
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
            self.settings_section_btn.setText(self.tr("▼ ⚙️ Settings"))
            self.settings_content_widget.show()
        else:
            self.settings_section_btn.setText(self.tr("▶ ⚙️ Settings"))
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
        checkmark = "✅" if is_enabled else "⬜"
        translated_label = self.tr(label)
        btn = QPushButton(f"  {checkmark} {icon} {translated_label}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(36)
        btn.setProperty("callback", callback)  # Store callback
        btn.setProperty("icon", icon)  # Store icon
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

        # Update button visual
        checkmark = "✅" if self.enable_audio_filters else "⬜"
        for child in self.audio_options_widget.findChildren(QPushButton):
            if "Enhance Audio" in child.text():
                icon = child.property("icon") or "🎚️"
                label = child.property("label") or "Enhance Audio"
                child.setText(f"  {checkmark} {icon} {label}")
                break

        logger.info(f"Audio filters {'enabled' if self.enable_audio_filters else 'disabled'}")

    def toggle_deep_scan(self):
        """Toggle deep scan on/off."""
        self.enable_deep_scan = not self.enable_deep_scan
        self.save_settings()

        # Update button visual
        checkmark = "✅" if self.enable_deep_scan else "⬜"
        for child in self.transcription_options_widget.findChildren(QPushButton):
            if "Deep Scan" in child.text():
                icon = child.property("icon") or "🔍"
                label = child.property("label") or "Deep Scan"
                child.setText(f"  {checkmark} {icon} {label}")
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
        self.basic_upload_progress_label = QLabel(self.tr("Ready to transcribe"))
        self.basic_upload_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_upload_progress_label)

        self.basic_upload_progress_bar = QProgressBar()
        self.basic_upload_progress_bar.setMinimumHeight(25)
        self.basic_upload_progress_bar.hide()  # Hide until processing starts
        layout.addWidget(self.basic_upload_progress_bar)

        # Info tip
        info = QLabel(self.tr("💡 Files automatically transcribe when dropped or selected"))
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
        info = QLabel(self.tr("💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click 'Transcribe Recording' to manually start transcription"))
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
        self.basic_save_btn = ModernButton(self.tr("💾 Save Transcription"), primary=True)
        self.basic_save_btn.setEnabled(False)
        self.basic_save_btn.clicked.connect(self.save_transcription)
        layout.addWidget(self.basic_save_btn)

        # Cancel transcription button (shown only while active)
        self.cancel_transcription_btn = ModernButton(self.tr("✖ Cancel Transcription"))
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
        title = QLabel(self.tr(f"🎙️ Audio Setup Guide for {platform_display}"))
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

    def toggle_audio_preview(self):
        """No-op. VU meters and preview removed."""
        pass

    def restart_audio_preview(self):
        """No-op. VU meters and preview removed."""
        pass

    def ensure_audio_preview_running(self):
        """No-op. VU meters and preview removed."""
        pass

    def toggle_basic_recording(self):
        """Toggle recording in Basic Mode (one-button flow)."""
        if not self.is_recording:
            # Check device availability first
            if self.check_audio_devices():
                self.start_basic_recording()
            else:
                # Show helpful message with retry option
                self.show_no_device_dialog()
        else:
            # Stop recording and auto-transcribe
            self.stop_basic_recording()

    def check_audio_devices(self):
        """Check if audio input devices are available."""
        return check_audio_input_devices()  # Use shared utility function

    def show_no_device_dialog(self):
        """Show dialog when no audio device is found."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(self.tr("No Microphone Found"))
        msg.setText(self.tr("No audio input device detected!"))
        msg.setInformativeText(
            "Please:\n"
            "1. Connect a microphone\n"
            "2. Check your audio settings\n"
            "3. Make sure device is enabled\n\n"
            "Click 'Retry' to check again, or 'Cancel' to go back."
        )
        msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Retry)

        result = msg.exec()

        if result == QMessageBox.Retry:
            # User wants to try again - re-check devices
            logger.info("User requested device detection retry")
            if self.check_audio_devices():
                QMessageBox.information(
                    self,
                    self.tr("Device Found"),
                    self.tr("✅ Audio input device detected!\n\nYou can now start recording.")
                )
                # Automatically start recording
                self.start_basic_recording()
            else:
                # Still no device - show dialog again
                self.show_no_device_dialog()

    def start_basic_recording(self):
        """Start recording in Basic Mode."""
        self.is_recording = True
        self.recording_start_time = time.time()

        # Update UI
        self.basic_record_btn.setText(self.tr("Stop Recording"))
        self.basic_record_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)

        # Disable drop zone and device selection during recording
        self.drop_zone.setEnabled(False)

        # Show and start recording timer
        self.recording_time_label.setText(self.tr("00:00:00"))
        self.recording_time_label.show()
        self.recording_timer.start(1000)  # Update every second

        # Update status
        self.statusBar().showMessage(self.tr("🔴 Recording from Microphone + Speaker..."))
        self.basic_record_progress_label.setText(self.tr("Recording in progress..."))
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('error', self.is_dark_mode)}; font-weight: bold;")

        logger.info(f"Started basic mode recording (mic: default, speaker: default/system)")

        # Stop audio preview worker to avoid conflicts
        self.stop_audio_preview()

        # Start actual recording in QThread worker with default devices
        self.recording_worker = RecordingWorker(
            output_dir=self.settings["recordings_dir"],
            mic_device=None,  # Use default
            speaker_device=None,  # Use default
            enable_filters=self.enable_audio_filters,  # Audio filters setting
            parent=self
        )
        self.recording_worker.recording_complete.connect(self.on_recording_complete)
        self.recording_worker.recording_error.connect(self.on_recording_error)
        self.recording_worker.audio_levels_update.connect(self.update_audio_levels)
        self.recording_worker.start()

    def stop_basic_recording(self):
        """Stop recording in Basic Mode."""
        self.is_recording = False
        self.recording_timer.stop()

        # Stop the worker thread
        if self.recording_worker:
            self.recording_worker.stop()

        # Update button
        self.basic_record_btn.setText(self.tr("Start Recording"))
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()

        # Re-enable controls
        self.drop_zone.setEnabled(True)

        # Hide recording timer
        self.recording_time_label.hide()

        # Show progress bar for processing
        self.basic_record_progress_bar.show()
        self.basic_record_progress_bar.setValue(0)
            # self.retranslate_ui()  # Only call in __init__ for startup translation

        # Update status
        self.statusBar().showMessage(self.tr("Processing recording..."))
        self.basic_record_progress_label.setText(self.tr("Processing recording..."))
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('warning', self.is_dark_mode)};")

        logger.info("Stopped basic mode recording")

    def update_recording_duration(self):
        """Update recording duration display."""
        if self.recording_start_time:
            elapsed = int(time.time() - self.recording_start_time)
            hours = elapsed // 3600
            mins = (elapsed % 3600) // 60
            secs = elapsed % 60
            # Show time in HH:MM:SS format (no "Duration:" label)
            self.recording_time_label.setText(f"{hours:02d}:{mins:02d}:{secs:02d}")

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
                    icon = child.property("icon") or "🎚️"
                    label = self.tr("Enhance Audio")
                    checkmark = "✅" if self.enable_audio_filters else "⬜"
                    child.setText(f"  {checkmark} {icon} {label}")
        # Update Deep Scan toggle
        if hasattr(self, 'transcription_options_widget'):
            for child in self.transcription_options_widget.findChildren(QPushButton):
                if "Deep Scan" in child.text():
                    icon = child.property("icon") or "🔍"
                    label = self.tr("Deep Scan")
                    checkmark = "✅" if self.enable_deep_scan else "⬜"
                    child.setText(f"  {checkmark} {icon} {label}")
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
            tab_icons = ["🎙️", "📁", "📄", "⚙️"]
            for i, btn in enumerate(self.tab_buttons):
                btn.setText(f"{tab_icons[i]}\n{tab_labels[i]}")
        # Sidebar
        if hasattr(self, 'collapsible_sidebar'):
            self.collapsible_sidebar.update_action_label("New Transcription", self.tr("New Transcription"))
            self.collapsible_sidebar.update_action_label("Change Folder", self.tr("Change Folder"))
            self.collapsible_sidebar.update_action_label("Open Folder", self.tr("Open Folder"))
        # Settings section
        if hasattr(self, 'settings_section_btn'):
            self.settings_section_btn.setText(self.tr("▼ ⚙️ Settings"))
        # Audio section
        if hasattr(self, 'audio_section_btn'):
            self.audio_section_btn.setText(self.tr("  ▼ 🎙️ Audio Processing"))
        # Transcription section
        if hasattr(self, 'transcription_section_btn'):
            self.transcription_section_btn.setText(self.tr("  ▼ 📝 Transcription"))
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
            self.change_dir_btn.set_label(self.tr("📂 Change Folder"))
        # Open folder button
        if hasattr(self, 'open_folder_btn'):
            self.open_folder_btn.set_label(self.tr("🗂️ Open Folder"))
        # Info labels
        if hasattr(self, 'info_label'):
            self.info_label.setText(self.tr("Recording will use the system's default microphone and audio output."))
        # Add more widget retranslation logic here as needed
        # Add more widget retranslation logic here as needed

    def start_audio_preview(self):
        """Start the audio preview worker for continuous VU meter updates."""
        if self.audio_preview_worker is None or not self.audio_preview_worker.isRunning():
            self.audio_preview_worker = AudioPreviewWorker(parent=self)
            self.audio_preview_worker.audio_levels_update.connect(self.update_audio_levels)
            self.audio_preview_worker.start()
            logger.info("Audio preview worker started for VU meters")

    def stop_audio_preview(self):
        """Stop the audio preview worker."""
        if self.audio_preview_worker and self.audio_preview_worker.isRunning():
            self.audio_preview_worker.stop()
            self.audio_preview_worker.wait()
            logger.info("Audio preview worker stopped")

    def update_audio_levels(self, mic_level, speaker_level):
        """Update VU meters with current audio levels."""
        if hasattr(self, 'mic_vu_meter'):
            self.mic_vu_meter.set_level(mic_level)
        if hasattr(self, 'speaker_vu_meter'):
            self.speaker_vu_meter.set_level(speaker_level)

    def on_recording_complete(self, recorded_path, duration):
        """Slot called when recording completes successfully (thread-safe)."""
        # Load file and update UI
        self.video_path = recorded_path
        # Reset mode for new recording
        self.multi_language_mode = None
        self.statusBar().showMessage(f"✅ Recording complete ({duration:.1f}s). File saved.")

        # Re-enable controls
        self.drop_zone.setEnabled(True)

        # Update progress label
        self.basic_record_progress_label.setText(f"Recording complete ({duration:.1f}s). Ready for manual transcription.")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('success', self.is_dark_mode)};")

        # Show manual transcribe button
        if hasattr(self, 'transcribe_recording_btn'):
            self.transcribe_recording_btn.show()

        # Restart audio preview worker for VU meters
        self.start_audio_preview()

    def on_recording_error(self, error_message):
        """Slot called when recording encounters an error (thread-safe)."""
        self.statusBar().showMessage(error_message)
        self.drop_zone.setEnabled(True)

        # Update progress label
        self.basic_record_progress_label.setText(f"Error: {error_message}")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('error', self.is_dark_mode)};")

        # Reset recording state
        self.is_recording = False
        self.recording_timer.stop()
        self.recording_time_label.hide()
        self.basic_record_btn.setText(self.tr("🎤 Start Recording"))
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()

        # Restart audio preview worker for VU meters
        self.start_audio_preview()

    def change_recordings_directory(self):
        """Open dialog to change recordings directory (delegated to FileManager)."""
        self.file_manager.change_recordings_directory(self.settings_manager)

    def open_recordings_folder(self):
        """Open the recordings folder in the system file explorer (delegated to FileManager)."""
        recordings_dir = self.settings_manager.get("recordings_dir", str(Path.home() / "FonixFlow" / "Recordings"))
        self.file_manager.open_recordings_folder(recordings_dir)

    def show_recording_dialog(self):
        """Show recording dialog (Advanced Mode only)."""
        dialog = RecordingDialog(self)
        if dialog.exec() and dialog.recorded_path:
            self.load_file(dialog.recorded_path)

    def start_transcription(self):
        """Start transcription process."""
        if not self.video_path:
            QMessageBox.warning(self, self.tr("No File"), self.tr("Please select a file first."))
            return

        # Disable buttons and clear results
        self.basic_save_btn.setEnabled(False)
        self.basic_result_text.clear()
        self.basic_upload_progress_bar.show()
        self.basic_upload_progress_bar.setValue(0)
        self.basic_record_progress_bar.show()
        self.basic_record_progress_bar.setValue(0)
        self.cancel_transcription_btn.show()
        self.cancel_transcription_btn.setEnabled(True)
        self.transcription_start_time = time.time()
        if not self.performance_overlay:
            self.performance_overlay = QLabel("")
            self.performance_overlay.setStyleSheet("font-size:12px; color:#888; font-family:Consolas;")
            self.statusBar().addPermanentWidget(self.performance_overlay)
        self.performance_overlay.setText(self.tr("Starting…"))

        # Create model name label if not exists
        if not self.model_name_label:
            self.model_name_label = QLabel("")
            self.model_name_label.setStyleSheet("font-size:12px; color:#0FD2CC; font-weight:bold; font-family:Consolas;")
            self.statusBar().addPermanentWidget(self.model_name_label)

        # Determine mode from dialog selection; fallback to checkbox if user toggled manually beforehand
        if self.multi_language_mode is None:
            # Prompt now; if canceled, abort
            if not self.prompt_multi_language_and_transcribe(from_start=True):
                return
        multi_mode = self.multi_language_mode

        if multi_mode:
            # Multi-language mode: Use turbo if GPU available, otherwise large
            if has_gpu_available():
                model_size = "turbo"
                logger.info("GPU detected: Using turbo model for multi-language transcription")
            else:
                model_size = "large"
                logger.info("No GPU detected: Using large model for multi-language transcription")
            language = None  # Auto-detect
            detect_language_changes = True
            # Use global deep scan toggle; if False use heuristic + conditional fallback
            use_deep_scan = bool(getattr(self, 'enable_deep_scan', False))
        else:
            # Single-language mode: Determine model based on language type
            single_lang_type = getattr(self, 'single_language_type', None)
            if single_lang_type == 'english':
                # English: Use optimized .en model (base.en for speed, small.en for better accuracy)
                model_size = "base.en"
                language = "en"  # Explicitly set English
                logger.info("Single-language English: Using base.en model")
            elif single_lang_type == 'other':
                # Other languages: Use medium multilingual model
                model_size = "medium"
                language = None  # Auto-detect language
                logger.info("Single-language Other: Using medium multilingual model")
            else:
                # Fallback if no selection made (shouldn't happen normally)
                model_size = "base"
                language = None
                logger.warning("No single-language type selected, using base model as fallback")
            detect_language_changes = False
            use_deep_scan = False

        # Update model name display in status bar
        if self.model_name_label:
            self.model_name_label.setText(f"Model: {model_size}")

        # Start transcription worker
        self.statusBar().showMessage("Starting transcription...")

        self.transcription_worker = TranscriptionWorker(
            self.video_path,
            model_size=model_size,
            language=language,
            detect_language_changes=detect_language_changes,
            use_deep_scan=use_deep_scan,
            enable_filters=self.enable_audio_filters,
            parent=self
        )
        # Pass allowed languages to worker if multi-language
        if detect_language_changes and hasattr(self, 'allowed_languages'):
            self.transcription_worker.allowed_languages = self.allowed_languages

        # Connect signals
        self.transcription_worker.progress_update.connect(self.on_transcription_progress)
        self.transcription_worker.transcription_complete.connect(self.on_transcription_complete)
        self.transcription_worker.transcription_error.connect(self.on_transcription_error)

        # Start worker
        self.transcription_worker.start()

        logger.info(f"Started transcription: {self.video_path}, model={model_size}, language={language}, multi-lang={detect_language_changes}, deep-scan={use_deep_scan}")

    # ---------- Multi-language selection dialog & helper ----------
    def prompt_multi_language_and_transcribe(self, from_start: bool = False):
        """Prompt user to choose multi-language vs single-language before transcription.

        Returns True if a selection was made (and transcription started), False if canceled.
        """
        if self.video_path is None:
            return False
        if self.multi_language_mode is not None and not from_start:
            # Already chosen for current file
            self.start_transcription()
            return True
        dlg = MultiLanguageChoiceDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.multi_language_mode = dlg.is_multi_language
            self.allowed_languages = getattr(dlg, 'selected_languages', []) if self.multi_language_mode else []
            # Store single-language type selection ('english' or 'other')
            self.single_language_type = getattr(dlg, 'single_language_type', None)
            if self.allowed_languages:
                logger.info(f"User selected languages: {self.allowed_languages}")
            if self.single_language_type:
                logger.info(f"User selected single-language type: {self.single_language_type}")
            logger.info(f"Language mode chosen via dialog: multi={self.multi_language_mode}")
            self.start_transcription()
            return True
        return False

    def save_transcription(self):
        """Save current transcription (Video2TextQt scope)."""
        if not getattr(self, 'transcription_result', None):
            QMessageBox.warning(self, self.tr("No Transcription"), self.tr("Please transcribe a file first."))
            return
        default_name = Path(self.video_path).stem if self.video_path else "transcription"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Transcription"),
            default_name,
            self.tr("Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)")
        )
        if not file_path:
            return
        try:
            ext = Path(file_path).suffix.lower()
            content = self.transcription_result.get('text', '')
            if ext == '.srt' or 'SRT' in selected_filter:
                from app.transcriber import Transcriber
                content = Transcriber().format_as_srt(self.transcription_result)
            elif ext == '.vtt' or 'VTT' in selected_filter:
                from app.transcriber import Transcriber
                srt_content = Transcriber().format_as_srt(self.transcription_result)
                content = "WEBVTT\n\n" + srt_content.replace(',', '.')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.statusBar().showMessage(f"Saved to: {file_path}")
            QMessageBox.information(self, self.tr("Saved Successfully"), f"Transcription saved to:\n{file_path}")
            logger.info(f"Transcription saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            QMessageBox.critical(self, self.tr("Save Error"), f"Failed to save transcription:\n\n{e}")

    def cancel_transcription(self):
        """User-triggered cancellation for active transcription."""
        if getattr(self, 'transcription_worker', None):
            try:
                self.transcription_worker.cancel()
            except Exception as e:
                logger.warning(f"Cancel request failed: {e}")
            if hasattr(self, 'cancel_transcription_btn'):
                self.cancel_transcription_btn.setEnabled(False)
            self.statusBar().showMessage("Cancel requested…")

    # ---------- Progress handling ----------
    def format_time_mmss(self, seconds: float) -> str:
        """Format time in mm:ss format."""
        total_secs = int(seconds)
        mins = total_secs // 60
        secs = total_secs % 60
        return f"{mins:02d}:{secs:02d}"

    def update_elapsed_time_display(self):
        """Update elapsed time display smoothly (called by timer)."""
        if getattr(self, 'transcription_start_time', None):
            elapsed = time.time() - self.transcription_start_time
            current_pct = getattr(self, 'current_progress_pct', 0)

            if current_pct < 100 and current_pct > 0:
                # Calculate ETA based on current progress rate
                rate = current_pct / elapsed if elapsed > 0 else 0
                eta_seconds = (100 - current_pct) / rate if rate > 0 else 0
                eta_str = self.format_time_mmss(eta_seconds)
            else:
                eta_str = "00:00"

            elapsed_str = self.format_time_mmss(elapsed)

            if hasattr(self, 'performance_overlay') and self.performance_overlay is not None:
                self.performance_overlay.setText(f"{current_pct}% | Elapsed {elapsed_str} | ETA {eta_str}")

    def on_transcription_progress(self, message: str, percentage: int):
        """Handle progress updates emitted by worker (message, percentage)."""
        # Store current progress percentage for timer updates
        self.current_progress_pct = percentage

        # Start elapsed time timer if not already running
        if not hasattr(self, 'elapsed_time_timer'):
            self.elapsed_time_timer = QTimer(self)
            self.elapsed_time_timer.timeout.connect(self.update_elapsed_time_display)
            self.elapsed_time_timer.start(500)  # Update every 500ms for smooth display

        # Update progress bar (basic mode - both upload and record tabs)
        if hasattr(self, 'basic_upload_progress_bar'):
            try:
                self.basic_upload_progress_bar.setValue(int(max(0, min(100, percentage))))
            except Exception as e:
                logger.debug(f"Could not update upload progress bar: {e}")

        if hasattr(self, 'basic_record_progress_bar'):
            try:
                self.basic_record_progress_bar.setValue(int(max(0, min(100, percentage))))
            except Exception as e:
                logger.debug(f"Could not update record progress bar: {e}")

        # Update timing display immediately
        self.update_elapsed_time_display()

        # Timing / ETA overlay
        if getattr(self, 'transcription_start_time', None) and percentage > 0:
            elapsed = time.time() - self.transcription_start_time
            if percentage < 100:
                rate = percentage / elapsed if elapsed > 0 else 0
                eta = (100 - percentage) / rate if rate > 0 else 0
            else:
                eta = 0
            if hasattr(self, 'performance_overlay') and self.performance_overlay is not None:
                self.performance_overlay.setText(f"{percentage}% | Elapsed {elapsed:.1f}s | ETA {eta:.1f}s")

        # Stop timer when complete
        if percentage >= 100:
            if hasattr(self, 'elapsed_time_timer'):
                self.elapsed_time_timer.stop()
                self.elapsed_time_timer.deleteLater()
                delattr(self, 'elapsed_time_timer')

        # Status bar
        try:
            self.statusBar().showMessage(message)
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")

    def on_transcription_complete(self, result: dict):
        """Handle successful transcription completion (worker signal)."""
        from transcription.enhanced import EnhancedTranscriber
        self.transcription_result = result
        text = result.get('text', '')
        segments = result.get('segments', [])
        segment_count = len(segments)
        language = result.get('language', 'unknown')
        lang_name = EnhancedTranscriber.LANGUAGE_NAMES.get(language, language.upper())
        language_timeline = result.get('language_timeline', '')
        language_segments = result.get('language_segments', [])
        
        # Debug logging for transcription results
        logger.debug(f"=== TRANSCRIPTION RESULT DEBUG ===")
        logger.debug(f"Text length: {len(text)} characters")
        logger.debug(f"Segments: {segment_count}")
        logger.debug(f"Language segments: {len(language_segments)}")
        logger.debug(f"Has timeline: {bool(language_timeline)}")
        if language_segments:
            logger.debug(f"First 3 language segments: {language_segments[:3]}")
        if not text:
            logger.warning(f"WARNING: text is empty! Checking language_segments...")
            if language_segments:
                # Try to reconstruct text from language_segments
                text = ' '.join(seg.get('text', '') for seg in language_segments)
                logger.debug(f"Reconstructed text from language_segments: {len(text)} characters")
        logger.debug(f"=== END DEBUG ===")

        has_multilang = bool(language_timeline or language_segments)
        display_text = text
        if has_multilang and language_timeline:
            unique_langs = {seg.get('language', 'unknown') for seg in language_segments}
            lang_names = [EnhancedTranscriber.LANGUAGE_NAMES.get(code, code.upper()) for code in sorted(unique_langs)]
            timeline_block = ("=" * 60 + "\n🌍 LANGUAGE TIMELINE:\n" + "=" * 60 + "\n\n" + language_timeline)
            display_text = f"{text}\n\n{timeline_block}"
            lang_info = f"Languages detected: {', '.join(lang_names)}"
        else:
            lang_info = f"Language: {lang_name}"
        # Update UI widgets
        if hasattr(self, 'basic_result_text'):
            logger.info(f"Setting text in UI. Display text length: {len(display_text)}, First 100 chars: {display_text[:100] if display_text else 'EMPTY'}")
            self.basic_result_text.clear()  # Clear first
            self.basic_result_text.setPlainText(display_text)
            logger.info(f"Text set in UI successfully")
            # Persist debug transcript for inspection (handles dot-only cases)
            try:
                debug_path = Path.cwd() / 'transcription_debug.txt'
                # Collect sample of first 20 segment texts (if available)
                sample_segments = []
                for s in segments[:20]:
                    sample_segments.append(repr(s.get('text','')))
                with open(debug_path, 'w', encoding='utf-8') as dbg:
                    dbg.write('=== Transcript Debug Dump ===\n')
                    dbg.write(f'Total characters: {len(display_text)}\n')
                    dbg.write(f'Total segments: {segment_count}\n')
                    dbg.write(f'Language: {lang_name}\n')
                    dbg.write('--- First 300 characters ---\n')
                    dbg.write(display_text[:300] + '\n')
                    dbg.write('--- Segment samples (first 20) ---\n')
                    for i, seg_txt in enumerate(sample_segments, 1):
                        dbg.write(f'{i}: {seg_txt}\n')
                logger.info(f"Wrote transcript debug file to {debug_path}")
                # Detect if transcript is only punctuation (dot heavy)
                meaningful_chars = sum(c.isalnum() for c in display_text)
                if meaningful_chars < max(10, len(display_text) * 0.02):
                    logger.warning("Transcript appears to be mostly non-meaningful punctuation (dot-only). Possibly silent or low-quality audio.")
            except Exception as dbg_err:
                logger.warning(f"Could not write transcript debug file: {dbg_err}")
        if hasattr(self, 'basic_save_btn'):
            self.basic_save_btn.setEnabled(True)
        if hasattr(self, 'cancel_transcription_btn') and self.cancel_transcription_btn:
            self.cancel_transcription_btn.setEnabled(False)
            self.cancel_transcription_btn.hide()
        # Performance overlay
        if getattr(self, 'transcription_start_time', None) and hasattr(self, 'performance_overlay') and self.performance_overlay:
            total = time.time() - self.transcription_start_time
            audio_dur = segments[-1].get('end', 0) if segments else 0
            rtf = (total / audio_dur) if audio_dur else 0
            self.performance_overlay.setText(f"Finished in {total:.2f}s (RTF {rtf:.2f})")
        # Descriptive labels
        if hasattr(self, 'basic_transcript_desc'):
            if has_multilang:
                self.basic_transcript_desc.setText(f"{lang_info} | {segment_count} segments")
            else:
                self.basic_transcript_desc.setText(f"Language: {lang_name} | {segment_count} segments")
        # Navigate to transcript tab (auto-jump after transcription completes)
        if hasattr(self, 'tab_bar') and hasattr(self, 'basic_tab_stack'):
            try:
                self.on_tab_changed(2)  # Index 2 is the Transcript tab
                logger.info("Auto-jumped to transcript tab after transcription completion")
            except Exception as e:
                logger.warning(f"Could not auto-jump to transcript tab: {e}")
        # Progress bars
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(f"✅ Complete! {lang_info}")
        if hasattr(self, 'basic_upload_progress_bar'):
            self.basic_upload_progress_bar.setValue(100)
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(f"✅ Complete! {lang_info}")
        if hasattr(self, 'basic_record_progress_bar'):
            self.basic_record_progress_bar.setValue(100)
        # Status
        try:
            self.statusBar().showMessage(f"Transcription complete ({segment_count} segments, {lang_info})")
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")
        # Logging
        if has_multilang:
            logger.info(f"Multi-language transcription complete: {len(language_segments)} language segments detected")
        logger.info(f"Transcription complete: {len(text)} characters, {segment_count} segments")

        # Clear file field after transcription completes (ready for next file)
        # Keep the transcript visible but allow user to easily upload a new file
        if hasattr(self, 'drop_zone'):
            self.drop_zone.clear_file()
        # Reset video path so user must select new file
        self.video_path = None

    def on_transcription_error(self, error_message: str):
        """Handle transcription error (worker signal)."""
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(f"❌ Error: {error_message}")
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(f"❌ Error: {error_message}")
        if hasattr(self, 'cancel_transcription_btn') and self.cancel_transcription_btn:
            self.cancel_transcription_btn.setEnabled(False)
            self.cancel_transcription_btn.hide()
        try:
            self.statusBar().showMessage("Transcription failed")
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")
        try:
            QMessageBox.critical(self, self.tr("Transcription Error"), f"Transcription failed:\n\n{error_message}\n\nPlease check the logs for more details.")
        except Exception as e:
            logger.warning(f"Could not show error dialog: {e}")
        logger.error(f"Transcription failed: {error_message}")

        # Clear file field after error (ready for retry or new file)
        if hasattr(self, 'drop_zone'):
            self.drop_zone.clear_file()
        # Reset video path so user must select file again
        self.video_path = None

    def clear_for_new_transcription(self):
        """Cancel any active transcription and reset UI for new transcription."""
        # Hide and reset recording timer and progress indicators in footer
        if hasattr(self, 'recording_timer'):
            self.recording_timer.stop()
        if hasattr(self, 'recording_time_label'):
            self.recording_time_label.hide()
            self.recording_time_label.setText("")
        if hasattr(self, 'basic_record_progress_bar'):
            self.basic_record_progress_bar.hide()
            self.basic_record_progress_bar.setValue(0)
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(self.tr("Ready"))
        if hasattr(self, 'basic_upload_progress_bar'):
            self.basic_upload_progress_bar.hide()
            self.basic_upload_progress_bar.setValue(0)
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(self.tr("Ready"))

        # Cancel active transcription if running
        self.cancel_transcription()
        # Stop recording worker if running
        if hasattr(self, 'recording_worker') and self.recording_worker and self.recording_worker.isRunning():
            try:
                self.recording_worker.stop()
            except Exception:
                pass
            self.recording_worker.wait(1500)
            self.recording_worker = None
        # Stop audio preview worker if running
        if hasattr(self, 'audio_preview_worker') and self.audio_preview_worker and self.audio_preview_worker.isRunning():
            try:
                self.audio_preview_worker.stop()
            except Exception:
                pass
            self.audio_preview_worker.wait(1500)
            self.audio_preview_worker = None
        # Reset stored result
        self.transcription_result = None
        # Clear text areas
        if hasattr(self, 'basic_result_text'):
            self.basic_result_text.clear()
        # Reset progress bars/labels
        if hasattr(self, 'basic_upload_progress_bar'):
            self.basic_upload_progress_bar.setValue(0)
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(self.tr("Ready"))
        if hasattr(self, 'basic_record_progress_bar'):
            self.basic_record_progress_bar.setValue(0)
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(self.tr("Ready"))
        # Disable save until new result
        if hasattr(self, 'basic_save_btn'):
            self.basic_save_btn.setEnabled(False)
        # Reset overlay
        if hasattr(self, 'performance_overlay') and self.performance_overlay:
            self.performance_overlay.setText("")
        # Clear file field in upload drop zone
        if hasattr(self, 'drop_zone'):
            self.drop_zone.clear_file()
        # Reset mode selection for new file
        self.multi_language_mode = None
        try:
            self.statusBar().showMessage(self.tr("Ready for new transcription"))
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")
        # Hide manual transcribe button if present
        if hasattr(self, 'transcribe_recording_btn'):
            self.transcribe_recording_btn.hide()

        # Restart audio preview worker for VU meters
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