"""
Qt worker threads for background processing.
"""

import logging
from pathlib import Path
from typing import List

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class AudioPreviewWorker(QThread):
    """Qt worker thread for audio level preview without recording."""

    audio_level = Signal(float, float)  # (mic_level, speaker_level)

    def __init__(self, mic_device=None, speaker_device=None, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.mic_device = mic_device
        self.speaker_device = speaker_device
        self.mic_level = 0.0
        self.speaker_level = 0.0

    def stop(self):
        """Stop the preview."""
        self.is_running = False

    def run(self):
        """Monitor audio levels without recording."""
        try:
            import sounddevice as sd
            import numpy as np
            import time

            sample_rate = 16000

            # Callbacks
            def mic_callback(indata, frames, time_info, status):
                if self.is_running:
                    rms = np.sqrt(np.mean(indata**2))
                    self.mic_level = float(min(1.0, rms * 10))

            def speaker_callback(indata, frames, time_info, status):
                if self.is_running:
                    rms = np.sqrt(np.mean(indata**2))
                    self.speaker_level = float(min(1.0, rms * 10))

            # Start streams
            mic_stream = None
            speaker_stream = None

            if self.mic_device is not None:
                try:
                    mic_stream = sd.InputStream(device=self.mic_device, samplerate=sample_rate, channels=1, callback=mic_callback)
                    mic_stream.start()
                except Exception as e:
                    logger.warning(f"Could not start mic preview: {e}")

            if self.speaker_device is not None:
                try:
                    speaker_stream = sd.InputStream(device=self.speaker_device, samplerate=sample_rate, channels=1, callback=speaker_callback)
                    speaker_stream.start()
                except Exception as e:
                    logger.warning(f"Could not start speaker preview: {e}")

            # Monitor while active
            last_level_update = time.time()
            while self.is_running:
                sd.sleep(100)
                current_time = time.time()
                if current_time - last_level_update >= 0.1:
                    self.audio_level.emit(self.mic_level, self.speaker_level)
                    last_level_update = current_time

            # Stop streams
            if mic_stream:
                mic_stream.stop()
                mic_stream.close()
            if speaker_stream:
                speaker_stream.stop()
                speaker_stream.close()

        except Exception as e:
            logger.error(f"Audio preview error: {e}", exc_info=True)


class RecordingWorker(QThread):
    """Qt worker thread for audio recording with proper signal handling."""

    # Signals for thread-safe communication with main thread
    recording_complete = Signal(str, float)  # (file_path, duration)
    recording_error = Signal(str)  # error_message
    status_update = Signal(str)  # status_message
    audio_level = Signal(float, float)  # (mic_level, speaker_level) in range 0.0-1.0

    def __init__(self, output_dir, mic_device=None, speaker_device=None,
                 filter_settings=None, parent=None):
        super().__init__(parent)
        self.is_recording = True
        self.output_dir = Path(output_dir)
        self.mic_device = mic_device  # Device index or None for auto-detect
        self.speaker_device = speaker_device  # Device index or None for auto-detect
        self.mic_level = 0.0
        self.speaker_level = 0.0
        self.filter_settings = filter_settings or {}

    def stop(self):
        """Stop the recording."""
        self.is_recording = False

    def _normalize_audio(self, audio_data, target_rms=0.15):
        """
        Normalize audio to target RMS level with intelligent AGC.

        Args:
            audio_data: numpy array of audio samples
            target_rms: target RMS level (0.15 = good speech level, ~-16.5dB)

        Returns:
            Normalized audio data
        """
        import numpy as np

        # Calculate current RMS
        current_rms = np.sqrt(np.mean(audio_data**2))

        # Avoid division by zero
        if current_rms < 0.0001:
            return audio_data

        # Calculate gain needed to reach target RMS
        gain = target_rms / current_rms

        # Limit maximum gain to prevent amplifying noise excessively
        # Max gain of 10x (~20dB boost) for very quiet audio
        gain = min(gain, 10.0)

        # Apply gain
        normalized = audio_data * gain

        # Soft clipping to prevent hard clipping artifacts
        normalized = np.tanh(normalized * 1.2) * 0.9

        return normalized

    def _apply_compression(self, audio_data, threshold=0.6, ratio=3.0):
        """
        Apply dynamic range compression to control peaks while maintaining loudness.

        Args:
            audio_data: numpy array of audio samples
            threshold: level above which compression kicks in (0.6 = -4.4dB)
            ratio: compression ratio (3.0 means 3:1 compression)

        Returns:
            Compressed audio data
        """
        import numpy as np

        # Work with absolute values for compression
        abs_audio = np.abs(audio_data)

        # Calculate compression for samples above threshold
        # Samples below threshold pass through unchanged
        mask = abs_audio > threshold

        if np.any(mask):
            # Amount above threshold
            over = abs_audio[mask] - threshold

            # Compress the overage
            compressed_over = over / ratio

            # Reconstruct: threshold + compressed overage
            abs_audio[mask] = threshold + compressed_over

        # Apply compressed envelope back to original signal (preserving sign)
        sign = np.sign(audio_data)
        compressed = sign * abs_audio

        # Normalize to target level (~-6dB for good headroom)
        target_level = 0.5
        current_peak = np.max(np.abs(compressed))
        if current_peak > 0:
            compressed = compressed * (target_level / current_peak)

        return compressed

    def _apply_filters(self, audio_data, sample_rate):
        """
        Apply audio filters (RNNoise, Noise Gate) based on settings.

        Args:
            audio_data: numpy array of audio samples
            sample_rate: audio sample rate

        Returns:
            Filtered audio data
        """
        from gui.audio_filters import AudioFilterChain

        # Create filter chain
        filter_chain = AudioFilterChain(sample_rate=sample_rate)

        # Add noise gate if enabled
        if self.filter_settings.get('noise_gate_enabled', False):
            filter_chain.add_noise_gate(
                enabled=True,
                threshold_db=self.filter_settings.get('noise_gate_threshold', -32.0),
                attack_ms=self.filter_settings.get('noise_gate_attack', 25.0),
                release_ms=self.filter_settings.get('noise_gate_release', 150.0),
                hold_ms=self.filter_settings.get('noise_gate_hold', 200.0)
            )

        # Add RNNoise if enabled
        if self.filter_settings.get('rnnoise_enabled', False):
            filter_chain.add_rnnoise(enabled=True)

        # Process audio through filter chain
        if filter_chain.filters:
            return filter_chain.process(audio_data)
        else:
            return audio_data

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

            # Device detection - use specified devices or auto-detect
            devices = sd.query_devices()

            # Find microphone - use specified or auto-detect
            mic_device = self.mic_device  # Use user selection if provided
            if mic_device is None:
                # Auto-detect microphone
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

            # Find loopback device - use specified or auto-detect
            loopback_device = self.speaker_device  # Use user selection if provided
            if loopback_device is None:
                # Auto-detect loopback device
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

                # Apply audio filters to microphone
                mic_data = self._apply_filters(mic_data, sample_rate)

                # Normalize microphone audio with AGC
                mic_data = self._normalize_audio(mic_data, target_rms=0.15)

                if speaker_chunks:
                    speaker_data = np.concatenate(speaker_chunks, axis=0)

                    # Apply audio filters to speaker
                    speaker_data = self._apply_filters(speaker_data, sample_rate)

                    # Normalize speaker audio with AGC
                    speaker_data = self._normalize_audio(speaker_data, target_rms=0.12)

                    # Align lengths
                    max_len = max(len(mic_data), len(speaker_data))
                    if len(mic_data) < max_len:
                        mic_data = np.pad(mic_data, ((0, max_len - len(mic_data)), (0, 0)))
                    if len(speaker_data) < max_len:
                        speaker_data = np.pad(speaker_data, ((0, max_len - len(speaker_data)), (0, 0)))

                    # Mix: 60% mic + 40% speaker
                    final_data = (mic_data * 0.6 + speaker_data * 0.4)
                else:
                    final_data = mic_data

                # Final normalization with enhanced compressor (if enabled)
                if self.filter_settings.get('use_enhanced_compressor', False):
                    from gui.audio_filters import EnhancedCompressor
                    compressor = EnhancedCompressor(
                        threshold_db=self.filter_settings.get('compressor_threshold', -18.0),
                        ratio=self.filter_settings.get('compressor_ratio', 3.0),
                        attack_ms=self.filter_settings.get('compressor_attack', 6.0),
                        release_ms=self.filter_settings.get('compressor_release', 60.0),
                        output_gain_db=self.filter_settings.get('compressor_gain', 0.0),
                        sample_rate=sample_rate
                    )
                    final_data = compressor.process(final_data)
                else:
                    # Use original simple compression
                    final_data = self._apply_compression(final_data)

                # Final safety limiting to prevent clipping
                max_val = np.max(np.abs(final_data))
                if max_val > 0.95:
                    final_data = final_data / max_val * 0.95

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

