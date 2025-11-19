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
from PySide6.QtCore import Qt, QTimer, QEvent  # type: ignore
from PySide6.QtGui import QPalette  # type: ignore

from gui.theme import Theme
from gui.widgets import ModernButton, Card, DropZone, VUMeter, ModernTabBar, CollapsibleSidebar
from gui.workers import RecordingWorker, TranscriptionWorker, AudioPreviewWorker
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

        # Start audio preview worker for VU meters
        self.audio_preview_worker = None
        self.start_audio_preview()

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
            "recordings_dir": str(Path.home() / "Video2Text" / "Recordings"),
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

        # Update sidebar if it exists (old)
        if hasattr(self, 'basic_sidebar'):
            self.update_sidebar_theme(self.basic_sidebar)

        # Update ModernTabBar theme
        if hasattr(self, 'tab_bar'):
            self.tab_bar.update_theme(self.is_dark_mode)

        # Update CollapsibleSidebar theme
        if hasattr(self, 'collapsible_sidebar'):
            self.collapsible_sidebar.update_theme(self.is_dark_mode)

        # Update settings sidebar theme
        if hasattr(self, 'settings_sidebar'):
            self.settings_sidebar.update_theme(self.is_dark_mode)

            # Update theme section button
            if hasattr(self, 'theme_section_btn'):
                self.theme_section_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {Theme.get('text_secondary', self.is_dark_mode)};
                        border: none;
                        border-radius: 6px;
                        padding: 6px 12px;
                        text-align: left;
                        font-size: 13px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                    }}
                """)

            # Update theme option buttons
            for btn in [getattr(self, 'theme_auto_btn', None),
                       getattr(self, 'theme_light_btn', None),
                       getattr(self, 'theme_dark_btn', None)]:
                if btn:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: transparent;
                            color: {Theme.get('text_primary', self.is_dark_mode)};
                            border: none;
                            border-radius: 6px;
                            padding: 8px 12px 8px 24px;
                            text-align: left;
                            font-size: 13px;
                        }}
                        QPushButton:hover {{
                            background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                        }}
                    """)

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
        """Setup the main UI with modern navigation."""
        central = QWidget()
        self.setCentralWidget(central)

        # Main vertical layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar with hamburger menu
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Modern tab bar
        self.tab_bar = ModernTabBar(
            tabs=[
                ("🎙️", "Record", 0),
                ("📁", "Upload", 1),
                ("📄", "Transcript", 2)
            ],
            is_dark_mode=self.is_dark_mode
        )
        self.tab_bar.tab_changed.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_bar)

        # Content area with sidebar + tabs
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, 1)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("background-color: #F5F5F5; color: #666; padding: 5px;")

    def create_top_bar(self):
        """Create top bar with title."""
        top_bar = QWidget()
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(15, 10, 15, 10)

        # App title
        title = QLabel("FonixFlow")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {Theme.get('text_primary', self.is_dark_mode)};
        """)
        layout.addWidget(title)

        layout.addStretch()

        return top_bar

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

    def create_content_area(self):
        """Create content area with collapsible sidebar and tab stack."""
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

        # Left collapsible sidebar with actions
        self.collapsible_sidebar = CollapsibleSidebar(self.is_dark_mode)
        self.collapsible_sidebar.add_action("🔄", "New Transcription", self.clear_for_new_transcription)
        self.collapsible_sidebar.add_separator()
        self.collapsible_sidebar.add_action("📂", "Change Recordings Folder", self.change_recordings_directory)
        self.collapsible_sidebar.add_action("🗂️", "Open Recordings Folder", self.open_recordings_folder)
        main_layout.addWidget(self.collapsible_sidebar)

        # Tab content stack - order: Record, Upload, Transcript
        self.basic_tab_stack = QStackedWidget()
        self.basic_tab_stack.addWidget(self.create_basic_record_tab())  # Index 0
        self.basic_tab_stack.addWidget(self.create_basic_upload_tab())  # Index 1
        self.basic_tab_stack.addWidget(self.create_basic_transcript_tab())  # Index 2
        main_layout.addWidget(self.basic_tab_stack, 1)

        # Right collapsible sidebar with settings
        self.settings_sidebar = self.create_settings_sidebar()
        main_layout.addWidget(self.settings_sidebar)

        return container

    def on_tab_changed(self, index):
        """Handle tab switching."""
        # Direct switch - animations with windowOpacity don't work well with QStackedWidget
        self.basic_tab_stack.setCurrentIndex(index)
        logger.info(f"Switched to tab index {index}")

    def create_settings_sidebar(self):
        """Create right sidebar with settings."""
        from PySide6.QtWidgets import QPushButton
        sidebar = CollapsibleSidebar(self.is_dark_mode, side='right')

        # Settings header
        settings_label = QLabel("⚙️ Settings")
        settings_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {Theme.get('text_primary', self.is_dark_mode)};
            padding: 8px 12px;
        """)
        sidebar.content_layout.insertWidget(0, settings_label)

        sidebar.add_separator()

        # Theme section header (clickable to expand/collapse)
        self.theme_section_expanded = True
        self.theme_section_btn = QPushButton("▼ 🎨 Theme")
        self.theme_section_btn.setCursor(Qt.PointingHandCursor)
        self.theme_section_btn.setMinimumHeight(36)
        self.theme_section_btn.clicked.connect(self.toggle_theme_section)
        self.theme_section_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.get('text_secondary', self.is_dark_mode)};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
        """)
        sidebar.content_layout.insertWidget(sidebar.content_layout.count() - 1, self.theme_section_btn)

        # Theme options container
        self.theme_options_widget = QWidget()
        theme_options_layout = QVBoxLayout(self.theme_options_widget)
        theme_options_layout.setContentsMargins(0, 0, 0, 0)
        theme_options_layout.setSpacing(2)

        # Create theme option buttons
        self.theme_auto_btn = self.create_theme_option_btn("🔄", "Auto", "auto")
        self.theme_light_btn = self.create_theme_option_btn("☀️", "Light", "light")
        self.theme_dark_btn = self.create_theme_option_btn("🌙", "Dark", "dark")

        theme_options_layout.addWidget(self.theme_auto_btn)
        theme_options_layout.addWidget(self.theme_light_btn)
        theme_options_layout.addWidget(self.theme_dark_btn)

        sidebar.content_layout.insertWidget(sidebar.content_layout.count() - 1, self.theme_options_widget)

        return sidebar

    def create_theme_option_btn(self, icon, label, mode):
        """Create a theme option button."""
        from PySide6.QtWidgets import QPushButton
        btn = QPushButton(f"  {icon} {label}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(36)
        btn.clicked.connect(lambda: self.set_theme_mode(mode))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.get('text_primary', self.is_dark_mode)};
                border: none;
                border-radius: 6px;
                padding: 8px 12px 8px 24px;
                text-align: left;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
        """)
        return btn

    def toggle_theme_section(self):
        """Toggle theme section visibility."""
        self.theme_section_expanded = not self.theme_section_expanded

        if self.theme_section_expanded:
            self.theme_section_btn.setText("▼ 🎨 Theme")
            self.theme_options_widget.show()
        else:
            self.theme_section_btn.setText("▶ 🎨 Theme")
            self.theme_options_widget.hide()

        logger.info(f"Theme section {'expanded' if self.theme_section_expanded else 'collapsed'}")

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

        # VU Meters (horizontal, stacked vertically)
        vu_container = QWidget()
        vu_layout = QVBoxLayout(vu_container)
        vu_layout.setSpacing(10)
        vu_layout.setContentsMargins(20, 10, 20, 10)

        self.mic_vu_meter = VUMeter(label="Microphone")
        self.speaker_vu_meter = VUMeter(label="Speaker")
        vu_layout.addWidget(self.mic_vu_meter)
        vu_layout.addWidget(self.speaker_vu_meter)

        layout.addWidget(vu_container)
        layout.addSpacing(10)

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
        title = QLabel(f"🎙️ Audio Setup Guide for {platform_display}")
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
        close_btn = ModernButton("Close", primary=True)
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
        msg.setWindowTitle("No Microphone Found")
        msg.setText("No audio input device detected!")
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
                    "Device Found",
                    "✅ Audio input device detected!\n\nYou can now start recording."
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
        self.basic_record_btn.setText("Stop Recording")
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

        # Show duration label
        self.recording_duration_label.show()
        self.recording_timer.start(1000)  # Update every second

        # Update status
        self.statusBar().showMessage("🔴 Recording from Microphone + Speaker...")
        self.basic_record_progress_label.setText("Recording in progress...")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('error', self.is_dark_mode)}; font-weight: bold;")

        logger.info(f"Started basic mode recording (mic: default, speaker: default/system)")

        # Stop audio preview worker to avoid conflicts
        self.stop_audio_preview()

        # Start actual recording in QThread worker with default devices
        self.recording_worker = RecordingWorker(
            output_dir=self.settings["recordings_dir"],
            mic_device=None,  # Use default
            speaker_device=None, # Use default
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
        self.basic_record_btn.setText("Start Recording")
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()

        # Re-enable controls
        self.drop_zone.setEnabled(True)

        # Hide duration label
        self.recording_duration_label.hide()

        # Show progress bar for processing
        self.basic_record_progress_bar.show()
        self.basic_record_progress_bar.setValue(0)

        # Update status
        self.statusBar().showMessage("Processing recording...")
        self.basic_record_progress_label.setText("Processing recording...")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('warning', self.is_dark_mode)};")

        logger.info("Stopped basic mode recording")

    def update_recording_duration(self):
        """Update recording duration display."""
        if self.recording_start_time:
            elapsed = int(time.time() - self.recording_start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.recording_duration_label.setText(f"🔴 Recording: {mins}:{secs:02d}")

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
        self.basic_record_btn.setText("🎤 Start Recording")
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()
        self.recording_duration_label.hide()

        # Restart audio preview worker for VU meters
        self.start_audio_preview()

    def change_recordings_directory(self):
        """Open dialog to change recordings directory."""
        current_dir = self.settings["recordings_dir"]
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Recordings Folder",
            current_dir,
            QFileDialog.ShowDirsOnly
        )

        if new_dir:
            self.settings["recordings_dir"] = new_dir
            if hasattr(self, 'recordings_dir_display') and self.recordings_dir_display is not None:
                try:
                    self.recordings_dir_display.setText(new_dir)
                except Exception:
                    pass
            self.save_settings()
            logger.info(f"Recordings directory changed to: {new_dir}")
            QMessageBox.information(
                self,
                "Settings Updated",
                f"Recordings will now be saved to:\n{new_dir}"
            )

    def open_recordings_folder(self):
        """Open the recordings folder in the system file explorer."""
        recordings_dir = Path(self.settings["recordings_dir"])

        # Create directory if it doesn't exist
        recordings_dir.mkdir(parents=True, exist_ok=True)

        # Open in file explorer (cross-platform)
        import subprocess
        import platform

        try:
            if platform.system() == "Windows":
                os.startfile(str(recordings_dir))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(recordings_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(recordings_dir)])

            logger.info(f"Opened recordings folder: {recordings_dir}")
        except Exception as e:
            logger.error(f"Could not open recordings folder: {e}")
            QMessageBox.warning(
                self,
                "Could Not Open Folder",
                f"Please navigate manually to:\n{recordings_dir}"
            )

    def show_recording_dialog(self):
        """Show recording dialog (Advanced Mode only)."""
        dialog = RecordingDialog(self)
        if dialog.exec() and dialog.recorded_path:
            self.load_file(dialog.recorded_path)

    def start_transcription(self):
        """Start transcription process."""
        if not self.video_path:
            QMessageBox.warning(self, "No File", "Please select a file first.")
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
        self.performance_overlay.setText("Starting…")

        # Determine mode from dialog selection; fallback to checkbox if user toggled manually beforehand
        if self.multi_language_mode is None:
            # Prompt now; if canceled, abort
            if not self.prompt_multi_language_and_transcribe(from_start=True):
                return
        multi_mode = self.multi_language_mode

        if multi_mode:
            model_size = "large"  # Highest accuracy for mixed languages
            language = None  # Auto-detect
            detect_language_changes = True
            # Use global deep scan toggle; if False use heuristic + conditional fallback
            use_deep_scan = bool(getattr(self, 'enable_deep_scan', False))
        else:
            model_size = "base"  # Default to base for single-language (more robust on this audio)
            language = None  # Still auto-detect primary language
            detect_language_changes = False
            use_deep_scan = False

        # Start transcription worker
        self.statusBar().showMessage("Starting transcription...")

        self.transcription_worker = TranscriptionWorker(
            self.video_path,
            model_size=model_size,
            language=language,
            detect_language_changes=detect_language_changes,
            use_deep_scan=use_deep_scan,
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
            if self.allowed_languages:
                logger.info(f"User selected languages: {self.allowed_languages}")
            logger.info(f"Language mode chosen via dialog: multi={self.multi_language_mode}")
            self.start_transcription()
            return True
        return False

    def save_transcription(self):
        """Save current transcription (Video2TextQt scope)."""
        if not getattr(self, 'transcription_result', None):
            QMessageBox.warning(self, "No Transcription", "Please transcribe a file first.")
            return
        default_name = Path(self.video_path).stem if self.video_path else "transcription"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            default_name,
            "Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)"
        )
        if not file_path:
            return
        try:
            ext = Path(file_path).suffix.lower()
            content = self.transcription_result.get('text', '')
            if ext == '.srt' or 'SRT' in selected_filter:
                from transcriber import Transcriber
                content = Transcriber().format_as_srt(self.transcription_result)
            elif ext == '.vtt' or 'VTT' in selected_filter:
                from transcriber import Transcriber
                srt_content = Transcriber().format_as_srt(self.transcription_result)
                content = "WEBVTT\n\n" + srt_content.replace(',', '.')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.statusBar().showMessage(f"Saved to: {file_path}")
            QMessageBox.information(self, "Saved Successfully", f"Transcription saved to:\n{file_path}")
            logger.info(f"Transcription saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save transcription:\n\n{e}")

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
    def on_transcription_progress(self, message: str, percentage: int):
        """Handle progress updates emitted by worker (message, percentage)."""
        # Update progress bar (basic mode)
        if hasattr(self, 'basic_upload_progress_bar'):
            try:
                self.basic_upload_progress_bar.setValue(int(max(0, min(100, percentage))))
            except Exception:
                pass
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
        # Status bar
        try:
            self.statusBar().showMessage(message)
        except Exception:
            pass

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
        
        # DEBUG: Log result details
        logger.info(f"=== TRANSCRIPTION RESULT DEBUG ===")
        logger.info(f"Text length: {len(text)} characters")
        logger.info(f"Segments: {segment_count}")
        logger.info(f"Language segments: {len(language_segments)}")
        logger.info(f"Has timeline: {bool(language_timeline)}")
        if language_segments:
            logger.info(f"First 3 language segments: {language_segments[:3]}")
        if not text:
            logger.warning(f"WARNING: text is empty! Checking language_segments...")
            if language_segments:
                # Try to reconstruct text from language_segments
                text = ' '.join(seg.get('text', '') for seg in language_segments)
                logger.info(f"Reconstructed text from language_segments: {len(text)} characters")
        logger.info(f"=== END DEBUG ===")

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
        # Navigate to transcript tab
        if hasattr(self, 'basic_sidebar') and hasattr(self, 'basic_tab_stack'):
            try:
                self.basic_sidebar.setCurrentRow(2)
                self.basic_tab_stack.setCurrentIndex(2)
            except Exception:
                pass
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
        except Exception:
            pass
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
        except Exception:
            pass
        try:
            QMessageBox.critical(self, "Transcription Error", f"Transcription failed:\n\n{error_message}\n\nPlease check the logs for more details.")
        except Exception:
            pass
        logger.error(f"Transcription failed: {error_message}")

        # Clear file field after error (ready for retry or new file)
        if hasattr(self, 'drop_zone'):
            self.drop_zone.clear_file()
        # Reset video path so user must select file again
        self.video_path = None

    def clear_for_new_transcription(self):
        """Reset UI to allow starting a new transcription."""
        # Reset stored result
        self.transcription_result = None
        # Clear text areas
        if hasattr(self, 'basic_result_text'):
            self.basic_result_text.clear()
        # Reset progress bars/labels
        if hasattr(self, 'basic_upload_progress_bar'):
            self.basic_upload_progress_bar.setValue(0)
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText("Ready")
        if hasattr(self, 'basic_record_progress_bar'):
            self.basic_record_progress_bar.setValue(0)
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText("Ready")
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
            self.statusBar().showMessage("Ready for new transcription")
        except Exception:
            pass
        # Hide manual transcribe button if present
        if hasattr(self, 'transcribe_recording_btn'):
            self.transcribe_recording_btn.hide()

    # ---------- Tab activation management ----------
    def on_basic_tab_changed(self, index: int):
        """Handle sidebar tab changes."""
        try:
            # Switch stacked widget
            if hasattr(self, 'basic_tab_stack'):
                self.basic_tab_stack.setCurrentIndex(index)
        except Exception:
            pass

        # If recording is ongoing and user navigates away, stop recording gracefully
        if index != 0 and getattr(self, 'is_recording', False):
            logger.info("Leaving Record tab while recording; stopping recording")
            try:
                self.stop_basic_recording()
            except Exception as e:
                logger.warning(f"Failed to stop recording on tab change: {e}")
        # Update status bar
        try:
            tab_names = {0: "Record", 1: "Upload", 2: "Transcript"}
            self.statusBar().showMessage(f"Switched to {tab_names.get(index, 'Unknown')} tab")
        except Exception:
            pass

    # Override refresh_audio_devices to avoid auto preview start when not on Record tab
    def refresh_audio_devices(self):
        """No-op. Device selection removed."""
        pass