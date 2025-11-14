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
    QStackedWidget, QFrame, QSizePolicy, QScrollArea, QDialog, QListWidget, QListWidgetItem,
    QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QDragEnterEvent, QDropEvent

from audio_extractor import AudioExtractor
from transcriber import Transcriber
from transcriber_enhanced import EnhancedTranscriber

logger = logging.getLogger(__name__)


class Theme:
    """Theme colors for light and dark modes."""

    LIGHT = {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F5F5F5',
        'bg_tertiary': '#FAFAFA',
        'text_primary': '#333333',
        'text_secondary': '#555555',
        'text_disabled': '#999999',
        'border': '#E0E0E0',
        'accent': '#2196F3',
        'accent_hover': '#1976D2',
        'success': '#4CAF50',
        'success_hover': '#45a049',
        'error': '#F44336',
        'warning': '#FF9800',
        'info': '#2196F3',
        'card_bg': '#FFFFFF',
        'card_border': '#E0E0E0',
        'input_bg': '#FAFAFA',
        'button_bg': '#FFFFFF',
        'button_text': '#333333',
        'dropzone_bg': '#FAFAFA',
        'dropzone_border': '#E0E0E0',
        'dropzone_hover_bg': '#E3F2FD',
        'dropzone_hover_border': '#2196F3',
        'selected_bg': '#E8F5E9',
        'selected_border': '#4CAF50',
        'selected_text': '#2E7D32',
    }

    DARK = {
        'bg_primary': '#1E1E1E',
        'bg_secondary': '#252525',
        'bg_tertiary': '#2D2D2D',
        'text_primary': '#E0E0E0',
        'text_secondary': '#B0B0B0',
        'text_disabled': '#666666',
        'border': '#404040',
        'accent': '#42A5F5',
        'accent_hover': '#64B5F6',
        'success': '#66BB6A',
        'success_hover': '#81C784',
        'error': '#EF5350',
        'warning': '#FFA726',
        'info': '#42A5F5',
        'card_bg': '#252525',
        'card_border': '#404040',
        'input_bg': '#2D2D2D',
        'button_bg': '#303030',
        'button_text': '#E0E0E0',
        'dropzone_bg': '#2D2D2D',
        'dropzone_border': '#404040',
        'dropzone_hover_bg': '#1E3A5F',
        'dropzone_hover_border': '#42A5F5',
        'selected_bg': '#1B3A2F',
        'selected_border': '#66BB6A',
        'selected_text': '#81C784',
    }

    @staticmethod
    def get(key, is_dark=False):
        """Get theme color by key."""
        theme = Theme.DARK if is_dark else Theme.LIGHT
        return theme.get(key, '#000000')


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


