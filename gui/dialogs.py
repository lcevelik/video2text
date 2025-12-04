import webbrowser
import requests
import platform
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout, 
    QApplication, QScrollArea, QWidget, QFileDialog, QMessageBox
)
from PySide6.QtGui import QTextCursor, QPixmap
from PySide6.QtCore import Qt
class LicenseKeyDialog(QDialog):
    """Dialog for entering and validating LemonSqueezy license key."""
    def __init__(self, parent=None, current_key=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Enter License Key"))
        self.setMinimumSize(400, 180)
        # Ensure dialog appears on top of splash screen
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.license_key = current_key
        self.valid = False
        self.current_key = current_key
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel(self.tr("Please enter your FonixFlow license key to enable transcription."))
        label.setWordWrap(True)
        layout.addWidget(label)

        self.key_input = QTextEdit()
        self.key_input.setPlaceholderText(self.tr("Paste your license key here"))
        self.key_input.setFixedHeight(40)

        # Pre-fill with current key if available
        if self.current_key:
            self.key_input.setPlainText(self.current_key)

        layout.addWidget(self.key_input)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #c00; font-size: 13px;")
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton(self.tr("Activate"))
        self.save_btn.clicked.connect(self.validate_and_save)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton(self.tr("Cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.buy_btn = QPushButton(self.tr("Buy License"))
        self.buy_btn.clicked.connect(lambda: webbrowser.open("https://fonixflow.com/#/pricing"))
        self.buy_btn.hide()
        btn_layout.addWidget(self.buy_btn)

        layout.addLayout(btn_layout)

    def validate_and_save(self):
        key = self.key_input.toPlainText().strip()
        if not key:
            self.status_label.setText(self.tr("License key cannot be empty."))
            self.status_label.setStyleSheet("color: #c00; font-size: 13px;")
            return
        self.status_label.setText(self.tr("Validating license key..."))
        self.status_label.setStyleSheet("color: #666; font-size: 13px;")
        QApplication.processEvents()
        # First, check local license files (encoded or plaintext)
        try:
            from pathlib import Path
            import base64

            valid_keys = []

            # Check encoded file first (used in distributed builds)
            license_file_encoded = Path(__file__).parent.parent / "licenses.dat"
            if license_file_encoded.exists():
                try:
                    with open(license_file_encoded, 'rb') as f:
                        encoded = f.read()
                    xor_bytes = base64.b64decode(encoded)
                    decode_key = b'FonixFlow2024VideoTranscription'
                    content_bytes = bytearray()
                    for i, byte in enumerate(xor_bytes):
                        content_bytes.append(byte ^ decode_key[i % len(decode_key)])
                    content = bytes(content_bytes).decode('utf-8')
                    valid_keys = [line.strip() for line in content.split('\n') if line.strip()]
                except Exception as e:
                    # If encoded file fails, try plaintext below
                    pass

            # Fall back to plaintext file (for development)
            if not valid_keys:
                license_file_plain = Path(__file__).parent.parent / "licenses.txt"
                if license_file_plain.exists():
                    with open(license_file_plain, "r") as f:
                        valid_keys = [line.strip() for line in f if line.strip()]

            # Check if key is valid
            if valid_keys and key in valid_keys:
                self.license_key = key
                self.valid = True
                self.status_label.setText(self.tr("✓ License key validated successfully! Saving..."))
                self.status_label.setStyleSheet("color: #4CAF50; font-size: 13px; font-weight: bold;")
                QApplication.processEvents()
                self.accept()
                return
        except Exception as e:
            self.status_label.setText(self.tr(f"Error reading local license file: {e}"))
            self.status_label.setStyleSheet("color: #c00; font-size: 13px;")
            self.buy_btn.show()
            return
        # If not found locally, check LemonSqueezy API
        try:
            url = "https://api.lemonsqueezy.com/v1/licenses/validate"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"license_key": key}
            resp = requests.post(url, headers=headers, data=data, timeout=10)
            result = resp.json()
            if result.get("status") == "active":
                self.license_key = key
                self.valid = True
                self.status_label.setText(self.tr("✓ License key validated successfully! Saving..."))
                self.status_label.setStyleSheet("color: #4CAF50; font-size: 13px; font-weight: bold;")
                QApplication.processEvents()
                self.accept()
            else:
                self.status_label.setText(self.tr("Invalid or inactive license key. Please check or purchase a valid license."))
                self.status_label.setStyleSheet("color: #c00; font-size: 13px;")
                self.buy_btn.show()
        except Exception as e:
            self.status_label.setText(self.tr(f"Error validating license: {e}"))
            self.status_label.setStyleSheet("color: #c00; font-size: 13px;")
            self.buy_btn.show()
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
        from gui.managers.path_manager import PathManager
        default_recordings = str(PathManager.get_recordings_dir())
        recordings_dir = self.parent().settings["recordings_dir"] if hasattr(self.parent(), 'settings') else default_recordings
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


class LogsDialog(QDialog):
    """Dialog for viewing and managing application logs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Application Logs"))
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_logs()
    
    def setup_ui(self):
        from gui.managers.log_manager import LogManager
        
        layout = QVBoxLayout(self)
        
        # Header with log file info
        info_layout = QHBoxLayout()
        log_info = LogManager.get_log_info()
        session_timestamp = LogManager.get_session_timestamp()
        info_label = QLabel(
            self.tr(f"Session: {session_timestamp}\n"
                   f"Log file: {log_info['path']}\n"
                   f"Size: {log_info['size_mb']} MB")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 11px; color: #666; padding: 5px;")
        info_layout.addWidget(info_label)
        layout.addLayout(info_layout)
        
        # Log content area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QApplication.font())
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
                font-size: 11px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton(self.tr("Refresh"))
        refresh_btn.clicked.connect(self.load_logs)
        btn_layout.addWidget(refresh_btn)
        
        open_folder_btn = QPushButton(self.tr("Open Log Folder"))
        open_folder_btn.clicked.connect(self.open_log_folder)
        btn_layout.addWidget(open_folder_btn)
        
        copy_btn = QPushButton(self.tr("Copy to Clipboard"))
        copy_btn.clicked.connect(self.copy_logs)
        btn_layout.addWidget(copy_btn)
        
        save_btn = QPushButton(self.tr("Save As..."))
        save_btn.clicked.connect(self.save_logs)
        btn_layout.addWidget(save_btn)
        
        clear_btn = QPushButton(self.tr("Clear Logs"))
        clear_btn.clicked.connect(self.clear_logs)
        btn_layout.addWidget(clear_btn)
        
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def load_logs(self):
        """Load recent logs into the text area."""
        from gui.managers.log_manager import LogManager
        logs = LogManager.get_recent_logs(lines=500)
        self.log_text.setPlainText(logs)
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def open_log_folder(self):
        """Open the log file folder in the system file explorer."""
        from gui.managers.log_manager import LogManager
        import subprocess
        log_file = LogManager.get_log_file_path()
        log_dir = log_file.parent
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(log_dir)])
            elif platform.system() == 'Windows':
                subprocess.run(['explorer', str(log_dir)])
            else:  # Linux
                subprocess.run(['xdg-open', str(log_dir)])
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr(f"Could not open folder: {e}\n\nLog directory: {log_dir}")
            )
    
    def copy_logs(self):
        """Copy logs to clipboard."""
        logs = self.log_text.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(logs)
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            self.tr("Copied"),
            self.tr("Logs copied to clipboard!")
        )
    
    def save_logs(self):
        """Save logs to a file."""
        logs = self.log_text.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Logs"),
            f"fonixflow_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            self.tr("Text Files (*.txt);;All Files (*)")
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(logs)
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    self.tr("Saved"),
                    self.tr(f"Logs saved to:\n{file_path}")
                )
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    self.tr("Error"),
                    self.tr(f"Could not save logs: {e}")
                )
    
    def clear_logs(self):
        """Clear the log file."""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            self.tr("Clear Logs"),
            self.tr("Are you sure you want to clear all logs? This cannot be undone."),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from gui.managers.log_manager import LogManager
            if LogManager.clear_logs():
                QMessageBox.information(
                    self,
                    self.tr("Logs Cleared"),
                    self.tr("Log file has been cleared.")
                )
                self.load_logs()
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Error"),
                    self.tr("Could not clear logs.")
                )


class LicenseLimitationsDialog(QDialog):
    """Dialog explaining limitations for unlicensed users."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("FonixFlow - Free Version"))
        self.setMaximumWidth(400)
        self.setMinimumSize(350, 300)
        # Ensure dialog appears on top of splash screen
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setup_ui()
        self.center_on_screen()
    
    def center_on_screen(self):
        """Center the dialog on the primary screen."""
        try:
            frame_geom = self.frameGeometry()
            screen_center = QApplication.primaryScreen().availableGeometry().center()
            frame_geom.moveCenter(screen_center)
            self.move(frame_geom.topLeft())
        except Exception as e:
            logger.warning(f"Error centering dialog: {e}")
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo
        from tools.resource_locator import get_resource_path
        logo_path = get_resource_path('assets/logo.png')
        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale logo to reasonable size (max width 300px, maintain aspect ratio)
            if pixmap.width() > 300:
                pixmap = pixmap.scaledToWidth(300)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            # Fallback text if logo not found
            logo_label.setText(self.tr("FonixFlow"))
            logo_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(logo_label)
        
        # Description text (plain text, no scrolling, no styled background)
        desc_text = QLabel(
            self.tr(
                "Free: Unlimited audio recording. Transcription is limited to 500 words per file.\n\n"
                "Pro:  Unlock unlimited transcription with no word limits and full multi-language support."
            )
        )
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("""
            font-size: 13px;
            padding: 10px 0px;
        """)
        layout.addWidget(desc_text)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        use_free_btn = QPushButton(self.tr("Use Free Version"))
        use_free_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        use_free_btn.clicked.connect(self.accept)
        btn_layout.addWidget(use_free_btn)
        
        purchase_btn = QPushButton(self.tr("Purchase License"))
        purchase_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        purchase_btn.clicked.connect(self.purchase_license)
        btn_layout.addWidget(purchase_btn)
        
        layout.addLayout(btn_layout)
    
    def purchase_license(self):
        """Open purchase page in browser."""
        import webbrowser
        webbrowser.open("https://fonixflow.com/#/pricing")
        self.accept()

