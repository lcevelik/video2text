"""
Dialog windows for the GUI.
"""

import logging
import time
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QWidget, QCheckBox, QGridLayout
)
from PySide6.QtCore import Qt, QTimer

from gui.widgets import ModernButton, Card
from gui.workers import RecordingWorker, AudioLevelMonitor
from gui.utils import check_audio_input_devices
from gui.vu_meter import VUMeter

logger = logging.getLogger(__name__)


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
        self.monitor = None  # QThread worker for audio level monitoring

        self.setup_ui()
        self.start_monitoring()  # Start monitoring audio levels immediately

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

        # Audio Level Meters label
        meters_label = QLabel("🎚️ Audio Level Monitoring")
        meters_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #555;")
        layout.addWidget(meters_label)

        # VU Meters (always visible for monitoring)
        self.vu_meters_widget = QWidget()
        self.vu_meters_widget.setMinimumHeight(100)  # Ensure widget has height
        self.vu_meters_widget.setStyleSheet("QWidget { background-color: #e8f5e9; border: 3px solid #4CAF50; border-radius: 4px; padding: 8px; }")
        vu_meters_layout = QVBoxLayout(self.vu_meters_widget)
        vu_meters_layout.setSpacing(10)
        vu_meters_layout.setContentsMargins(5, 5, 5, 5)

        self.mic_vu_meter = VUMeter("🎤 Microphone")
        self.speaker_vu_meter = VUMeter("🔊 Speaker/System")

        # DEBUG: Set initial test level to make meters visible
        self.mic_vu_meter.set_level(0.3)
        self.speaker_vu_meter.set_level(0.2)

        vu_meters_layout.addWidget(self.mic_vu_meter)
        vu_meters_layout.addWidget(self.speaker_vu_meter)

        # VU meters are now always visible for live monitoring
        self.vu_meters_widget.setVisible(True)  # Explicitly show the widget
        self.vu_meters_widget.show()  # Double-ensure visibility
        layout.addWidget(self.vu_meters_widget)

        # DEBUG: Log VU meter widget state
        logger.info(f"VU meters widget created: visible={self.vu_meters_widget.isVisible()}, size={self.vu_meters_widget.size()}")
        logger.info(f"Mic VU meter: visible={self.mic_vu_meter.isVisible()}, size={self.mic_vu_meter.size()}")
        logger.info(f"Speaker VU meter: visible={self.speaker_vu_meter.isVisible()}, size={self.speaker_vu_meter.size()}")

        # User-selected language mode (None until chosen via dialog)
        self.multi_language_mode = None
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

    def start_monitoring(self):
        """Start audio level monitoring (runs before and after recording)."""
        if self.monitor is not None:
            # Already monitoring
            return

        try:
            self.monitor = AudioLevelMonitor(parent=self)
            self.monitor.audio_level.connect(self.update_audio_levels)
            self.monitor.start()
            logger.info("Audio level monitoring started")
        except Exception as e:
            logger.warning(f"Failed to start audio monitoring: {e}")

    def stop_monitoring(self):
        """Stop audio level monitoring."""
        if self.monitor:
            self.monitor.stop()
            self.monitor.wait(1000)  # Wait up to 1 second for thread to finish
            self.monitor = None
            logger.info("Audio level monitoring stopped")

    def closeEvent(self, event):
        """Handle dialog close - clean up monitoring."""
        self.stop_monitoring()
        if self.worker:
            self.worker.stop()
            self.worker.wait(2000)
        super().closeEvent(event)

    def start_recording(self):
        # Check device availability first
        if not self.check_audio_devices():
            # Show helpful message with retry option
            self.show_no_device_dialog()
            return

        # Stop monitoring while recording (recording worker will provide levels)
        self.stop_monitoring()

        self.recording = True
        self.start_time = time.time()
        self.status_label.setText("🔴 Recording from Microphone + Speaker...")
        self.status_label.setStyleSheet("font-size: 14px; color: #F44336; font-weight: bold;")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.timer.start(1000)

        # Start actual recording in QThread worker
        # Get recordings directory from parent window
        recordings_dir = self.parent().settings["recordings_dir"] if hasattr(self.parent(), 'settings') else str(Path.home() / "FonixFlow" / "Recordings")
        self.worker = RecordingWorker(recordings_dir, self)
        self.worker.recording_complete.connect(self.on_recording_complete)
        self.worker.recording_error.connect(self.on_recording_error)
        self.worker.audio_level.connect(self.update_audio_levels)
        self.worker.start()

        # Reset VU meters for new recording
        self.mic_vu_meter.reset()
        self.speaker_vu_meter.reset()

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

        # Resume monitoring after recording stops
        self.start_monitoring()

    def update_duration(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            self.duration_label.setText(f"Duration: {mins}:{secs:02d}")

    def update_audio_levels(self, mic_level, speaker_level):
        """Update VU meters with current audio levels (thread-safe slot)."""
        self.mic_vu_meter.set_level(mic_level)
        self.speaker_vu_meter.set_level(speaker_level)

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


class MultiLanguageChoiceDialog(QDialog):
    """Dialog asking whether audio contains multiple languages (code switching) and optional language selection."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Language Mode")
        self.setModal(True)
        self.is_multi_language = False
        self.selected_languages: List[str] = []
        self.setMinimumWidth(520)

        layout = QVBoxLayout()
        title = QLabel("Is your file multi-language?")
        title.setStyleSheet("font-size:16px; font-weight:bold;")
        layout.addWidget(title)


        # Language selection area (hidden until user chooses multi-language)
        self.lang_select_widget = QWidget()
        self.lang_select_layout = QVBoxLayout(self.lang_select_widget)
        self.lang_select_widget.setVisible(False)
        lang_label = QLabel("Select languages present (check all that apply):")
        lang_label.setStyleSheet("font-weight:bold; margin-top:8px;")
        self.lang_select_layout.addWidget(lang_label)
        # Expanded allow-list (can be extended further)
        self.available_languages = [
            ('en','English'), ('cs','Czech'), ('de','German'), ('fr','French'), ('es','Spanish'), ('it','Italian'),
            ('pl','Polish'), ('ru','Russian'), ('zh','Chinese'), ('ja','Japanese'), ('ko','Korean'), ('ar','Arabic')
        ]
        grid = QGridLayout()
        self.lang_checkboxes: List[QCheckBox] = []
        for idx,(code,name) in enumerate(self.available_languages):
            cb = QCheckBox(name)
            cb.lang_code = code
            if code in ('en','es'):  # common pair default
                cb.setChecked(True)
            self.lang_checkboxes.append(cb)
            grid.addWidget(cb, idx//3, idx%3)
        self.lang_select_layout.addLayout(grid)
        hint = QLabel("At least one language must be selected before confirming.")
        hint.setStyleSheet("font-size:11px; color:#666;")
        self.lang_select_layout.addWidget(hint)
        layout.addWidget(self.lang_select_widget)

        btn_row = QHBoxLayout()
        self.yes_btn = QPushButton("Multi-Language")
        self.no_btn = QPushButton("Single-Language")
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.no_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.setStyleSheet("background:#2196F3; color:white; padding:10px; border-radius:6px; font-weight:bold;")
        self.no_btn.setStyleSheet("background:#4CAF50; color:white; padding:10px; border-radius:6px; font-weight:bold;")
        btn_row.addWidget(self.yes_btn)
        btn_row.addWidget(self.no_btn)
        layout.addLayout(btn_row)

        info = QLabel("Cancel to decide later.")
        info.setStyleSheet("font-size:12px; color:#888;")
        layout.addWidget(info)

        self.setLayout(layout)
        self.yes_btn.clicked.connect(self.choose_multi)
        self.no_btn.clicked.connect(self.choose_single)

    def choose_multi(self):
        # First click reveals language selection; second confirms
        if not self.lang_select_widget.isVisible():
            self.is_multi_language = True
            self.lang_select_widget.setVisible(True)
            self.yes_btn.setText("Confirm Languages")
            return
        # Confirm selection
        chosen = [cb.lang_code for cb in self.lang_checkboxes if cb.isChecked()]
        if not chosen:
            QMessageBox.warning(self, "No Languages Selected", "Select at least one language to proceed.")
            return
        self.selected_languages = chosen
        self.accept()

    def choose_single(self):
        # Single-language choice; dialog only reports selection back to parent.
        self.is_multi_language = False
        self.selected_languages = []
        self.accept()

