"""
Transcription management mixin for FonixFlow main window.

Extracted from main_window.py to reduce God class size.
Handles: transcription start/stop/cancel, progress, completion, save.
"""

import time
import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QFileDialog,
    QMessageBox, QStackedWidget, QListWidget, QListWidgetItem, QMenu, QDialog,
    QComboBox, QCheckBox, QGroupBox, QSystemTrayIcon, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QEvent, QCoreApplication, QThread, Signal  # type: ignore
from PySide6.QtGui import QPalette, QIcon, QAction  # type: ignore

from gui.workers import TranscriptionWorker
from gui.dialogs import MultiLanguageChoiceDialog

logger = logging.getLogger(__name__)


class TranscriptionController:
    """Mixin providing transcription management methods."""

    def start_transcription(self):
        """Start transcription process."""
        if not self.video_path:
            QMessageBox.warning(self, self.tr("No File"), self.tr("Please select a file first."))
            return

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

        if not self.model_name_label:
            self.model_name_label = QLabel("")
            self.model_name_label.setStyleSheet("font-size:12px; color:#0FD2CC; font-weight:bold; font-family:Consolas;")
            self.statusBar().addPermanentWidget(self.model_name_label)
            if not hasattr(self, 'hardware_status_widget'):
                from PySide6.QtWidgets import QWidget, QHBoxLayout
                self.hardware_status_widget = QWidget()
                layout = QHBoxLayout(self.hardware_status_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(6)
                self.hardware_status_dot = QLabel()
                self.hardware_status_dot.setFixedSize(12, 12)
                self.hardware_status_dot.setStyleSheet("border-radius: 6px; background: #BDBDBD; border: 1px solid #888;")
                layout.addWidget(self.hardware_status_dot)
                self.hardware_status_label = QLabel("")
                self.hardware_status_label.setStyleSheet("font-size:12px; font-family:Consolas; color:#888;")
                layout.addWidget(self.hardware_status_label)
                self.statusBar().addPermanentWidget(self.hardware_status_widget)

        self.update_hardware_status_indicator()

    def update_hardware_status_indicator(self):
        from gui.utils import has_gpu_available
        gpu_ok = has_gpu_available()
        if gpu_ok:
            self.hardware_status_dot.setStyleSheet("border-radius: 6px; background: #0FD2CC; border: 1px solid #0CBFB3;")
            self.hardware_status_label.setText("GPU: OK")
            self.hardware_status_label.setStyleSheet("font-size:12px; font-family:Consolas; color:#0FD2CC; font-weight:bold;")
        else:
            self.hardware_status_dot.setStyleSheet("border-radius: 6px; background: #E74C3C; border: 1px solid #B22222;")
            self.hardware_status_label.setText("CPU")
            self.hardware_status_label.setStyleSheet("font-size:12px; font-family:Consolas; color:#E74C3C; font-weight:bold;")

        if self.multi_language_mode is None:
            if not self.prompt_multi_language_and_transcribe(from_start=True):
                return
        multi_mode = self.multi_language_mode

        if multi_mode:
            COMMON_LANGUAGES = {'en', 'es', 'fr', 'de', 'it', 'pt'}
            requires_large_model = False
            if hasattr(self, 'allowed_languages') and self.allowed_languages:
                for lang in self.allowed_languages:
                    if lang not in COMMON_LANGUAGES:
                        requires_large_model = True
                        break

            if requires_large_model:
                model_size = "large-v3"
                logger.info(f"Less common languages detected {getattr(self, 'allowed_languages', [])}: Using large-v3 for better accuracy")
            else:
                model_size = "medium"
                if hasattr(self, 'allowed_languages') and self.allowed_languages:
                    logger.info(f"Common languages detected {self.allowed_languages}: Using medium model")
                else:
                    logger.info("No specific languages selected: Using medium model")

            language = None
            detect_language_changes = True
            use_deep_scan = bool(getattr(self, 'enable_deep_scan', False))
        else:
            single_lang_type = getattr(self, 'single_language_type', None)
            if single_lang_type == 'english':
                model_size = "small.en"
                language = "en"
                logger.info("Single-language English: Using small.en model")
            elif single_lang_type == 'other':
                model_size = "medium"
                language = None
                logger.info("Single-language Other: Using medium multilingual model")
            else:
                model_size = "base"
                language = None
                logger.warning("No single-language type selected, using base model as fallback")
            detect_language_changes = False
            use_deep_scan = False

        if self.model_name_label:
            if detect_language_changes:
                self.model_name_label.setText(f"Model: Base + {model_size}")
            else:
                self.model_name_label.setText(f"Model: {model_size}")

        if hasattr(self, 'transcription_worker') and self.transcription_worker and self.transcription_worker.isRunning():
            logger.warning("Transcription already running, ignoring duplicate start request")
            return

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
        if detect_language_changes and hasattr(self, 'allowed_languages'):
            self.transcription_worker.allowed_languages = self.allowed_languages

        self.transcription_worker.progress_update.connect(self.on_transcription_progress)
        self.transcription_worker.transcription_complete.connect(self.on_transcription_complete)
        self.transcription_worker.transcription_error.connect(self.on_transcription_error)

        self.transcription_worker.start()

        logger.info(f"Started transcription: {self.video_path}, model={model_size}, language={language}, multi-lang={detect_language_changes}, deep-scan={use_deep_scan}")

    def prompt_multi_language_and_transcribe(self, from_start: bool = False):
        """Prompt user to choose multi-language vs single-language before transcription."""
        logger.info(f"[PROMPT_MULTI_LANG] video_path={self.video_path}, from_start={from_start}")
        if self.video_path is None:
            logger.warning("[PROMPT_MULTI_LANG] video_path is None, aborting transcription")
            return False
        if self.multi_language_mode is not None and not from_start:
            self.start_transcription()
            return True

        dlg = MultiLanguageChoiceDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.multi_language_mode = dlg.is_multi_language
            self.allowed_languages = getattr(dlg, 'selected_languages', []) if self.multi_language_mode else []
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
        """Save current transcription."""
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
        self.current_progress_pct = percentage

        if "Falling back to CPU due to MPS compatibility issue" in message:
            self.update_hardware_status_indicator()

        if not hasattr(self, 'elapsed_time_timer'):
            self.elapsed_time_timer = QTimer(self)
            self.elapsed_time_timer.timeout.connect(self.update_elapsed_time_display)
            self.elapsed_time_timer.start(500)

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

        self.update_elapsed_time_display()

        if getattr(self, 'transcription_start_time', None) and percentage > 0:
            elapsed = time.time() - self.transcription_start_time
            if percentage < 100:
                rate = percentage / elapsed if elapsed > 0 else 0
                eta = (100 - percentage) / rate if rate > 0 else 0
            else:
                eta = 0
            if hasattr(self, 'performance_overlay') and self.performance_overlay is not None:
                self.performance_overlay.setText(f"{percentage}% | Elapsed {elapsed:.1f}s | ETA {eta:.1f}s")

        if percentage >= 100:
            if hasattr(self, 'elapsed_time_timer'):
                self.elapsed_time_timer.stop()
                self.elapsed_time_timer.deleteLater()
                delattr(self, 'elapsed_time_timer')

        try:
            self.statusBar().showMessage(message)
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")

    def on_transcription_complete(self, result: dict):
        """Handle successful transcription completion (worker signal)."""
        from transcription.enhanced import EnhancedTranscriber
        self.transcription_result = result
        text = result.get('text', '')

        if not self.license_valid:
            words = text.split()
            if len(words) > 500:
                logger.info(f"Unlicensed user word limit exceeded ({len(words)} words). Truncating to 500.")
                truncated_text = " ".join(words[:500])
                text = truncated_text + f"\n\n[TRUNCATED: Free version limit is 500 words. Your transcription has {len(words)} words. Activate a license for unlimited transcription.]"
                result['text'] = text
                QMessageBox.information(
                    self,
                    self.tr("Transcription Limit Reached"),
                    self.tr(f"Your transcription has {len(words)} words, but the free version is limited to 500 words.\n\nActivate a license to transcribe unlimited words.")
                )

        segments = result.get('segments', [])
        segment_count = len(segments)
        language = result.get('language', 'unknown')
        lang_name = EnhancedTranscriber.LANGUAGE_NAMES.get(language, language.upper())
        language_timeline = result.get('language_timeline', '')
        language_segments = result.get('language_segments', [])

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

        if hasattr(self, 'basic_result_text'):
            self.basic_result_text.clear()
            self.basic_result_text.setPlainText(display_text)

        if hasattr(self, 'basic_save_btn'):
            self.basic_save_btn.setEnabled(True)
        if hasattr(self, 'cancel_transcription_btn') and self.cancel_transcription_btn:
            self.cancel_transcription_btn.setEnabled(False)
            self.cancel_transcription_btn.hide()

        if getattr(self, 'transcription_start_time', None) and hasattr(self, 'performance_overlay') and self.performance_overlay:
            total = time.time() - self.transcription_start_time
            audio_dur = segments[-1].get('end', 0) if segments else 0
            rtf = (total / audio_dur) if audio_dur else 0
            self.performance_overlay.setText(f"Finished in {total:.2f}s (RTF {rtf:.2f})")

        if hasattr(self, 'basic_transcript_desc'):
            if has_multilang:
                self.basic_transcript_desc.setText(f"{lang_info} | {segment_count} segments")
            else:
                self.basic_transcript_desc.setText(f"Language: {lang_name} | {segment_count} segments")

        if hasattr(self, 'tab_bar') and hasattr(self, 'basic_tab_stack'):
            try:
                self.on_tab_changed(2)
                logger.info("Auto-jumped to transcript tab after transcription completion")
            except Exception as e:
                logger.warning(f"Could not auto-jump to transcript tab: {e}")

        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(f"Complete! {lang_info}")
        if hasattr(self, 'basic_upload_progress_bar'):
            self.basic_upload_progress_bar.setValue(100)
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(f"Complete! {lang_info}")
        if hasattr(self, 'basic_record_progress_bar'):
            self.basic_record_progress_bar.setValue(100)

        try:
            self.statusBar().showMessage(f"Transcription complete ({segment_count} segments, {lang_info})")
        except Exception as e:
            logger.debug(f"Could not update status bar: {e}")

        if has_multilang:
            logger.info(f"Multi-language transcription complete: {len(language_segments)} language segments detected")
        logger.info(f"Transcription complete: {len(text)} characters, {segment_count} segments")

        if hasattr(self, 'transcription_worker') and self.transcription_worker:
            try:
                self.transcription_worker.deleteLater()
            except Exception:
                pass
            self.transcription_worker = None
            logger.info("Transcription worker cleaned up after completion")

    def on_transcription_error(self, error_message: str):
        """Handle transcription error (worker signal)."""
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(f"Error: {error_message}")
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(f"Error: {error_message}")
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

        if hasattr(self, 'transcription_worker') and self.transcription_worker:
            try:
                self.transcription_worker.deleteLater()
            except Exception:
                pass
            self.transcription_worker = None
            logger.info("Transcription worker cleaned up after error")

    def clear_for_new_transcription(self):
        """Cancel any active transcription and reset UI for new transcription."""
        if getattr(self, 'transcription_worker', None) and self.transcription_worker.isRunning():
            self.transcription_worker.cancel()
            self.transcription_worker.wait(3000)

        self.video_path = None
        self.transcription_result = None
        self.multi_language_mode = None
        self.allowed_languages = []
        self.single_language_type = None

        if hasattr(self, 'basic_result_text'):
            self.basic_result_text.clear()
        if hasattr(self, 'basic_save_btn'):
            self.basic_save_btn.setEnabled(False)
        if hasattr(self, 'basic_upload_progress_bar'):
            self.basic_upload_progress_bar.setValue(0)
        if hasattr(self, 'basic_record_progress_bar'):
            self.basic_record_progress_bar.setValue(0)
        if hasattr(self, 'basic_upload_progress_label'):
            self.basic_upload_progress_label.setText(self.tr("Ready to transcribe"))
        if hasattr(self, 'basic_record_progress_label'):
            self.basic_record_progress_label.setText(self.tr("Ready to record"))

        if hasattr(self, 'drop_zone'):
            self.drop_zone.setEnabled(True)
            if hasattr(self.drop_zone, 'text_label'):
                self.drop_zone.text_label.setText(self.tr("Drag and drop video/audio file"))

        if hasattr(self, 'cancel_transcription_btn'):
            self.cancel_transcription_btn.hide()

        if hasattr(self, 'performance_overlay') and self.performance_overlay:
            self.performance_overlay.setText("")

        if hasattr(self, 'model_name_label') and self.model_name_label:
            self.model_name_label.setText("")

        self.statusBar().showMessage(self.tr("Ready for new transcription"))
        logger.info("Cleared for new transcription")
