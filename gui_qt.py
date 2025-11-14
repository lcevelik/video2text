"""
Modern Qt-based GUI for Video2Text

A beautiful, user-friendly interface built with PySide6/Qt.
Features modern design, smooth animations, and excellent cross-platform support.
"""

import sys
import os
import logging
import json
import time
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QFileDialog,
    QMessageBox, QComboBox, QRadioButton, QButtonGroup, QGroupBox,
    QStackedWidget, QFrame, QSizePolicy, QScrollArea, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QDragEnterEvent, QDropEvent

from audio_extractor import AudioExtractor
from transcriber import Transcriber

logger = logging.getLogger(__name__)


class RecordingWorker(QThread):
    """Qt worker thread for audio recording with proper signal handling."""

    # Signals for thread-safe communication with main thread
    recording_complete = Signal(str, float)  # (file_path, duration)
    recording_error = Signal(str)  # error_message
    status_update = Signal(str)  # status_message

    def __init__(self, output_dir, parent=None):
        super().__init__(parent)
        self.is_recording = True
        self.output_dir = Path(output_dir)

    def stop(self):
        """Stop the recording."""
        self.is_recording = False

    def run(self):
        """Execute recording in background thread."""
        try:
            import sounddevice as sd
            import numpy as np
            from scipy.io import wavfile
            from datetime import datetime

            sample_rate = 16000
            mic_chunks = []
            speaker_chunks = []

            # Device detection
            devices = sd.query_devices()

            # Find microphone
            mic_device = None
            try:
                default_input = sd.default.device[0]
                if default_input is not None and default_input >= 0:
                    if devices[default_input]['max_input_channels'] > 0:
                        mic_device = default_input
            except:
                pass

            if mic_device is None:
                for idx, device in enumerate(devices):
                    if device['max_input_channels'] > 0:
                        device_name_lower = device['name'].lower()
                        if not any(kw in device_name_lower for kw in ['stereo mix', 'loopback', 'monitor']):
                            mic_device = idx
                            break

            if mic_device is None:
                logger.error("No microphone found in worker")
                self.recording_error.emit("❌ No microphone found!")
                return

            # Find loopback device
            loopback_device = None
            for idx, device in enumerate(devices):
                if idx == mic_device:
                    continue
                device_name_lower = device['name'].lower()
                if any(kw in device_name_lower for kw in ['stereo mix', 'loopback', 'monitor', 'blackhole']):
                    if device['max_input_channels'] > 0:
                        loopback_device = idx
                        break

            # Callbacks
            def mic_callback(indata, frames, time_info, status):
                if self.is_recording:
                    mic_chunks.append(indata.copy())

            def speaker_callback(indata, frames, time_info, status):
                if self.is_recording:
                    speaker_chunks.append(indata.copy())

            # Start streams
            mic_stream = sd.InputStream(device=mic_device, samplerate=sample_rate, channels=1, callback=mic_callback)
            mic_stream.start()

            speaker_stream = None
            if loopback_device is not None:
                try:
                    speaker_stream = sd.InputStream(device=loopback_device, samplerate=sample_rate, channels=1, callback=speaker_callback)
                    speaker_stream.start()
                except:
                    pass

            # Record while active
            while self.is_recording:
                sd.sleep(100)

            # Stop streams
            mic_stream.stop()
            mic_stream.close()
            if speaker_stream:
                speaker_stream.stop()
                speaker_stream.close()

            # Process and save
            if mic_chunks:
                mic_data = np.concatenate(mic_chunks, axis=0)

                if speaker_chunks:
                    speaker_data = np.concatenate(speaker_chunks, axis=0)
                    max_len = max(len(mic_data), len(speaker_data))
                    if len(mic_data) < max_len:
                        mic_data = np.pad(mic_data, ((0, max_len - len(mic_data)), (0, 0)))
                    if len(speaker_data) < max_len:
                        speaker_data = np.pad(speaker_data, ((0, max_len - len(speaker_data)), (0, 0)))
                    final_data = (mic_data * 0.6 + speaker_data * 0.4)
                    max_val = np.max(np.abs(final_data))
                    if max_val > 0:
                        final_data = final_data / max_val * 0.9
                else:
                    final_data = mic_data

                # Create output directory if it doesn't exist
                self.output_dir.mkdir(parents=True, exist_ok=True)

                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
                recorded_path = str(self.output_dir / filename)

                # Save recording
                final_data_int16 = (final_data * 32767).astype(np.int16)
                wavfile.write(recorded_path, sample_rate, final_data_int16)

                duration = len(final_data) / sample_rate
                logger.info(f"Recording saved: {recorded_path} ({duration:.1f}s)")

                # Emit signal to main thread
                self.recording_complete.emit(recorded_path, duration)

        except Exception as e:
            logger.error(f"Recording error: {e}", exc_info=True)
            self.recording_error.emit(f"❌ Recording error: {str(e)}")


