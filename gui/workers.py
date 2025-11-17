"""
Qt worker threads for background processing.
"""

import logging
from pathlib import Path
from typing import List

from PySide6.QtCore import QThread, Signal  # type: ignore
from gui.utils import get_platform, get_audio_devices

# Sentinel for following system default output (Windows WASAPI loopback)
DEFAULT_SPEAKER_FOLLOW_SYSTEM = -2

logger = logging.getLogger(__name__)

# BlackHole is the preferred method for system audio capture on macOS
# if ScreenCaptureKit fails or is not desired.
# We will simply check for a device named "BlackHole 2ch".



class RecordingWorker(QThread):
    """Qt worker thread for audio recording with proper signal handling."""

    # Signals for thread-safe communication with main thread
    recording_complete = Signal(str, float)  # (file_path, duration)
    recording_error = Signal(str)  # error_message
    status_update = Signal(str)  # status_message

    def __init__(self, output_dir, mic_device=None, speaker_device=None, parent=None):
        super().__init__(parent)
        self.is_recording = True
        self.output_dir = Path(output_dir)
        self.mic_device = mic_device  # Device index or None for auto-detect
        self.speaker_device = speaker_device  # Device index or None for auto-detect

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
        import numpy as np  # type: ignore

        # Handle empty input
        if audio_data is None or audio_data.size == 0:
            return audio_data

        # Ensure float format to prevent clipping/wrapping issues with int
        audio_data = audio_data.astype(np.float32)

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
        # This will gently compress peaks instead of harsh clipping
        normalized = np.tanh(normalized)

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
        import numpy as np  # type: ignore

        # Handle empty input
        if audio_data is None or audio_data.size == 0:
            return audio_data

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
        if compressed.size == 0:
            return compressed
        current_peak = np.max(np.abs(compressed))
        if current_peak > 0:
            compressed = compressed * (target_level / current_peak)

        return compressed

    def _resample(self, audio_data, from_rate, to_rate):
        try:
            if audio_data is None or audio_data.size == 0 or not from_rate or not to_rate or int(from_rate) == int(to_rate):
                return audio_data
            from scipy.signal import resample_poly  # type: ignore
            import numpy as np  # type: ignore
            import math
            fr = int(from_rate)
            tr = int(to_rate)
            g = math.gcd(fr, tr)
            up = tr // g
            down = fr // g
            mono = audio_data.squeeze()
            y = resample_poly(mono, up, down)
            return y.reshape(-1, 1)
        except Exception:
            try:
                import numpy as np  # type: ignore
                mono = audio_data.squeeze()
                new_len = int(round(len(mono) * float(to_rate) / float(from_rate)))
                x_old = np.linspace(0, 1, len(mono), endpoint=False)
                x_new = np.linspace(0, 1, new_len, endpoint=False)
                y = np.interp(x_new, x_old, mono)
                return y.reshape(-1, 1)
            except Exception:
                return audio_data

    def run(self):
        """Execute recording in background thread."""
        try:
            import sounddevice as sd  # type: ignore
            import numpy as np  # type: ignore
            from pydub import AudioSegment  # type: ignore
            from datetime import datetime

            sample_rate_final = 16000
            mic_chunks = []
            speaker_chunks = []

            logger.info("=== Recording Worker Started ===")
            logger.info(f"Requested devices - Mic: {self.mic_device}, Speaker: {self.speaker_device}")

            # Device detection - use specified devices or auto-detect
            devices = sd.query_devices()
            logger.info(f"Total devices available: {len(devices)}")

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

            # System audio capture: Use BlackHole on macOS, otherwise loopback device
            loopback_device = None
            is_macos = get_platform() == 'macos'

            if is_macos:
                # On macOS, look for BlackHole as the system audio source
                for idx, device in enumerate(devices):
                    if 'blackhole 2ch' in device.get('name', '').lower():
                        loopback_device = idx
                        logger.info(f"Found BlackHole 2ch for system audio capture: {device.get('name','')}")
                        break
                if loopback_device is None:
                    logger.warning("BlackHole 2ch not found. System audio will not be recorded.")
                    logger.info("Please install BlackHole for system audio recording on macOS: https://github.com/ExistentialAudio/BlackHole")

            else:
                # Find loopback device for non-macOS
                loopback_device = self.speaker_device
                if loopback_device is None:
                    # Auto-detect loopback device
                    try:
                        hostapis = sd.query_hostapis()
                    except Exception:
                        hostapis = []
                    # 1) Prefer input-capable devices with loopback/monitor names
                    for idx, device in enumerate(devices):
                        if idx == mic_device:
                            continue
                        try:
                            device_name_lower = str(device.get('name', '')).lower()
                            matches_loopback = any(kw in device_name_lower for kw in ['stereo mix', 'loopback', 'monitor', 'speakers wave', 'blackhole', 'soundflower', 'steam'])
                            if device.get('max_input_channels', 0) > 0 and matches_loopback:
                                loopback_device = idx
                                logger.info(f"Auto-detected loopback device (monitor/input): {device.get('name','')}")
                                break
                        except Exception:
                            continue
                    # 2) Fallback: WASAPI output-only devices (skip non-WASAPI outputs)
                    if loopback_device is None:
                        for idx, device in enumerate(devices):
                            if idx == mic_device:
                                continue
                            try:
                                if device.get('max_output_channels', 0) > 0 and device.get('max_input_channels', 0) == 0:
                                    ha_idx = device.get('hostapi', None)
                                    ha_name = ''
                                    try:
                                        if ha_idx is not None:
                                            ha_name = sd.query_hostapis()[ha_idx]['name'].lower()
                                    except Exception:
                                        ha_name = ''
                                    if 'wasapi' in ha_name:
                                        loopback_device = idx
                                        logger.info(f"Auto-detected WASAPI output for loopback: {device.get('name','')}")
                                        break
                            except Exception:
                                continue

            # Callbacks with debug tracking
            mic_callback_count = [0]  # Use list to allow modification in nested function

            def mic_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Mic callback status: {status}")
                if self.is_recording:
                    mic_chunks.append(indata.copy())
                    mic_callback_count[0] += 1

            def speaker_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Speaker callback status: {status}")
                if self.is_recording:
                    speaker_chunks.append(indata.copy())

            # Start mic stream (use device default sample rate with fallback)
            mic_capture_rate = None
            mic_stream = None
            open_errors = []
            try:
                mic_info = devices[mic_device]
                mic_capture_rate = int(mic_info.get('default_samplerate', 0) or 0)
            except Exception:
                mic_capture_rate = 0
            candidate_rates = [r for r in [mic_capture_rate, 48000, 44100, 32000, 16000] if r and r > 0]
            for r in candidate_rates:
                try:
                    mic_stream = sd.InputStream(device=mic_device, samplerate=int(r), channels=1, callback=mic_callback)
                    mic_stream.start()
                    mic_capture_rate = int(r)
                    logger.info(f"✅ Mic stream opened: device {mic_device}, rate {r}Hz")
                    break
                except Exception as e:
                    open_errors.append(str(e))
                    mic_stream = None
                    logger.debug(f"Failed to open mic at {r}Hz: {e}")
                    continue
            if mic_stream is None:
                error_details = "\n".join([f"  - {rate}Hz: {err}" for rate, err in zip(candidate_rates, open_errors)])
                logger.error(f"Failed to open microphone. Tried rates:\n{error_details}")
                self.recording_error.emit(
                    f"❌ Could not open microphone with any sample rate.\n\n"
                    f"Tried: {', '.join(str(r) for r in candidate_rates)}Hz\n\n"
                    f"Try: Change Windows sound format to 48000Hz or 44100Hz\n"
                    f"(Right-click speaker icon → Sound Settings → Device Properties → Advanced)"
                )
                return

            # Start speaker/loopback stream if not using ScreenCaptureKit
            speaker_stream = None
            speaker_capture_rate = None
            if loopback_device is not None:
                try:
                    # Follow system default output (Windows)
                    target_device = loopback_device
                    if loopback_device == DEFAULT_SPEAKER_FOLLOW_SYSTEM and get_platform() == 'windows':
                        try:
                            out_index = sd.default.device[1]
                        except Exception:
                            out_index = None
                        if out_index is not None and isinstance(out_index, int) and out_index >= 0:
                            target_device = out_index
                        else:
                            # Fallback: first output-capable device
                            target_device = None
                            for i, d in enumerate(devices):
                                if d.get('max_output_channels', 0) > 0:
                                    target_device = i
                                    logger.info(f"Follow-system fallback selected output device idx {i}: {d.get('name','')} ")
                                    break
                            if target_device is None:
                                logger.warning("No usable default output device found for loopback recording; skipping speaker capture")

                    # Get device info to determine channel count
                    if target_device is None:
                        loopback_info = None
                    else:
                        loopback_info = devices[target_device]

                    # For output devices, use their output channel count
                    # For input monitors, use input channel count
                    if loopback_info and loopback_info['max_output_channels'] > 0 and loopback_info['max_input_channels'] == 0:
                        # Pure output device - use output channels for loopback
                        # Note: Some backends (WASAPI) support recording from output devices
                        # Only proceed if host API is WASAPI; otherwise skip output-only devices
                        try:
                            ha_name = sd.query_hostapis()[loopback_info['hostapi']]['name'].lower()
                        except Exception:
                            ha_name = ''
                        if 'wasapi' not in ha_name:
                            logger.info("Skipping non-WASAPI output device for loopback; selecting mic-only recording")
                            loopback_channels = 0
                            speaker_rate = mic_capture_rate or sample_rate_final
                            speaker_capture_rate = speaker_rate
                        else:
                            loopback_channels = min(loopback_info['max_output_channels'], 2)  # Use stereo max
                            logger.info(f"Opening loopback stream on WASAPI output with {loopback_channels} channel(s)")
                            # Prefer device default sample rate for compatibility
                            speaker_rate = int(loopback_info.get('default_samplerate', mic_capture_rate or sample_rate_final) or (mic_capture_rate or sample_rate_final))
                            speaker_capture_rate = speaker_rate
                    else:
                        # Input monitor device - use input channels
                        if loopback_info:
                            loopback_channels = min(loopback_info['max_input_channels'], 2)
                            # For BlackHole and other virtual devices, match the mic rate
                            speaker_rate = int(loopback_info.get('default_samplerate', mic_capture_rate or sample_rate_final) or (mic_capture_rate or sample_rate_final))
                            speaker_capture_rate = speaker_rate
                        else:
                            loopback_channels = 0
                            speaker_rate = mic_capture_rate or sample_rate_final
                        logger.info(f"Opening loopback stream on input device with {loopback_channels} channel(s)")

                    # Create callback that handles multi-channel and downmixes to mono
                    original_speaker_callback = speaker_callback
                    def multi_channel_speaker_callback(indata, frames, time_info, status):
                        if self.is_recording:
                            # Downmix to mono if stereo
                            if indata.shape[1] > 1:
                                mono_data = np.mean(indata, axis=1, keepdims=True)
                            else:
                                mono_data = indata
                            speaker_chunks.append(mono_data.copy())

                    extra = None
                    try:
                        if loopback_info and 'wasapi' in sd.query_hostapis()[loopback_info['hostapi']]['name'].lower():
                            extra = sd.WasapiSettings(loopback=True)
                    except Exception:
                        extra = None

                    if target_device is not None and loopback_channels > 0:
                        speaker_stream = sd.InputStream(
                            device=target_device,
                            samplerate=speaker_rate,
                            channels=loopback_channels,
                            callback=multi_channel_speaker_callback,
                            extra_settings=extra
                        )
                        speaker_stream.start()
                        logger.info(f"✅ Speaker stream opened: device {target_device}, rate {speaker_rate}Hz, channels {loopback_channels}")
                    else:
                        logger.warning("Skipping speaker capture due to unresolved output device or channel count")
                except Exception as e:
                    logger.warning(f"Could not open loopback stream on device {loopback_device}: {e}")
                    logger.info("Recording will continue with microphone only")

            # Record while active
            import time
            record_start = time.time()

            logger.info(f"🔴 Recording started at {record_start}")
            logger.info(f"is_recording = {self.is_recording}")

            while self.is_recording:
                sd.sleep(100)

            # Stop streams
            logger.info(f"⏹️  Recording stopped. Duration: {time.time() - record_start:.1f}s")
            logger.info(f"Mic callbacks fired: {mic_callback_count[0]}")
            logger.info(f"Mic chunks collected: {len(mic_chunks)}")
            logger.info(f"Speaker chunks collected: {len(speaker_chunks)}")

            mic_stream.stop()
            mic_stream.close()
            if speaker_stream:
                speaker_stream.stop()
                speaker_stream.close()

            # Process and save
            if mic_chunks:
                mic_data = np.concatenate(mic_chunks, axis=0)
                logger.info(f"Mic data shape after concatenate: {mic_data.shape}, size: {mic_data.size}")
                if mic_data.size == 0:
                    logger.error("Mic data is empty after concatenation!")
                    self.recording_error.emit("❌ No audio captured from microphone; please try again")
                    return
            else:
                logger.error(f"❌ CRITICAL: mic_chunks is empty! Callbacks fired: {mic_callback_count[0]}, is_recording was: {self.is_recording}")
                self.recording_error.emit(
                    f"❌ No audio samples captured!\n\n"
                    f"Debug info:\n"
                    f"- Mic callbacks fired: {mic_callback_count[0]}\n"
                    f"- Recording duration: {time.time() - record_start:.1f}s\n"
                    f"- Device: {mic_device}\n\n"
                    f"Try:\n"
                    f"1. Check if microphone is working in other apps\n"
                    f"2. Try a different microphone from the dropdown\n"
                    f"3. Run: python diagnose_audio.py"
                )
                return

            # Resample mic to final rate if needed
            if mic_capture_rate and mic_capture_rate != sample_rate_final:
                mic_data = self._resample(mic_data, mic_capture_rate, sample_rate_final)

            if speaker_chunks:
                speaker_data = np.concatenate(speaker_chunks, axis=0)
                if speaker_data.size == 0:
                    speaker_data = None

                # Resample speaker to final rate if needed
                if speaker_capture_rate and speaker_capture_rate != sample_rate_final:
                    speaker_data = self._resample(speaker_data, speaker_capture_rate, sample_rate_final)

                if speaker_data is not None:
                    # Align lengths before mixing
                    max_len = max(len(mic_data), len(speaker_data))
                    if len(mic_data) < max_len:
                        mic_data = np.pad(mic_data, ((0, max_len - len(mic_data)), (0, 0)))
                    if len(speaker_data) < max_len:
                        speaker_data = np.pad(speaker_data, ((0, max_len - len(speaker_data)), (0, 0)))

                    # Mix by averaging to prevent clipping before normalization
                    final_data = (mic_data + speaker_data) / 2.0
                else:
                    final_data = mic_data
            else:
                final_data = mic_data

            if final_data is None or final_data.size == 0:
                logger.error(f"Final data is empty! mic_data size: {mic_data.size if 'mic_data' in locals() else 'N/A'}")
                self.recording_error.emit("❌ Recording error: no audio samples captured")
                return

            # Normalize the final mixed audio
            final_data = self._normalize_audio(final_data, target_rms=0.12)

            # Final safety limiting to prevent clipping
            if final_data.size > 0:
                max_val = np.max(np.abs(final_data))
                if max_val > 0.98:
                    final_data = final_data / max_val * 0.98

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
                frame_rate=sample_rate_final,
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
                    wf.setframerate(sample_rate_final)
                    wf.writeframes(final_data_int16.tobytes())
                recorded_path = wav_path

            duration = len(final_data) / sample_rate_final
            logger.info(f"✅ Recording saved: {recorded_path} ({duration:.1f}s)")

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

