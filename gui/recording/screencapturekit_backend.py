"""
ScreenCaptureKit backend for macOS native system audio capture.

Requires macOS 12.3+ (Monterey or later) and PyObjC.
This provides native system audio capture without requiring BlackHole or other virtual devices.

WARNING: This is a PARTIAL IMPLEMENTATION. Currently captures microphone only.
System audio capture via ScreenCaptureKit needs to be completed.
"""

import logging
import time
import numpy as np
from typing import Optional
from .base import RecordingBackend, RecordingResult

logger = logging.getLogger(__name__)

# Try to import PyObjC and ScreenCaptureKit
# These imports are wrapped in try/except to avoid crashes on non-macOS systems
# or when PyObjC is not installed
HAS_SCREENCAPTUREKIT = False
AudioCaptureDelegate = None
ScreenCaptureKitBackend = None

try:
    import sounddevice as sd  # Still needed for microphone
    import objc
    from Foundation import NSObject
    from Cocoa import NSApplication
    import AVFoundation
    import ScreenCaptureKit as SCKit

    HAS_SCREENCAPTUREKIT = True

    class AudioCaptureDelegate(NSObject):
        """Delegate to handle audio samples from ScreenCaptureKit stream."""

        def init(self):
            """Initialize the delegate."""
            self = objc.super(AudioCaptureDelegate, self).init()
            if self is None:
                return None
            self.audio_chunks = []
            self.is_recording = True
            self.sample_rate = None
            return self

        def stream_didOutputSampleBuffer_ofType_(self, stream, sample_buffer, sample_type):
            """
            Called when a new audio sample is available.

            NOTE: This implementation is incomplete and not yet functional.
            """
            if not self.is_recording:
                return

            try:
                # TODO: Implement proper CMSampleBuffer handling
                logger.debug("ScreenCaptureKit audio sample received (not yet processed)")
            except Exception as e:
                logger.error(f"Error processing ScreenCaptureKit audio sample: {e}")

        def stream_didStopWithError_(self, stream, error):
            """Called when the stream stops."""
            if error:
                logger.error(f"ScreenCaptureKit stream error: {error}")

    class ScreenCaptureKitBackend(RecordingBackend):
        """
        Recording backend using macOS ScreenCaptureKit for system audio.

        WARNING: PARTIAL IMPLEMENTATION
        - Microphone capture: ✅ Working (via sounddevice)
        - System audio: ⚠️  Not yet implemented (placeholder)

        To complete system audio capture, implement:
        1. Request screen recording permission
        2. Configure SCStreamConfiguration
        3. Create and start SCStream
        4. Process CMSampleBuffer in delegate
        """

        def __init__(self, mic_device: Optional[int] = None,
                     speaker_device: Optional[int] = None):
            """
            Initialize ScreenCaptureKit backend.

            Args:
                mic_device: Device index for microphone (None = auto-detect)
                speaker_device: Ignored for now (system audio not implemented)
            """
            super().__init__(mic_device, speaker_device)

            self.mic_stream = None
            self.system_stream = None
            self.mic_chunks = []
            self.mic_callback_count = 0
            self.mic_sample_rate = None
            self.delegate = None
            self.record_start_time = None

        def start_recording(self) -> None:
            """Start recording microphone (system audio not yet implemented)."""
            logger.info("=== Starting ScreenCaptureKit Recording (Partial) ===")
            logger.warning("ScreenCaptureKit system audio NOT YET IMPLEMENTED - mic only")

            # Start microphone recording using sounddevice
            self._start_microphone()

            # System audio would be started here when implemented
            # self._start_system_audio()

            self.is_recording = True
            self.record_start_time = time.time()
            logger.info("🔴 ScreenCaptureKit recording started (microphone only)")

        def _start_microphone(self) -> None:
            """Start microphone recording using sounddevice."""
            devices = sd.query_devices()

            # Find microphone device
            mic_device = self.mic_device
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
                            if not any(kw in device_name_lower
                                     for kw in ['stereo mix', 'loopback', 'monitor', 'blackhole']):
                                mic_device = idx
                                break

            if mic_device is None:
                raise RuntimeError("No microphone found")

            # Callback for mic audio
            def mic_callback(indata, frames, time_info, status):
                if status:
                    logger.warning(f"Mic callback status: {status}")
                if self.is_recording:
                    self.mic_chunks.append(indata.copy())
                    self.mic_callback_count += 1

            # Try to open mic stream with various sample rates
            mic_info = devices[mic_device]
            mic_capture_rate = int(mic_info.get('default_samplerate', 0) or 0)
            candidate_rates = [r for r in [mic_capture_rate, 48000, 44100, 16000] if r and r > 0]

            for rate in candidate_rates:
                try:
                    self.mic_stream = sd.InputStream(
                        device=mic_device,
                        samplerate=int(rate),
                        channels=1,
                        callback=mic_callback
                    )
                    self.mic_stream.start()
                    self.mic_sample_rate = int(rate)
                    logger.info(f"✅ Mic stream opened: device {mic_device}, rate {rate}Hz")
                    break
                except Exception as e:
                    logger.debug(f"Failed to open mic at {rate}Hz: {e}")
                    continue

            if self.mic_stream is None:
                raise RuntimeError(f"Could not open microphone with any sample rate")

        def _start_system_audio(self) -> None:
            """
            Start system audio capture using ScreenCaptureKit.

            TODO: THIS IS NOT YET IMPLEMENTED

            Implementation steps:
            1. Request screen recording permission
            2. Get shareable content (SCShareableContent)
            3. Create SCStreamConfiguration (audio-only)
            4. Create SCStream with delegate
            5. Start stream
            """
            logger.warning(
                "ScreenCaptureKit system audio capture NOT IMPLEMENTED\n"
                "To complete implementation:\n"
                "  1. Request screen recording permission\n"
                "  2. Configure SCStreamConfiguration for audio-only capture\n"
                "  3. Create and start SCStream with AudioCaptureDelegate\n"
                "  4. Process CMSampleBuffer in delegate callback"
            )

        def stop_recording(self) -> RecordingResult:
            """Stop recording and return collected audio."""
            self.is_recording = False
            duration = time.time() - self.record_start_time if self.record_start_time else 0

            logger.info(f"⏹️  ScreenCaptureKit recording stopped. Duration: {duration:.1f}s")
            logger.info(f"Mic callbacks fired: {self.mic_callback_count}")
            logger.info(f"Mic chunks collected: {len(self.mic_chunks)}")

            # Stop microphone stream
            if self.mic_stream:
                self.mic_stream.stop()
                self.mic_stream.close()

            # Stop system audio stream (when implemented)
            if self.system_stream:
                # TODO: Stop ScreenCaptureKit stream
                pass

            # Process microphone data
            if not self.mic_chunks:
                raise RuntimeError("No audio samples captured from microphone")

            mic_data = np.concatenate(self.mic_chunks, axis=0)
            logger.info(f"Mic data shape: {mic_data.shape}, size: {mic_data.size}")

            # System audio data (not yet captured)
            speaker_data = None
            speaker_sample_rate = None
            speaker_chunks_count = 0

            if self.delegate and hasattr(self.delegate, 'audio_chunks') and self.delegate.audio_chunks:
                # This would work when system audio is implemented
                speaker_data = np.concatenate(self.delegate.audio_chunks, axis=0)
                speaker_sample_rate = self.delegate.sample_rate
                speaker_chunks_count = len(self.delegate.audio_chunks)
                logger.info(f"System audio data shape: {speaker_data.shape}, size: {speaker_data.size}")

            return RecordingResult(
                mic_data=mic_data,
                speaker_data=speaker_data,
                mic_sample_rate=self.mic_sample_rate,
                speaker_sample_rate=speaker_sample_rate,
                duration=duration,
                mic_chunks_count=len(self.mic_chunks),
                speaker_chunks_count=speaker_chunks_count
            )

        def get_backend_name(self) -> str:
            """Return backend name."""
            return "screencapturekit"

        def cleanup(self) -> None:
            """Clean up resources."""
            if self.mic_stream:
                try:
                    self.mic_stream.stop()
                    self.mic_stream.close()
                except:
                    pass

            if self.system_stream:
                try:
                    # TODO: Stop and release ScreenCaptureKit stream
                    pass
                except:
                    pass

except ImportError as e:
    HAS_SCREENCAPTUREKIT = False
    logger.debug(f"ScreenCaptureKit not available: {e}")

    # Create stub class for when PyObjC is not installed
    class ScreenCaptureKitBackend:
        """Stub class when ScreenCaptureKit is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ScreenCaptureKit requires macOS 12.3+ and PyObjC.\n"
                "Install with: pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation"
            )
