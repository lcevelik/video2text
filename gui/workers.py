"""
Qt worker threads for background processing.
"""

import logging
from pathlib import Path
from typing import List

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class RecordingWorker(QThread):
    """Qt worker thread for audio recording with proper signal handling."""

    # Signals for thread-safe communication with main thread
    recording_complete = Signal(str, float)  # (file_path, duration)
    recording_error = Signal(str)  # error_message
    status_update = Signal(str)  # status_message
    audio_level = Signal(float, float)  # (mic_level, speaker_level) in range 0.0-1.0

    def __init__(self, output_dir, parent=None):
        super().__init__(parent)
        self.is_recording = True
        self.output_dir = Path(output_dir)
        self.mic_level = 0.0
        self.speaker_level = 0.0

    def stop(self):
        """Stop the recording."""
        self.is_recording = False

    def run(self):
        """Execute recording in background thread."""
        try:
            import sounddevice as sd
            import numpy as np
            from pydub import AudioSegment
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
                    # Calculate RMS (root mean square) level for visualization
                    rms = np.sqrt(np.mean(indata**2))
                    self.mic_level = float(min(1.0, rms * 10))  # Scale and clamp to 0-1

            def speaker_callback(indata, frames, time_info, status):
                if self.is_recording:
                    speaker_chunks.append(indata.copy())
                    # Calculate RMS level
                    rms = np.sqrt(np.mean(indata**2))
                    self.speaker_level = float(min(1.0, rms * 10))  # Scale and clamp to 0-1

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
            import time
            last_level_update = time.time()
            while self.is_recording:
                sd.sleep(100)
                # Emit audio levels every 100ms
                current_time = time.time()
                if current_time - last_level_update >= 0.1:
                    self.audio_level.emit(self.mic_level, self.speaker_level)
                    last_level_update = current_time

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
                filename = f"recording_{timestamp}.mp3"
                recorded_path = str(self.output_dir / filename)

                # Save recording as high-quality MP3 (320kbps)
                final_data_int16 = (final_data * 32767).astype(np.int16)

                # Convert numpy array to AudioSegment and export as MP3
                audio_segment = AudioSegment(
                    final_data_int16.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,  # 16-bit audio = 2 bytes
                    channels=1  # mono
                )
                audio_segment.export(recorded_path, format="mp3", bitrate="320k")

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
        self._transcriber = None
        self.cancel_requested = False
        self.allowed_languages: List[str] = []

    def run(self):
        """Execute transcription in background thread."""
        try:
            from audio_extractor import AudioExtractor
            from transcriber import Transcriber
            from transcription.enhanced import EnhancedTranscriber

            # Step 1: Extract audio from video if needed (with progress callback)
            self.progress_update.emit("Extracting audio...", 10)

            extractor = AudioExtractor()

            # Define progress callback for audio extraction
            def audio_progress_callback(message, percentage):
                # Map audio extraction progress (5-30%) to overall progress (10-30%)
                overall_pct = 10 + int((percentage / 30.0) * 20)
                self.progress_update.emit(message, overall_pct)

            audio_path = extractor.extract_audio(self.video_path, progress_callback=audio_progress_callback)

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
            self._transcriber = transcriber
            if self.detect_language_changes and self.allowed_languages and hasattr(transcriber, 'allowed_languages'):
                transcriber.allowed_languages = self.allowed_languages

            # Define progress callback
            def progress_callback(message):
                # Support PROGRESS:<pct>:<msg> format for granular updates
                if message.startswith("PROGRESS:"):
                    try:
                        parts = message.split(":", 2)
                        pct = int(parts[1])
                        msg = parts[2] if len(parts) > 2 else ""
                        self.progress_update.emit(msg, max(0, min(100, pct)))
                        return
                    except Exception:
                        pass
                if "Starting" in message:
                    self.progress_update.emit(message, 50)
                elif "complete" in message.lower():
                    self.progress_update.emit(message, 95)
                else:
                    # Default mid-progress bucket
                    self.progress_update.emit(message, 70)

            # Transcribe
            if self.detect_language_changes:
                # Always enable multi-language path; decide depth via fast_text_language vs deep scan
                mode_desc = "deep scanning (audio chunks)" if self.use_deep_scan else "fast transcript segmentation"
                self.progress_update.emit(f"Transcribing with multi-language {mode_desc}...", 60)
                logger.info(f"Starting transcribe_multilang with allowed_languages={self.allowed_languages}")
                # Ensure fallback to audio chunk analysis if transcript heuristic yields single language
                result = transcriber.transcribe_multilang(
                    audio_path,
                    detect_language_changes=True,
                    use_segment_retranscription=True,
                    progress_callback=progress_callback,
                    detection_model="base",
                    transcription_model=self.model_size,
                    skip_fast_single=True,  # Always allow fallback chunk pass when heuristic returns single language
                    skip_sampling=True,
                    fast_text_language=not self.use_deep_scan,
                    allowed_languages=self.allowed_languages if self.allowed_languages else None
                )
                logger.info(f"transcribe_multilang returned. Result type: {type(result)}, has 'text': {'text' in result if result else 'None'}")
            else:
                self.progress_update.emit("Transcribing audio...", 60)
                logger.info("Starting regular transcribe")
                result = transcriber.transcribe(
                    audio_path,
                    language=self.language if self.language and self.language != "Auto-detect" else None,
                    progress_callback=progress_callback
                )
                logger.info(f"transcribe returned. Result type: {type(result)}")

            logger.info(f"About to emit progress 100%")
            self.progress_update.emit("Transcription complete!", 100)
            
            logger.info(f"About to emit transcription_complete signal. Result keys: {result.keys() if result else 'None'}")
            try:
                # Emit result
                self.transcription_complete.emit(result)
                logger.info(f"transcription_complete signal emitted successfully")
            except Exception as emit_error:
                logger.error(f"ERROR emitting signal: {emit_error}", exc_info=True)
                raise

        except Exception as e:
            import traceback
            logger.error(f"Transcription error: {e}", exc_info=True)
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.transcription_error.emit(f"Transcription failed: {str(e)}")

    def cancel(self):
        """Request cancellation of current transcription (chunk-level for multi-language)."""
        self.cancel_requested = True
        if self._transcriber and hasattr(self._transcriber, 'request_cancel'):
            self._transcriber.request_cancel()
        self.progress_update.emit("Cancellation requested...", 95)
        logger.info("Cancellation requested by user")

