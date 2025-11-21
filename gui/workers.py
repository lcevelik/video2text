from PySide6.QtCore import QThread, Signal
class AudioPreviewWorker(QThread):
    """Background worker to stream live audio levels for VU meters."""
    audio_levels_update = Signal(float, float)  # (mic_level, speaker_level)

    def __init__(self, mic_device=None, speaker_device=None, parent=None):
        super().__init__(parent)
        self.mic_device = mic_device
        self.speaker_device = speaker_device
        self.is_running = True
        self.backend = None

    def stop(self):
        self.is_running = False
        if self.backend:
            self.backend.is_recording = False

    def run(self):
        from gui.recording import SoundDeviceBackend
        import sounddevice as sd
        import numpy as np
        self.backend = SoundDeviceBackend(self.mic_device, self.speaker_device)
        self.backend.start_recording()
        last_mic_level = 0.0
        last_speaker_level = 0.0
        while self.is_running:
            mic_level = 0.0
            if self.backend.mic_chunks:
                mic_chunk = self.backend.mic_chunks[-1]
                mic_level = float(np.clip(np.abs(mic_chunk).max(), 0.0, 1.0))
            speaker_level = 0.0
            if self.backend.speaker_chunks:
                speaker_chunk = self.backend.speaker_chunks[-1]
                speaker_level = float(np.clip(np.abs(speaker_chunk).max(), 0.0, 1.0))
            if abs(mic_level - last_mic_level) > 0.01 or abs(speaker_level - last_speaker_level) > 0.01:
                self.audio_levels_update.emit(mic_level, speaker_level)
                last_mic_level = mic_level
                last_speaker_level = speaker_level
            sd.sleep(50)
        if self.backend:
            self.backend.cleanup()
"""
Qt worker threads for background processing - Refactored with modular backends.
"""

import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

import numpy as np
from PySide6.QtCore import QThread, Signal
from pydub import AudioSegment

from gui.utils import get_platform
from gui.recording import (
    AudioProcessor,
    SoundDeviceBackend,
    ScreenCaptureKitBackend,
    HAS_SCREENCAPTUREKIT
)

logger = logging.getLogger(__name__)


