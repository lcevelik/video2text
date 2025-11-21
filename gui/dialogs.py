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
from gui.workers import RecordingWorker
from gui.utils import check_audio_input_devices
from gui.vu_meter import VUMeter
from gui.icons import get_icon

logger = logging.getLogger(__name__)

# Helper function to set icon with proper sizing
def set_icon(widget, icon_name, size=29):
    """Set icon on a widget with proper size."""
    from PySide6.QtCore import QSize
    widget.setIcon(get_icon(icon_name))
    widget.setIconSize(QSize(size, size))


class RecordingDialog(QDialog):
    """Modern recording dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Audio Recording"))
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
        title = QLabel(self.tr("Audio Recording"))
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Info card
        info_card = Card(self.tr("Audio Recording"), is_dark_mode=False)  # Dialog uses light mode
        info_card.content_layout.addWidget(QLabel(self.tr("What will be recorded:")))
        info_card.content_layout.addWidget(QLabel(self.tr("Microphone: Your voice and ambient sounds")))
        info_card.content_layout.addWidget(QLabel(self.tr("Speaker: System audio, music, video calls")))
        info_card.content_layout.addWidget(QLabel(self.tr("Both sources mixed into one recording")))
        layout.addWidget(info_card)

        # Status
        self.status_label = QLabel(self.tr("Ready to record"))
        self.status_label.setStyleSheet("font-size: 14px; color: #666;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # VU Meters (shown during recording)
        self.vu_meters_widget = QWidget()
        vu_meters_layout = QVBoxLayout(self.vu_meters_widget)
        vu_meters_layout.setSpacing(10)

        self.mic_vu_meter = VUMeter(self.tr("Microphone"))
        self.speaker_vu_meter = VUMeter(self.tr("Speaker/System"))

        vu_meters_layout.addWidget(self.mic_vu_meter)
        vu_meters_layout.addWidget(self.speaker_vu_meter)

        self.vu_meters_widget.hide()
        layout.addWidget(self.vu_meters_widget)

        # User-selected language mode (None until chosen via dialog)
        self.multi_language_mode = None
        # Duration
        self.duration_label = QLabel(self.tr("Duration: 0:00"))
        self.duration_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0FD2CC;")
        self.duration_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.duration_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = ModernButton(self.tr("Start Recording"), primary=True)
        set_icon(self.start_btn, 'circle')
        self.stop_btn = ModernButton(self.tr("Stop Recording"))
        set_icon(self.stop_btn, 'stop-circle')
        self.stop_btn.setEnabled(False)
        close_btn = ModernButton(self.tr("Close"))

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        close_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        # Tip
        tip = QLabel(self.tr("ℹ️ Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured."))
        tip.setStyleSheet("font-size: 11px; color: #999;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)

        layout.addStretch()
        self.setLayout(layout)

        # Timer for duration update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_duration)

    def start_recording(self):
        with open("debug_dialog_button_click.txt", "a") as f:
            import datetime
            f.write(f"{datetime.datetime.now()}: DIALOG BUTTON CLICKED!\n")
        # Check device availability first
        if not self.check_audio_devices():
            # Show helpful message with retry option
            self.show_no_device_dialog()
            return

        self.recording = True
        self.start_time = time.time()
        self.status_label.setText("Recording from Microphone + Speaker...")
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

        # Show VU meters
        self.vu_meters_widget.show()
        self.mic_vu_meter.reset()
        self.speaker_vu_meter.reset()

    def stop_recording(self):
        self.recording = False

        # Stop the worker thread
        if self.worker:
            self.worker.stop()

        self.status_label.setText(self.tr("Stopping recording..."))
        self.status_label.setStyleSheet("font-size: 14px; color: #FF9800;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.timer.stop()

        # Hide VU meters
        self.vu_meters_widget.hide()

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
            logger.info("User requested device detection retry (Advanced Mode)")
            if self.check_audio_devices():
                QMessageBox.information(
                    self,
                    self.tr("Device Found"),
                    self.tr("✅ Audio input device detected!\n\nYou can now start recording.")
                )
                # Automatically start recording
                self.start_recording()
            else:
                # Still no device - show dialog again
                self.show_no_device_dialog()

    def on_recording_complete(self, recorded_path, duration):
        """Slot called when recording completes successfully (thread-safe)."""
        self.recorded_path = recorded_path
        self.status_label.setText(f"Recording complete ({duration:.1f}s)")
        self.status_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_recording_error(self, error_message):
        """Slot called when recording encounters an error (thread-safe)."""
        self.status_label.setText(f"Error: {error_message}")
        self.status_label.setStyleSheet("font-size: 14px; color: #F44336;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.recording = False
        self.timer.stop()


class MultiLanguageChoiceDialog(QDialog):
    """Dialog asking whether audio contains multiple languages (code switching) and optional language selection."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Language Mode"))
        self.setModal(True)
        self.is_multi_language = False
        self.selected_languages: List[str] = []
        self.single_language_type = None  # 'english' or 'other'
        self.setMinimumWidth(520)

        layout = QVBoxLayout()
        title = QLabel(self.tr("Is your file multi-language?"))
        title.setStyleSheet("font-size:16px; font-weight:bold;")
        layout.addWidget(title)

        # Single-language selection area (hidden until user chooses single-language)
        self.single_lang_select_widget = QWidget()
        self.single_lang_select_layout = QVBoxLayout(self.single_lang_select_widget)
        self.single_lang_select_widget.setVisible(False)
        single_lang_label = QLabel(self.tr("Select language type:"))
        single_lang_label.setStyleSheet("font-weight:bold; margin-top:8px;")
        self.single_lang_select_layout.addWidget(single_lang_label)

        # English checkbox
        self.english_checkbox = QCheckBox(self.tr("English (uses optimized .en model)"))
        self.english_checkbox.setChecked(True)
        self.single_lang_select_layout.addWidget(self.english_checkbox)

        # Other checkbox
        self.other_checkbox = QCheckBox(self.tr("Other language (uses multilingual model)"))
        self.single_lang_select_layout.addWidget(self.other_checkbox)

        # Make checkboxes mutually exclusive
        self.english_checkbox.stateChanged.connect(lambda state: self.other_checkbox.setChecked(False) if state else None)
        self.other_checkbox.stateChanged.connect(lambda state: self.english_checkbox.setChecked(False) if state else None)

        single_hint = QLabel(self.tr("Select one language type before confirming."))
        single_hint.setStyleSheet("font-size:11px; color:#666;")
        self.single_lang_select_layout.addWidget(single_hint)
        layout.addWidget(self.single_lang_select_widget)

        # Multi-language selection area (hidden until user chooses multi-language)
        self.lang_select_widget = QWidget()
        self.lang_select_layout = QVBoxLayout(self.lang_select_widget)
        self.lang_select_widget.setVisible(False)
        lang_label = QLabel(self.tr("Select languages present (check all that apply):"))
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
            cb = QCheckBox(self.tr(name))  # Translate language name
            cb.lang_code = code
            if code in ('en','es'):  # common pair default
                cb.setChecked(True)
            self.lang_checkboxes.append(cb)
            grid.addWidget(cb, idx//3, idx%3)
        self.lang_select_layout.addLayout(grid)
        hint = QLabel(self.tr("At least one language must be selected before confirming."))
        hint.setStyleSheet("font-size:11px; color:#666;")
        self.lang_select_layout.addWidget(hint)
        layout.addWidget(self.lang_select_widget)

        btn_row = QHBoxLayout()
        self.yes_btn = QPushButton(self.tr("Multi-Language"))
        self.no_btn = QPushButton(self.tr("Single-Language"))
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.no_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FD2CC;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #0CBFB3;
            }
            QPushButton:pressed {
                background-color: #0AA99E;
            }
        """)
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        btn_row.addWidget(self.yes_btn)
        btn_row.addWidget(self.no_btn)
        layout.addLayout(btn_row)

        info = QLabel(self.tr("Cancel to decide later."))
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
            self.single_lang_select_widget.setVisible(False)  # Hide single-language options
            self.yes_btn.setText(self.tr("Confirm Languages"))
            return
        # Confirm selection
        chosen = [cb.lang_code for cb in self.lang_checkboxes if cb.isChecked()]
        if not chosen:
            QMessageBox.warning(self, self.tr("No Languages Selected"), self.tr("Select at least one language to proceed."))
            return
        self.selected_languages = chosen
        self.accept()

    def choose_single(self):
        # First click reveals language type selection; second confirms
        if not self.single_lang_select_widget.isVisible():
            self.is_multi_language = False
            self.single_lang_select_widget.setVisible(True)
            self.lang_select_widget.setVisible(False)  # Hide multi-language options
            self.no_btn.setText(self.tr("Confirm Selection"))
            return
        # Confirm selection
        if not self.english_checkbox.isChecked() and not self.other_checkbox.isChecked():
            QMessageBox.warning(self, self.tr("No Language Type Selected"), self.tr("Please select either English or Other language."))
            return

        # Determine which type was selected
        if self.english_checkbox.isChecked():
            self.single_language_type = 'english'
        else:
            self.single_language_type = 'other'

        self.selected_languages = []
        self.accept()