class ModernButton(QPushButton):
    """Modern styled button with hover effects."""

    def __init__(self, text, primary=False):
        super().__init__(text)
        self.primary = primary
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()

    def apply_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #333;
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    border-color: #2196F3;
                    background-color: #F5F5F5;
                }
                QPushButton:pressed {
                    background-color: #EEEEEE;
                }
                QPushButton:disabled {
                    background-color: #F5F5F5;
                    color: #BDBDBD;
                }
            """)


class Card(QFrame):
    """Modern card widget with shadow effect."""

    def __init__(self, title=""):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            Card {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        self.setLayout(layout)


class DropZone(QFrame):
    """Drag and drop zone for files."""

    file_dropped = Signal(str)
    clicked = Signal()  # Signal emitted when user clicks the drop zone

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setMaximumHeight(200)
        self.has_file = False
        self.setCursor(Qt.PointingHandCursor)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("🎬")
        self.icon_label.setStyleSheet("font-size: 48px;")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel("Drag & Drop Video/Audio File Here\n\nor click Browse")
        self.text_label.setStyleSheet("font-size: 16px; color: #666;")
        self.text_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)

        self.setLayout(self.layout)
        self.update_style()

    def update_style(self, hovering=False):
        if self.has_file:
            color = "#4CAF50"
            bg = "#E8F5E9"
        elif hovering:
            color = "#2196F3"
            bg = "#E3F2FD"
        else:
            color = "#E0E0E0"
            bg = "#FAFAFA"

        self.setStyleSheet(f"""
            DropZone {{
                background-color: {bg};
                border: 3px dashed {color};
                border-radius: 12px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.update_style(hovering=True)

    def dragLeaveEvent(self, event):
        self.update_style(hovering=False)

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.file_dropped.emit(files[0])
        self.update_style(hovering=False)

    def set_file(self, filename):
        self.has_file = True
        self.icon_label.setText("✅")
        self.text_label.setText(f"Selected: {filename}\n\nClick to change")
        self.update_style()

    def clear_file(self):
        self.has_file = False
        self.icon_label.setText("🎬")
        self.text_label.setText("Drag & Drop Video/Audio File Here\n\nor click Browse")
        self.update_style()

    def mousePressEvent(self, event):
        """Handle mouse click - emit signal instead of navigating parent chain."""
        self.clicked.emit()


class RecordingDialog(QDialog):
    """Modern recording dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio Recording")
        self.setMinimumSize(500, 400)
        self.recording = False
        self.start_time = None
        self.recorded_path = None
        self.worker = None  # QThread worker for recording

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title
        title = QLabel("🎤 Audio Recording")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Info card
        info_card = Card()
        info_card.content_layout.addWidget(QLabel("What will be recorded:"))
        info_card.content_layout.addWidget(QLabel("🎤 Microphone: Your voice and ambient sounds"))
        info_card.content_layout.addWidget(QLabel("🔊 Speaker: System audio, music, video calls"))
        info_card.content_layout.addWidget(QLabel("📝 Both sources mixed into one recording"))
        layout.addWidget(info_card)

        # Status
        self.status_label = QLabel("Ready to record")
        self.status_label.setStyleSheet("font-size: 14px; color: #666;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Duration
        self.duration_label = QLabel("Duration: 0:00")
        self.duration_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        self.duration_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.duration_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = ModernButton("🔴 Start Recording", primary=True)
        self.stop_btn = ModernButton("⏹️ Stop Recording")
        self.stop_btn.setEnabled(False)
        close_btn = ModernButton("Close")

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        close_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        # Tip
        tip = QLabel("💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured.")
        tip.setStyleSheet("font-size: 11px; color: #999;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)

        layout.addStretch()
        self.setLayout(layout)

        # Timer for duration update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_duration)

    def start_recording(self):
        # Check device availability first
        if not self.check_audio_devices():
            # Show helpful message with retry option
            self.show_no_device_dialog()
            return

        self.recording = True
        self.start_time = time.time()
        self.status_label.setText("🔴 Recording from Microphone + Speaker...")
        self.status_label.setStyleSheet("font-size: 14px; color: #F44336; font-weight: bold;")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.timer.start(1000)

        # Start actual recording in QThread worker
        # Get recordings directory from parent window
        recordings_dir = self.parent().settings["recordings_dir"] if hasattr(self.parent(), 'settings') else str(Path.home() / "Video2Text" / "Recordings")
        self.worker = RecordingWorker(recordings_dir, self)
        self.worker.recording_complete.connect(self.on_recording_complete)
        self.worker.recording_error.connect(self.on_recording_error)
        self.worker.start()

    def stop_recording(self):
        self.recording = False

        # Stop the worker thread
        if self.worker:
            self.worker.stop()

        self.status_label.setText("⏹️ Stopping recording...")
        self.status_label.setStyleSheet("font-size: 14px; color: #FF9800;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.timer.stop()

    def update_duration(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.duration_label.setText(f"Duration: {mins}:{secs:02d}")

    def check_audio_devices(self):
        """Check if audio input devices are available."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()

            # Check for any input device
            has_input = any(d['max_input_channels'] > 0 for d in devices)

            if has_input:
                logger.info(f"Audio devices available: {sum(1 for d in devices if d['max_input_channels'] > 0)} input device(s)")
                return True
            else:
                logger.warning("No audio input devices found")
                return False

        except Exception as e:
            logger.error(f"Error checking audio devices: {e}")
            return False

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
            logger.info("User requested device detection retry (Advanced Mode)")
            if self.check_audio_devices():
                QMessageBox.information(
                    self,
                    "Device Found",
                    "✅ Audio input device detected!\n\nYou can now start recording."
                )
                # Automatically start recording
                self.start_recording()
            else:
                # Still no device - show dialog again
                self.show_no_device_dialog()

    def on_recording_complete(self, recorded_path, duration):
        """Slot called when recording completes successfully (thread-safe)."""
        self.recorded_path = recorded_path
        self.status_label.setText(f"✅ Recording complete ({duration:.1f}s)")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_recording_error(self, error_message):
        """Slot called when recording encounters an error (thread-safe)."""
        self.status_label.setText(f"❌ Error: {error_message}")
        self.status_label.setStyleSheet("font-size: 14px; color: #F44336;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.recording = False
        self.timer.stop()


class Video2TextQt(QMainWindow):
    """Modern Qt-based main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video2Text - Whisper Transcription")
        self.setMinimumSize(1000, 700)

        # Config file location
        self.config_file = Path.home() / ".video2text_config.json"

        # Load settings
        self.settings = self.load_settings()

        # State
        self.video_path = None
        self.transcription_result = None
        self.transcriber = None
        self.audio_extractor = AudioExtractor()
        self.current_mode = "basic"

        self.setup_ui()
        self.center_window()

    def load_settings(self):
        """Load settings from config file."""
        default_settings = {
            "recordings_dir": str(Path.home() / "Video2Text" / "Recordings")
        }

        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
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

        # Mode switcher
        mode_switcher = self.create_mode_switcher()
        layout.addWidget(mode_switcher)

        # Stacked widget for modes
        self.mode_stack = QStackedWidget()
        self.mode_stack.addWidget(self.create_basic_mode())
        self.mode_stack.addWidget(self.create_advanced_mode())
        layout.addWidget(self.mode_stack)

        # Progress section
        progress_section = self.create_progress_section()
        layout.addWidget(progress_section)

        # Result section
        result_section = self.create_result_section()
        layout.addWidget(result_section, 1)

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
        """Create application header."""
        header = QWidget()
        layout = QHBoxLayout()

        title = QLabel("🎬 Video2Text")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")

        subtitle = QLabel("AI-Powered Transcription with Whisper")
        subtitle.setStyleSheet("font-size: 14px; color: #666;")

        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(5)

        layout.addLayout(title_layout)
        layout.addStretch()

        header.setLayout(layout)
        return header

    def create_mode_switcher(self):
        """Create mode switcher buttons."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.basic_btn = ModernButton("📱 Basic Mode", primary=True)
        self.advanced_btn = ModernButton("⚙️ Advanced Mode")

        self.basic_btn.setMinimumWidth(150)
        self.advanced_btn.setMinimumWidth(150)

        self.basic_btn.clicked.connect(lambda: self.switch_mode("basic"))
        self.advanced_btn.clicked.connect(lambda: self.switch_mode("advanced"))

        layout.addWidget(self.basic_btn)
        layout.addWidget(self.advanced_btn)
        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def create_settings_card(self):
        """Create settings card for recordings directory."""
        card = Card("⚙️ Recordings Settings")

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
        """Create basic mode interface."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)

        # State for recording
        self.is_recording = False
        self.recording_start_time = None
        self.recording_worker = None  # QThread worker for recording
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_duration)

        # Description
        desc = QLabel("Simple, automatic transcription. Drop a file or record audio!")
        desc.setStyleSheet("font-size: 15px; color: #666; margin-bottom: 10px;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        # Drop zone - more prominent
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.load_file)
        self.drop_zone.clicked.connect(self.browse_file)
        layout.addWidget(self.drop_zone)

        # Recording duration (shown during recording, hidden otherwise)
        self.recording_duration_label = QLabel("Duration: 0:00")
        self.recording_duration_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #F44336; "
            "margin-top: 10px; margin-bottom: 10px;"
        )
        self.recording_duration_label.setAlignment(Qt.AlignCenter)
        self.recording_duration_label.hide()
        layout.addWidget(self.recording_duration_label)

        # Main action buttons - cleaner layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        # Browse button
        self.browse_btn = ModernButton("📁 Browse File")
        self.browse_btn.setMinimumWidth(180)
        self.browse_btn.setMinimumHeight(45)
        self.browse_btn.clicked.connect(self.browse_file)

        # Record toggle button
        self.basic_record_btn = ModernButton("🎤 Start Recording", primary=True)
        self.basic_record_btn.setMinimumWidth(180)
        self.basic_record_btn.setMinimumHeight(45)
        self.basic_record_btn.clicked.connect(self.toggle_basic_recording)

        btn_layout.addStretch()
        btn_layout.addWidget(self.browse_btn)
        btn_layout.addWidget(self.basic_record_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Transcribe button - more prominent
        self.basic_transcribe_btn = ModernButton("✨ Transcribe Now", primary=True)
        self.basic_transcribe_btn.setMinimumHeight(55)
        self.basic_transcribe_btn.setEnabled(False)
        self.basic_transcribe_btn.clicked.connect(self.start_transcription)
        self.basic_transcribe_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        layout.addWidget(self.basic_transcribe_btn)

        # Info tip
        info = QLabel("💡 Tip: Recording auto-transcribes • Auto-selects best model")
        info.setStyleSheet("font-size: 12px; color: #2196F3; margin-top: 15px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        # Add spacer
        layout.addSpacing(20)

        # Settings card - moved to bottom, less intrusive
        settings_card = self.create_settings_card()
        layout.addWidget(settings_card)

        # Status label (hidden file info, only shown when needed)
        self.basic_file_label = QLabel("")
        self.basic_file_label.setStyleSheet("font-size: 11px; color: #999;")
        self.basic_file_label.setAlignment(Qt.AlignCenter)
        self.basic_file_label.setWordWrap(True)
        self.basic_file_label.hide()  # Hidden by default
        layout.addWidget(self.basic_file_label)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_advanced_mode(self):
        """Create advanced mode interface."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # File selection card
        file_card = Card("Media File")
        file_layout = QHBoxLayout()
        self.adv_file_label = QLabel("No file selected")
        browse_btn = ModernButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.adv_file_label, 1)
        file_layout.addWidget(browse_btn)
        file_card.content_layout.addLayout(file_layout)
        layout.addWidget(file_card)

        # Settings card (shared with Basic Mode)
        settings_card = self.create_settings_card()
        layout.addWidget(settings_card)

        # Recording card
        record_card = Card("Audio Recording")
        record_btn = ModernButton("🎤 Record (Mic + Speaker)", primary=True)
        record_btn.clicked.connect(self.show_recording_dialog)
        record_card.content_layout.addWidget(record_btn)
        record_card.content_layout.addWidget(QLabel("Records both microphone and speaker audio simultaneously"))
        layout.addWidget(record_card)

        # Model selection card
        model_card = Card("Whisper Model")
        self.auto_model_check = QRadioButton("🤖 Auto-select model (recommended)")
        self.auto_model_check.setChecked(True)
        self.manual_model_check = QRadioButton("Manual selection")

        self.model_combo = QComboBox()
        self.model_combo.addItems(Transcriber.MODEL_SIZES)
        self.model_combo.setCurrentText("tiny")
        self.model_combo.setEnabled(False)

        self.auto_model_check.toggled.connect(lambda checked: self.model_combo.setEnabled(not checked))

        model_card.content_layout.addWidget(self.auto_model_check)
        model_card.content_layout.addWidget(self.manual_model_check)
        model_card.content_layout.addWidget(self.model_combo)
        layout.addWidget(model_card)

        # Language card
        lang_card = Card("Language")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Auto-detect", "English", "Spanish", "French", "German",
                                   "Italian", "Portuguese", "Russian", "Japanese", "Korean",
                                   "Chinese", "Arabic"])
        lang_card.content_layout.addWidget(self.lang_combo)
        layout.addWidget(lang_card)

        # Output format card
        format_card = Card("Output Format")
        format_layout = QHBoxLayout()
        self.txt_radio = QRadioButton("Plain Text (.txt)")
        self.srt_radio = QRadioButton("SRT Subtitles (.srt)")
        self.vtt_radio = QRadioButton("VTT Subtitles (.vtt)")
        self.txt_radio.setChecked(True)

        format_layout.addWidget(self.txt_radio)
        format_layout.addWidget(self.srt_radio)
        format_layout.addWidget(self.vtt_radio)
        format_card.content_layout.addLayout(format_layout)
        layout.addWidget(format_card)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.adv_start_btn = ModernButton("Start Transcription", primary=True)
        self.adv_start_btn.setEnabled(False)
        self.adv_start_btn.clicked.connect(self.start_transcription)
        btn_layout.addWidget(self.adv_start_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll

    def create_progress_section(self):
        """Create progress section."""
        card = Card("Progress")

        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("font-size: 13px; color: #666;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 6px;
            }
        """)

        card.content_layout.addWidget(self.progress_label)
        card.content_layout.addWidget(self.progress_bar)

        return card

    def create_result_section(self):
        """Create result section."""
        card = Card("Transcription Result")

        self.result_text = QTextEdit()
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)

        self.save_btn = ModernButton("💾 Save Transcription", primary=True)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_transcription)

        card.content_layout.addWidget(self.result_text, 1)
        card.content_layout.addWidget(self.save_btn)

        return card

    def center_window(self):
        """Center window on screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def switch_mode(self, mode):
        """Switch between basic and advanced modes."""
        self.current_mode = mode

        if mode == "basic":
            self.mode_stack.setCurrentIndex(0)
            self.basic_btn.primary = True
            self.advanced_btn.primary = False
        else:
            self.mode_stack.setCurrentIndex(1)
            self.basic_btn.primary = False
            self.advanced_btn.primary = True

        self.basic_btn.apply_style()
        self.advanced_btn.apply_style()

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

    def load_file(self, file_path):
        """Load a video or audio file."""
        self.video_path = file_path
        filename = Path(file_path).name

        # Update UI based on mode
        if self.current_mode == "basic":
            self.drop_zone.set_file(filename)
            self.basic_file_label.setText(f"Selected: {filename}")
            self.basic_transcribe_btn.setEnabled(True)
        else:
            self.adv_file_label.setText(filename)
            self.adv_start_btn.setEnabled(True)

        self.statusBar().showMessage(f"File selected: {filename}")
        logger.info(f"Selected file: {file_path}")

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
        try:
            import sounddevice as sd
            devices = sd.query_devices()

            # Check for any input device
            has_input = any(d['max_input_channels'] > 0 for d in devices)

            if has_input:
                logger.info(f"Audio devices available: {sum(1 for d in devices if d['max_input_channels'] > 0)} input device(s)")
                return True
            else:
                logger.warning("No audio input devices found")
                return False

        except Exception as e:
            logger.error(f"Error checking audio devices: {e}")
            return False

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
        self.basic_record_btn.setText("⏹️ Stop Recording")
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

        # Disable other controls
        self.browse_btn.setEnabled(False)
        self.basic_transcribe_btn.setEnabled(False)
        self.drop_zone.setEnabled(False)

        # Show duration label
        self.recording_duration_label.show()
        self.recording_timer.start(1000)  # Update every second

        # Update status
        self.statusBar().showMessage("🔴 Recording from Microphone + Speaker...")
        self.basic_file_label.setText("Recording in progress...")
        self.basic_file_label.setStyleSheet("font-size: 12px; color: #F44336;")

        logger.info("Started basic mode recording")

        # Start actual recording in QThread worker
        self.recording_worker = RecordingWorker(self.settings["recordings_dir"], self)
        self.recording_worker.recording_complete.connect(self.on_recording_complete)
        self.recording_worker.recording_error.connect(self.on_recording_error)
        self.recording_worker.start()

    def stop_basic_recording(self):
        """Stop recording in Basic Mode."""
        self.is_recording = False
        self.recording_timer.stop()

        # Stop the worker thread
        if self.recording_worker:
            self.recording_worker.stop()

        # Update button
        self.basic_record_btn.setText("🎤 Start Recording")
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()

        # Hide duration label
        self.recording_duration_label.hide()

        # Update status
        self.statusBar().showMessage("Processing recording...")
        self.basic_file_label.setText("Processing...")

        logger.info("Stopped basic mode recording")

    def update_recording_duration(self):
        """Update recording duration display."""
        if self.recording_start_time:
            elapsed = int(time.time() - self.recording_start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.recording_duration_label.setText(f"🔴 Recording: {mins}:{secs:02d}")

    def on_recording_complete(self, recorded_path, duration):
        """Slot called when recording completes successfully (thread-safe)."""
        # Load file and update UI
        self.video_path = recorded_path
        self.statusBar().showMessage(f"✅ Recording complete ({duration:.1f}s) - Starting transcription...")

        # Re-enable controls
        self.browse_btn.setEnabled(True)
        self.drop_zone.setEnabled(True)

        # Auto-start transcription
        QTimer.singleShot(500, self.start_transcription)

    def on_recording_error(self, error_message):
        """Slot called when recording encounters an error (thread-safe)."""
        self.statusBar().showMessage(error_message)
        self.browse_btn.setEnabled(True)
        self.drop_zone.setEnabled(True)

        # Reset recording state
        self.is_recording = False
        self.recording_timer.stop()
        self.basic_record_btn.setText("🎤 Start Recording")
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()
        self.recording_duration_label.hide()

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
            self.recordings_dir_display.setText(new_dir)
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
        if dialog.exec_() and dialog.recorded_path:
            self.load_file(dialog.recorded_path)

    def start_transcription(self):
        """Start transcription process."""
        if not self.video_path:
            QMessageBox.warning(self, "No File", "Please select a file first.")
            return

        # Disable buttons
        if self.current_mode == "basic":
            self.basic_transcribe_btn.setEnabled(False)
        else:
            self.adv_start_btn.setEnabled(False)

        self.save_btn.setEnabled(False)
        self.result_text.clear()
        self.progress_bar.setValue(0)

        # TODO: Implement transcription in background thread
        self.statusBar().showMessage("Transcribing...")
        self.progress_label.setText("Starting transcription...")

        QMessageBox.information(self, "Coming Soon",
                               "Transcription implementation in progress.\n"
                               "All UI elements are ready!")

    def save_transcription(self):
        """Save transcription to file."""
        if not self.transcription_result:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            "",
            "Text Files (*.txt);;SRT Files (*.srt);;VTT Files (*.vtt)"
        )

        if file_path:
            # TODO: Implement save logic
            QMessageBox.information(self, "Saved", f"Transcription saved to:\n{file_path}")


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