class RecordingWorker(QThread):
    """
    Qt worker thread for audio recording with pluggable backends.

    Automatically selects the best backend for the platform:
    - macOS 12.3+: ScreenCaptureKit (if available)
    - All platforms: SoundDevice (with BlackHole/WASAPI/PulseAudio)
    """

    # Signals for thread-safe communication with main thread
    recording_complete = Signal(str, float)  # (file_path, duration)
    recording_error = Signal(str)  # error_message
    status_update = Signal(str)  # status_message
    audio_levels_update = Signal(float, float)  # (mic_level, speaker_level)

    def __init__(self, output_dir: str,
                 mic_device: Optional[int] = None,
                 speaker_device: Optional[int] = None,
                 backend: Optional[str] = None,
                 parent=None):
        """
        Initialize recording worker.

        Args:
            output_dir: Directory to save recordings
            mic_device: Device index for microphone (None = auto-detect)
            speaker_device: Device index for system audio (None = auto-detect)
            backend: Force specific backend ('sounddevice' or 'screencapturekit'),
                    or None for auto-select
            parent: Parent QObject
        """
        super().__init__(parent)
        self.output_dir = Path(output_dir)
        self.mic_device = mic_device
        self.speaker_device = speaker_device
        self.backend_name = backend
        self.backend = None
        self.is_recording = True

    def stop(self):
        """Stop the recording."""
        self.is_recording = False
        if self.backend:
            self.backend.is_recording = False

    def _select_backend(self):
        """
        Select the best recording backend for the current platform.

        Returns:
            Initialized recording backend

        Raises:
            RuntimeError: If no suitable backend is available
        """
        # If backend explicitly specified, use it
        if self.backend_name == 'screencapturekit':
            if not HAS_SCREENCAPTUREKIT:
                raise RuntimeError(
                    "ScreenCaptureKit backend requested but not available.\n"
                    "Requires macOS 12.3+ and PyObjC."
                )
            logger.info("Using ScreenCaptureKit backend (forced)")
            return ScreenCaptureKitBackend(self.mic_device, self.speaker_device)

        if self.backend_name == 'sounddevice':
            logger.info("Using SoundDevice backend (forced)")
            return SoundDeviceBackend(self.mic_device, self.speaker_device)

        # Auto-select backend based on platform
        platform = get_platform()

        # On macOS, prefer ScreenCaptureKit for native system audio (no BlackHole required!)
        if platform == 'macos' and HAS_SCREENCAPTUREKIT:
            try:
                logger.info("Auto-selecting ScreenCaptureKit backend for macOS (native system audio)")
                return ScreenCaptureKitBackend(self.mic_device, self.speaker_device)
            except Exception as e:
                logger.warning(f"ScreenCaptureKit unavailable ({e}), falling back to SoundDevice")
                logger.info("To use ScreenCaptureKit: pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation pyobjc-framework-Cocoa")

        # Default to SoundDevice backend (cross-platform)
        # Note: On macOS without ScreenCaptureKit, this requires BlackHole for system audio
        logger.info(f"Using SoundDevice backend for {platform}")
        return SoundDeviceBackend(self.mic_device, self.speaker_device)

    def run(self):
        """Execute recording in background thread."""
        try:
            # Select and initialize backend
            self.backend = self._select_backend()
            backend_name = self.backend.get_backend_name()
            logger.info(f"=== Recording Worker Started (backend: {backend_name}) ===")
            logger.info(f"Requested devices - Mic: {self.mic_device}, Speaker: {self.speaker_device}")

            # Start recording
            self.backend.start_recording()

            # Record while active, emit audio levels
            import sounddevice as sd
            last_mic_level = 0.0
            last_speaker_level = 0.0
            while self.is_recording:
                # Calculate mic level
                mic_level = 0.0
                if self.backend.mic_chunks:
                    mic_chunk = self.backend.mic_chunks[-1]
                    mic_level = float(np.clip(np.abs(mic_chunk).max(), 0.0, 1.0))
                # Calculate speaker level
                speaker_level = 0.0
                if self.backend.speaker_chunks:
                    speaker_chunk = self.backend.speaker_chunks[-1]
                    speaker_level = float(np.clip(np.abs(speaker_chunk).max(), 0.0, 1.0))
                # Debug logging for chunk sizes and levels
                logger.debug(f"VU DEBUG: mic_chunks={len(self.backend.mic_chunks)}, speaker_chunks={len(self.backend.speaker_chunks)}, mic_level={mic_level:.3f}, speaker_level={speaker_level:.3f}")
                # Only emit if changed
                if abs(mic_level - last_mic_level) > 0.01 or abs(speaker_level - last_speaker_level) > 0.01:
                    logger.debug(f"VU DEBUG: Emitting levels mic={mic_level:.3f}, speaker={speaker_level:.3f}")
                    self.audio_levels_update.emit(mic_level, speaker_level)
                    last_mic_level = mic_level
                    last_speaker_level = speaker_level
                sd.sleep(50)

            # Stop and collect results
            result = self.backend.stop_recording()

            # Process audio using AudioProcessor
            logger.info("Processing recorded audio...")
            final_data = AudioProcessor.mix_audio(
                mic_data=result.mic_data,
                speaker_data=result.speaker_data,
                mic_rate=result.mic_sample_rate,
                speaker_rate=result.speaker_sample_rate,
                target_rate=16000
            )

            if final_data is None or final_data.size == 0:
                logger.error("Final data is empty after processing!")
                self.recording_error.emit("❌ Recording error: no audio samples captured")
                return

            # Normalize the final mixed audio
            logger.info(f"Normalizing audio (current shape: {final_data.shape})")
            final_data = AudioProcessor.normalize_audio(final_data, target_rms=0.12)

            # Final safety limiting to prevent clipping
            final_data = AudioProcessor.apply_safety_limiting(final_data, max_level=0.98)

            # Save recording
            recorded_path = self._save_recording(final_data, sample_rate=16000)
            duration = len(final_data) / 16000

            logger.info(f"✅ Recording saved: {recorded_path} ({duration:.1f}s)")

            # Emit signal to main thread
            self.recording_complete.emit(recorded_path, duration)

        except Exception as e:
            logger.error(f"Recording error: {e}", exc_info=True)
            self.recording_error.emit(f"❌ Recording error: {str(e)}")

        finally:
            if self.backend:
                self.backend.cleanup()

    def _save_recording(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """
        Save audio data to file.

        Args:
            audio_data: Normalized audio data
            sample_rate: Sample rate (Hz)

        Returns:
            Path to saved file

        Raises:
            RuntimeError: If save fails
        """
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp3"
        recorded_path = str(self.output_dir / filename)

        logger.info(f"Saving recording to: {recorded_path}")

        # Convert to int16 for audio file
        audio_data_int16 = (audio_data * 32767).astype(np.int16)

        # Convert numpy array to AudioSegment and export as MP3
        audio_segment = AudioSegment(
            audio_data_int16.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,  # 16-bit audio = 2 bytes
            channels=1  # mono
        )

        try:
            audio_segment.export(recorded_path, format="mp3", bitrate="320k")
        except Exception as export_err:
            logger.warning(f"MP3 export failed ({export_err}); falling back to WAV")
            import wave
            wav_path = str(self.output_dir / f"recording_{timestamp}.wav")
            with wave.open(wav_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data_int16.tobytes())
            recorded_path = wav_path

        return recorded_path


class TranscriptionWorker(QThread):
    """Qt worker thread for transcription with proper signal handling."""

    # Signals for thread-safe communication
    progress_update = Signal(str, int)  # (message, percentage)
    transcription_complete = Signal(dict)  # result dictionary
    transcription_error = Signal(str)  # error message

    def __init__(self, video_path, model_size='tiny', language=None,
                 detect_language_changes=False, use_deep_scan=False, parent=None):
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

            audio_path = extractor.extract_audio(self.video_path,
                                                progress_callback=audio_progress_callback)

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

            if (self.detect_language_changes and self.allowed_languages and
                hasattr(transcriber, 'allowed_languages')):
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
                mode_desc = ("deep scanning (audio chunks)" if self.use_deep_scan
                           else "fast transcript segmentation")
                self.progress_update.emit(
                    f"Transcribing with multi-language {mode_desc}...", 60
                )
                logger.info(f"Starting transcribe_multilang with "
                          f"allowed_languages={self.allowed_languages}")

                result = transcriber.transcribe_multilang(
                    audio_path,
                    detect_language_changes=True,
                    use_segment_retranscription=True,
                    progress_callback=progress_callback,
                    detection_model="base",
                    transcription_model=self.model_size,
                    skip_fast_single=True,
                    skip_sampling=True,
                    fast_text_language=not self.use_deep_scan,
                    allowed_languages=self.allowed_languages if self.allowed_languages else None
                )
                logger.info(f"transcribe_multilang returned. Result type: {type(result)}, "
                          f"has 'text': {'text' in result if result else 'None'}")
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

            logger.info(f"About to emit transcription_complete signal. "
                       f"Result keys: {result.keys() if result else 'None'}")
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