class TranscriptionWorker(QThread):
    """Qt worker thread for transcription with proper signal handling."""

    # Signals for thread-safe communication
    progress_update = Signal(str, int)  # (message, percentage)
    transcription_complete = Signal(dict)  # result dictionary
    transcription_error = Signal(str)  # error message

    def __init__(self, video_path, model_size='tiny', language=None, detect_language_changes=False, use_deep_scan=False, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.model_size = model_size
        self.language = language
        self.detect_language_changes = detect_language_changes
        self.use_deep_scan = use_deep_scan

    def run(self):
        """Execute transcription in background thread."""
        try:
            from audio_extractor import AudioExtractor
            from transcriber import Transcriber
            from transcriber_enhanced import EnhancedTranscriber

            # Step 1: Extract audio from video if needed
            self.progress_update.emit("Extracting audio...", 10)

            extractor = AudioExtractor()
            audio_path = extractor.extract_audio(self.video_path)

            if not audio_path or not Path(audio_path).exists():
                self.transcription_error.emit("Failed to extract audio from video")
                return

            self.progress_update.emit(f"Audio extracted successfully", 30)

            # Step 2: Load and run transcription
            self.progress_update.emit(f"Loading Whisper model ({self.model_size})...", 40)

            # Use EnhancedTranscriber if language change detection is enabled
            if self.detect_language_changes:
                transcriber = EnhancedTranscriber(model_size=self.model_size)
            else:
                transcriber = Transcriber(model_size=self.model_size)

            # Define progress callback
            def progress_callback(message):
                # Update progress during transcription
                if "Starting" in message:
                    self.progress_update.emit(message, 50)
                elif "completed" in message.lower():
                    self.progress_update.emit(message, 90)
                else:
                    self.progress_update.emit(message, 70)

            # Transcribe
            if self.detect_language_changes:
                mode_desc = "deep scanning (segment-by-segment)" if self.use_deep_scan else "fast detection"
                self.progress_update.emit(f"Transcribing with multi-language {mode_desc}...", 60)
                result = transcriber.transcribe_multilang(
                    audio_path,
                    detect_language_changes=True,
                    use_segment_retranscription=self.use_deep_scan,
                    progress_callback=progress_callback
                )
            else:
                self.progress_update.emit("Transcribing audio...", 60)
                result = transcriber.transcribe(
                    audio_path,
                    language=self.language if self.language and self.language != "Auto-detect" else None,
                    progress_callback=progress_callback
                )

            self.progress_update.emit("Transcription complete!", 100)

            # Emit result
            self.transcription_complete.emit(result)

        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            self.transcription_error.emit(f"Transcription failed: {str(e)}")


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

    def __init__(self, title="", is_dark_mode=False):
        super().__init__()
        self.is_dark_mode = is_dark_mode
        self.title = title
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        if title:
            self.title_label = QLabel(title)
            layout.addWidget(self.title_label)
        else:
            self.title_label = None

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        self.setLayout(layout)
        self.update_theme(is_dark_mode)

    def update_theme(self, is_dark_mode):
        """Update card theme."""
        self.is_dark_mode = is_dark_mode
        self.setStyleSheet(f"""
            Card {{
                background-color: {Theme.get('card_bg', is_dark_mode)};
                border-radius: 12px;
                border: 1px solid {Theme.get('card_border', is_dark_mode)};
            }}
        """)

        if self.title_label:
            self.title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Theme.get('text_primary', is_dark_mode)};")


