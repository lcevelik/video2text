"""
Recording management mixin for FonixFlow main window.

Extracted from main_window.py to reduce God class size.
Handles: recording start/stop, audio preview, device management, recording callbacks.
"""

import time
import logging

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QTimer

from gui.theme import Theme
from gui.workers import RecordingWorker, AudioPreviewWorker
from gui.utils import check_audio_input_devices

logger = logging.getLogger(__name__)


class RecordingController:
    """Mixin providing recording management methods."""

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
            if self.check_audio_devices():
                self.start_basic_recording()
            else:
                self.show_no_device_dialog()
        else:
            self.stop_basic_recording()

    def check_audio_devices(self):
        """Check if audio input devices are available."""
        return check_audio_input_devices()

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
            logger.info("User requested device detection retry")
            if self.check_audio_devices():
                QMessageBox.information(
                    self,
                    self.tr("Device Found"),
                    self.tr("✅ Audio input device detected!\n\nYou can now start recording.")
                )
                self.start_basic_recording()
            else:
                self.show_no_device_dialog()

    def start_basic_recording(self):
        """Start recording in Basic Mode."""
        self.is_recording = True
        self.recording_start_time = time.time()

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

        self.drop_zone.setEnabled(False)
        self.recording_time_label.setText(self.tr("00:00:00"))
        self.recording_time_label.show()
        self.recording_timer.start(1000)

        self.statusBar().showMessage(self.tr("Recording from Microphone + Speaker..."))
        self.basic_record_progress_label.setText(self.tr("Recording in progress..."))
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('error', self.is_dark_mode)}; font-weight: bold;")

        logger.info("Started basic mode recording (mic: default, speaker: default/system)")

        self.stop_audio_preview()

        self.recording_worker = RecordingWorker(
            output_dir=self.settings["recordings_dir"],
            mic_device=None,
            speaker_device=None,
            enable_filters=self.enable_audio_filters,
            time_limit=self.recording_time_limit,
            parent=self
        )
        self.recording_worker.recording_complete.connect(self.on_recording_complete)
        self.recording_worker.recording_error.connect(self.on_recording_error)
        self.recording_worker.audio_levels_update.connect(self.update_audio_levels)
        self.recording_worker.status_update.connect(self.on_recording_status_update)
        self.recording_worker.start()

    def stop_basic_recording(self):
        """Stop recording in Basic Mode."""
        self.is_recording = False
        self.recording_timer.stop()

        if self.recording_worker:
            self.recording_worker.stop()

        self.basic_record_btn.setText(self.tr("Start Recording"))
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()

        self.drop_zone.setEnabled(True)
        self.recording_time_label.hide()

        self.basic_record_progress_bar.show()
        self.basic_record_progress_bar.setValue(0)

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
            self.recording_time_label.setText(f"{hours:02d}:{mins:02d}:{secs:02d}")

    def start_audio_preview(self):
        """Start the audio preview worker for continuous VU meter updates."""
        if self.audio_preview_worker is None or not self.audio_preview_worker.isRunning():
            if self.audio_preview_worker is not None:
                try:
                    self.audio_preview_worker.audio_levels_update.disconnect(self.update_audio_levels)
                except Exception:
                    pass
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
        self.video_path = recorded_path
        self.multi_language_mode = None
        self.statusBar().showMessage(f"Recording complete ({duration:.1f}s). File saved.")

        self.drop_zone.setEnabled(True)
        self.basic_record_progress_label.setText(f"Recording complete ({duration:.1f}s). Ready for manual transcription.")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('success', self.is_dark_mode)};")

        if hasattr(self, 'transcribe_recording_btn'):
            self.transcribe_recording_btn.show()

        self.start_audio_preview()

    def on_recording_status_update(self, message: str):
        """Handle status updates from recording worker."""
        if "System audio not captured" in message or "Warning" in message:
            QMessageBox.warning(
                self,
                self.tr("System Audio Not Available"),
                self.tr(
                    "System audio was not captured during recording.\n\n"
                    "Possible causes:\n"
                    "1. Screen Recording permission not granted\n"
                    "2. No audio was playing during recording\n"
                    "3. ScreenCaptureKit stream failed to start\n\n"
                    "To fix:\n"
                    "1. Go to: System Settings → Privacy & Security → Screen Recording\n"
                    "2. Enable permission for Terminal (or your Python launcher)\n"
                    "3. Restart the application\n\n"
                    "Recording will continue with microphone only."
                )
            )
        self.statusBar().showMessage(message)

    def on_recording_error(self, error_message):
        """Slot called when recording encounters an error (thread-safe)."""
        self.statusBar().showMessage(error_message)
        self.drop_zone.setEnabled(True)

        self.basic_record_progress_label.setText(f"Error: {error_message}")
        self.basic_record_progress_label.setStyleSheet(f"font-size: 13px; color: {Theme.get('error', self.is_dark_mode)};")

        self.is_recording = False
        self.recording_timer.stop()
        self.recording_time_label.hide()
        self.basic_record_btn.setText(self.tr("Start Recording"))
        self.basic_record_btn.primary = True
        self.basic_record_btn.apply_style()

        self.start_audio_preview()

    def change_recordings_directory(self):
        """Open dialog to change recordings directory (delegated to FileManager)."""
        self.file_manager.change_recordings_directory(self.settings_manager)

    def open_recordings_folder(self):
        """Open the recordings folder in the system file explorer (delegated to FileManager)."""
        from gui.managers.path_manager import PathManager
        default_recordings = str(PathManager.get_recordings_dir())
        recordings_dir = self.settings_manager.get("recordings_dir", default_recordings)
        self.file_manager.open_recordings_folder(recordings_dir)

    def show_recording_dialog(self):
        """Show recording dialog (Advanced Mode only)."""
        from gui.dialogs import RecordingDialog
        dialog = RecordingDialog(self)
        if dialog.exec() and dialog.recorded_path:
            self.load_file(dialog.recorded_path)