class DropZone(QFrame):
    """Drag and drop zone for files."""

    file_dropped = Signal(str)
    clicked = Signal()  # Signal emitted when user clicks the drop zone

    def __init__(self, is_dark_mode=False):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setMaximumHeight(200)
        self.has_file = False
        self.is_dark_mode = is_dark_mode
        self.setCursor(Qt.PointingHandCursor)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("🎬")
        self.icon_label.setStyleSheet("font-size: 48px;")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel("Drag & Drop Video/Audio\nFile Here")
        self.text_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)

        self.setLayout(self.layout)
        self.update_style()

    def set_theme(self, is_dark_mode):
        """Update theme colors."""
        self.is_dark_mode = is_dark_mode
        self.update_style()
        if not self.has_file:
            self.text_label.setStyleSheet(f"font-size: 16px; color: {Theme.get('text_secondary', self.is_dark_mode)}; font-weight: 500;")

    def update_style(self, hovering=False):
        if self.has_file:
            color = Theme.get('selected_border', self.is_dark_mode)
            bg = Theme.get('selected_bg', self.is_dark_mode)
        elif hovering:
            color = Theme.get('dropzone_hover_border', self.is_dark_mode)
            bg = Theme.get('dropzone_hover_bg', self.is_dark_mode)
        else:
            color = Theme.get('dropzone_border', self.is_dark_mode)
            bg = Theme.get('dropzone_bg', self.is_dark_mode)

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
        self.text_label.setText(f"Selected: {filename}")
        self.text_label.setStyleSheet(f"font-size: 14px; color: {Theme.get('selected_text', self.is_dark_mode)}; font-weight: 600;")
        self.update_style()

    def clear_file(self):
        self.has_file = False
        self.icon_label.setText("🎬")
        self.text_label.setText("Drag & Drop Video/Audio\nFile Here")
        self.text_label.setStyleSheet(f"font-size: 16px; color: {Theme.get('text_secondary', self.is_dark_mode)}; font-weight: 500;")
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
        info_card = Card(is_dark_mode=False)  # Dialog uses light mode
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
        self.transcription_worker = None  # QThread worker for transcription
        self.is_dark_mode = self.settings.get("dark_mode", False)

        self.setup_ui()
        self.apply_theme()
        self.center_window()

    def load_settings(self):
        """Load settings from config file."""
        default_settings = {
            "recordings_dir": str(Path.home() / "Video2Text" / "Recordings"),
            "dark_mode": False
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

    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.settings["dark_mode"] = self.is_dark_mode
        self.save_settings()
        self.apply_theme()

        # Update toggle button text
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.setText("☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode")

        logger.info(f"Theme switched to {'dark' if self.is_dark_mode else 'light'} mode")

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

    def update_all_cards_theme(self):
        """Update theme for all Card widgets."""
        for widget in self.findChildren(Card):
            widget.update_theme(self.is_dark_mode)

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
        """Create application header."""
        header = QWidget()
        layout = QHBoxLayout()

        # Title and subtitle
        self.title_label = QLabel("🎬 Video2Text")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")

        self.subtitle_label = QLabel("AI-Powered Transcription with Whisper")
        self.subtitle_label.setStyleSheet("font-size: 14px; color: #666;")

        title_layout = QVBoxLayout()
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        title_layout.setSpacing(5)

        layout.addLayout(title_layout)
        layout.addStretch()

        # Theme toggle button
        self.theme_toggle_btn = QPushButton("🌙 Dark Mode" if not self.is_dark_mode else "☀️ Light Mode")
        self.theme_toggle_btn.setMinimumWidth(120)
        self.theme_toggle_btn.setMinimumHeight(35)
        self.theme_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_toggle_btn)

        header.setLayout(layout)
        return header

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

        # Title
        title = QLabel("📁 Upload File")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Theme.get('text_primary', self.is_dark_mode)};")
        layout.addWidget(title)

        # Description
        desc = QLabel("Drop a video/audio file or click to browse")
        desc.setStyleSheet(f"font-size: 14px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(desc)

        # Drop zone
        self.drop_zone = DropZone(self.is_dark_mode)
        self.drop_zone.file_dropped.connect(self.on_file_dropped_basic)
        self.drop_zone.clicked.connect(self.browse_file)
        layout.addWidget(self.drop_zone)

        # Settings Card
        settings_card = Card("⚙️ Transcription Settings", self.is_dark_mode)

        # Model selector
        model_label = QLabel("Whisper Model:")
        model_label.setStyleSheet(f"font-weight: bold; color: {Theme.get('text_primary', self.is_dark_mode)};")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText("large")  # Default to large for better multi-language
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {Theme.get('border', self.is_dark_mode)};
                border-radius: 6px;
                background-color: {Theme.get('input_bg', self.is_dark_mode)};
                color: {Theme.get('text_primary', self.is_dark_mode)};
            }}
        """)

        model_info = QLabel("ℹ️ Larger models are more accurate for multi-language.\n💡 'large' recommended for code-switching (Czech ↔ English)")
        model_info.setWordWrap(True)
        model_info.setStyleSheet(f"color: {Theme.get('text_secondary', self.is_dark_mode)}; font-size: 11px; padding: 5px;")

        settings_card.content_layout.addWidget(model_label)
        settings_card.content_layout.addWidget(self.model_combo)
        settings_card.content_layout.addWidget(model_info)

        # Deep scanning checkbox
        self.deep_scan_check = QCheckBox("🔬 Deep multi-language scanning (segment-by-segment)")
        self.deep_scan_check.setChecked(True)  # Default enabled for TRUE multi-language support
        self.deep_scan_check.setStyleSheet(f"color: {Theme.get('text_primary', self.is_dark_mode)}; padding: 5px; font-weight: bold;")

        deep_info = QLabel("✅ Enabled: Re-transcribes each segment for accurate language detection.\n"
                          "Perfect for code-switching (Czech → English → Czech).\n"
                          "⏱️ Slower but handles language mixing correctly.")
        deep_info.setWordWrap(True)
        deep_info.setStyleSheet(f"color: {Theme.get('info', self.is_dark_mode)}; font-size: 11px; padding: 5px;")

        settings_card.content_layout.addWidget(self.deep_scan_check)
        settings_card.content_layout.addWidget(deep_info)

        layout.addWidget(settings_card)

        # Progress section
        self.basic_upload_progress_label = QLabel("Ready to transcribe")
        self.basic_upload_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_upload_progress_label)

        self.basic_upload_progress_bar = QProgressBar()
        self.basic_upload_progress_bar.setMinimumHeight(25)
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

        # Title
        title = QLabel("🎙️ Record Audio")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Theme.get('text_primary', self.is_dark_mode)};")
        layout.addWidget(title)

        # Description
        desc = QLabel("Record audio from microphone and system speaker")
        desc.setStyleSheet(f"font-size: 14px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(desc)

        # Recording button container
        record_container = QFrame()
        record_container.setMinimumHeight(200)
        record_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                border-radius: 12px;
                border: 2px solid {Theme.get('border', self.is_dark_mode)};
            }}
        """)
        record_layout = QVBoxLayout(record_container)
        record_layout.setAlignment(Qt.AlignCenter)

        # Record icon
        record_icon = QLabel("🎙️")
        record_icon.setStyleSheet("font-size: 64px;")
        record_icon.setAlignment(Qt.AlignCenter)
        record_layout.addWidget(record_icon)

        # Record toggle button
        self.basic_record_btn = ModernButton("🎤 Start Recording", primary=True)
        self.basic_record_btn.setMinimumHeight(50)
        self.basic_record_btn.setMinimumWidth(220)
        self.basic_record_btn.clicked.connect(self.toggle_basic_recording)
        record_layout.addWidget(self.basic_record_btn, 0, Qt.AlignCenter)

        layout.addWidget(record_container)

        # Recording duration (shown during recording, hidden otherwise)
        self.recording_duration_label = QLabel("Duration: 0:00")
        self.recording_duration_label.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {Theme.get('error', self.is_dark_mode)};"
        )
        self.recording_duration_label.setAlignment(Qt.AlignCenter)
        self.recording_duration_label.hide()
        layout.addWidget(self.recording_duration_label)

        # Progress section
        self.basic_record_progress_label = QLabel("Ready to record")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_record_progress_label)

        self.basic_record_progress_bar = QProgressBar()
        self.basic_record_progress_bar.setMinimumHeight(25)
        layout.addWidget(self.basic_record_progress_bar)

        # Settings card
        settings_card = self.create_settings_card()
        layout.addWidget(settings_card)

        # Info tip
        info = QLabel("💡 Recording automatically transcribes when stopped")
        info.setStyleSheet(f"font-size: 12px; color: {Theme.get('info', self.is_dark_mode)};")
        layout.addWidget(info)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_basic_transcript_tab(self):
        """Create Transcript tab for Basic mode."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("📄 Transcription Result")
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Theme.get('text_primary', self.is_dark_mode)};")
        layout.addWidget(title)

        # Description
        self.basic_transcript_desc = QLabel("Your transcription will appear here")
        self.basic_transcript_desc.setStyleSheet(f"font-size: 14px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        layout.addWidget(self.basic_transcript_desc)

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

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.basic_save_btn = ModernButton("💾 Save Transcription", primary=True)
        self.basic_save_btn.setEnabled(False)
        self.basic_save_btn.clicked.connect(self.save_transcription)

        self.basic_clear_btn = ModernButton("🔄 New Transcription", primary=False)
        self.basic_clear_btn.setEnabled(False)
        self.basic_clear_btn.clicked.connect(self.clear_for_new_transcription)

        button_layout.addWidget(self.basic_save_btn)
        button_layout.addWidget(self.basic_clear_btn)
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def on_file_dropped_basic(self, file_path):
        """Handle file drop - auto-start transcription."""
        self.load_file(file_path)
        # Auto-start transcription
        # Small delay to let UI update
        QTimer.singleShot(100, self.start_transcription)

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
            # Auto-start transcription
            QTimer.singleShot(100, self.start_transcription)

    def load_file(self, file_path):
        """Load a video or audio file."""
        self.video_path = file_path
        filename = Path(file_path).name

        # Update UI
        self.drop_zone.set_file(filename)
        # Auto-transcribes when file is loaded

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

        # Disable drop zone during recording
        self.drop_zone.setEnabled(False)

        # Show duration label
        self.recording_duration_label.show()
        self.recording_timer.start(1000)  # Update every second

        # Update status
        self.statusBar().showMessage("🔴 Recording from Microphone + Speaker...")
        self.basic_record_progress_label.setText("Recording in progress...")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('error', self.is_dark_mode)}; font-weight: bold;")

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

    def on_recording_complete(self, recorded_path, duration):
        """Slot called when recording completes successfully (thread-safe)."""
        # Load file and update UI
        self.video_path = recorded_path
        self.statusBar().showMessage(f"✅ Recording complete ({duration:.1f}s) - Starting transcription...")

        # Re-enable controls
        self.drop_zone.setEnabled(True)

        # Update progress label
        self.basic_record_progress_label.setText(f"Recording complete ({duration:.1f}s) - Starting transcription...")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('success', self.is_dark_mode)};")

        # Auto-start transcription
        QTimer.singleShot(500, self.start_transcription)

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

        # Disable buttons and clear results
        self.basic_save_btn.setEnabled(False)
        self.basic_clear_btn.setEnabled(False)
        self.basic_result_text.clear()
        self.basic_upload_progress_bar.setValue(0)
        self.basic_record_progress_bar.setValue(0)

        # Get transcription settings from UI
        model_size = self.model_combo.currentText()  # User-selected model (default: large)
        language = None  # Always auto-detect for multi-language
        detect_language_changes = True  # Always enabled for multi-language support
        use_deep_scan = self.deep_scan_check.isChecked()  # User can toggle (default: True)

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

        # Connect signals
        self.transcription_worker.progress_update.connect(self.on_transcription_progress)
        self.transcription_worker.transcription_complete.connect(self.on_transcription_complete)
        self.transcription_worker.transcription_error.connect(self.on_transcription_error)

        # Start worker
        self.transcription_worker.start()

        logger.info(f"Started transcription: {self.video_path}, model={model_size}, language={language}, multi-lang={detect_language_changes}, deep-scan={use_deep_scan}")

    def on_transcription_progress(self, message, percentage):
        """Handle transcription progress updates."""
        # Update progress bars
        self.basic_upload_progress_label.setText(message)
        self.basic_upload_progress_bar.setValue(percentage)
        self.basic_record_progress_label.setText(message)
        self.basic_record_progress_bar.setValue(percentage)

        self.statusBar().showMessage(message)

    def on_transcription_complete(self, result):
        """Handle successful transcription completion."""
        from transcriber_enhanced import EnhancedTranscriber

        self.transcription_result = result

        # Display result
        text = result.get('text', '')
        language = result.get('language', 'unknown')
        segment_count = len(result.get('segments', []))

        # Get language name
        lang_name = EnhancedTranscriber.LANGUAGE_NAMES.get(language, language.upper())

        # Check for multi-language information
        language_timeline = result.get('language_timeline', '')
        language_segments = result.get('language_segments', [])
        has_multilang = bool(language_timeline or language_segments)

        # Prepare display text
        display_text = text
        if has_multilang and language_timeline:
            # Add language timeline to the displayed text
            display_text = f"{text}\n\n{'='*60}\n🌍 LANGUAGE TIMELINE:\n{'='*60}\n\n{language_timeline}"

            # Count unique languages and show their names
            unique_langs = set(seg.get('language', 'unknown') for seg in language_segments)
            lang_names = [EnhancedTranscriber.LANGUAGE_NAMES.get(code, code.upper()) for code in sorted(unique_langs)]
            lang_info = f"Languages detected: {', '.join(lang_names)}"
        else:
            lang_info = f"Language: {lang_name}"

        # Update UI
        self.basic_result_text.setPlainText(display_text)
        self.basic_save_btn.setEnabled(True)
        self.basic_clear_btn.setEnabled(True)

        if has_multilang:
            self.basic_transcript_desc.setText(f"{lang_info} | {segment_count} segments")
        else:
            self.basic_transcript_desc.setText(f"Language: {lang_name} | {segment_count} segments")

        # Auto-navigate to Transcript tab (index 2)
        self.basic_sidebar.setCurrentRow(2)
        self.basic_tab_stack.setCurrentIndex(2)

        # Update progress bars
        self.basic_upload_progress_label.setText(f"✅ Complete! {lang_info}")
        self.basic_upload_progress_bar.setValue(100)
        self.basic_record_progress_label.setText(f"✅ Complete! {lang_info}")
        self.basic_record_progress_bar.setValue(100)

        status_msg = f"Transcription complete ({segment_count} segments, {lang_info})"
        self.statusBar().showMessage(status_msg)

        if has_multilang:
            logger.info(f"Multi-language transcription complete: {len(language_segments)} language segments detected")
        logger.info(f"Transcription complete: {len(text)} characters, {segment_count} segments")

    def on_transcription_error(self, error_message):
        """Handle transcription error."""
        # Update UI
        self.basic_upload_progress_label.setText(f"❌ Error: {error_message}")
        self.basic_record_progress_label.setText(f"❌ Error: {error_message}")

        self.statusBar().showMessage("Transcription failed")

        QMessageBox.critical(
            self,
            "Transcription Error",
            f"Transcription failed:\n\n{error_message}\n\nPlease check the logs for more details."
        )

        logger.error(f"Transcription failed: {error_message}")

    def save_transcription(self):
        """Save transcription to file."""
        if not self.transcription_result:
            QMessageBox.warning(self, "No Transcription", "Please transcribe a file first.")
            return

        # Determine default filename and filter
        if self.video_path:
            default_name = Path(self.video_path).stem
        else:
            default_name = "transcription"

        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Transcription",
            default_name,
            "Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)"
        )

        if not file_path:
            return

        try:
            # Determine format from extension or filter
            ext = Path(file_path).suffix.lower()

            if ext == '.txt' or 'Text' in selected_filter:
                # Save as plain text
                content = self.transcription_result.get('text', '')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            elif ext == '.srt' or 'SRT' in selected_filter:
                # Save as SRT subtitles
                from transcriber import Transcriber
                transcriber = Transcriber()
                content = transcriber.format_as_srt(self.transcription_result)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            elif ext == '.vtt' or 'VTT' in selected_filter:
                # Save as VTT subtitles (similar to SRT but with VTT header)
                from transcriber import Transcriber
                transcriber = Transcriber()
                srt_content = transcriber.format_as_srt(self.transcription_result)
                # Convert SRT to VTT format
                vtt_content = "WEBVTT\n\n" + srt_content.replace(',', '.')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(vtt_content)

            else:
                # Default to text
                content = self.transcription_result.get('text', '')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            self.statusBar().showMessage(f"Saved to: {file_path}")
            QMessageBox.information(
                self,
                "Saved Successfully",
                f"Transcription saved to:\n{file_path}"
            )
            logger.info(f"Transcription saved to: {file_path}")

        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save transcription:\n\n{str(e)}"
            )

    def clear_for_new_transcription(self):
        """Clear current transcription and reset UI for a new transcription."""
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "New Transcription",
            "Start a new transcription? This will clear the current results.\n\n"
            "(Make sure you've saved your transcription if needed!)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Clear state
        self.video_path = None
        self.transcription_result = None

        # Reset UI
        self.basic_result_text.clear()
        self.basic_save_btn.setEnabled(False)
        self.basic_clear_btn.setEnabled(False)
        self.basic_transcript_desc.setText("Your transcription will appear here")
        self.basic_upload_progress_label.setText("Ready to transcribe")
        self.basic_upload_progress_bar.setValue(0)
        self.basic_record_progress_label.setText("Ready to transcribe")
        self.basic_record_progress_bar.setValue(0)

        # Clear drop zone
        if hasattr(self, 'drop_zone'):
            self.drop_zone.clear_file()

        # Navigate back to Upload tab (index 1)
        self.basic_sidebar.setCurrentRow(1)
        self.basic_tab_stack.setCurrentIndex(1)

        self.statusBar().showMessage("Ready for new transcription")
        logger.info("Cleared for new transcription")


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
