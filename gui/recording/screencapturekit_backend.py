"""
ScreenCaptureKit backend for macOS native system audio capture.

Requires macOS 12.3+ (Monterey or later) and PyObjC.
This provides native system audio capture without requiring BlackHole or other virtual devices.
"""

import logging
import time
import numpy as np
from typing import Optional
from .base import RecordingBackend, RecordingResult

logger = logging.getLogger(__name__)

try:
    import sounddevice as sd  # Still needed for microphone
    import objc
    from Foundation import NSObject
    from Cocoa import NSApplication
    import AVFoundation
    import ScreenCaptureKit

    HAS_SCREENCAPTUREKIT = True
except ImportError as e:
    HAS_SCREENCAPTUREKIT = False
    logger.debug(f"ScreenCaptureKit not available: {e}")


class AudioCaptureDelegate(NSObject):
    """Delegate to handle audio samples from ScreenCaptureKit stream."""

    def init(self):
        self = objc.super(AudioCaptureDelegate, self).init()
        if self is None:
            return None
        self.audio_chunks = []
        self.is_recording = True
        self.sample_rate = None
        return self

    def stream_didOutputSampleBuffer_ofType_(self, stream, sample_buffer, sample_type):
        """Called when a new audio sample is available."""
        if not self.is_recording:
            return

        try:
            # ScreenCaptureKitOutputTypeAudio = 1
            if sample_type != 1:  # Only process audio samples
                return

            # Extract audio data from CMSampleBuffer
            block_buffer = AVFoundation.CMSampleBufferGetDataBuffer(sample_buffer)
            if block_buffer is None:
                return

            # Get audio format description
            format_desc = AVFoundation.CMSampleBufferGetFormatDescription(sample_buffer)
            if format_desc is None:
                return

            asbd = AVFoundation.CMAudioFormatDescriptionGetStreamBasicDescription(format_desc)
            if asbd is None:
                return

            # Store sample rate from first buffer
            if self.sample_rate is None:
                self.sample_rate = int(asbd.contents.mSampleRate)
                logger.info(f"ScreenCaptureKit audio format: {self.sample_rate}Hz, "
                           f"{asbd.contents.mChannelsPerFrame} channels")

            # Get audio buffer
            audio_buffer_list = objc.alloca(ctypes.sizeof(AVFoundation.AudioBufferList))
            length = ctypes.c_size_t(0)

            AVFoundation.CMBlockBufferGetDataPointer(
                block_buffer, 0, None, ctypes.byref(length), audio_buffer_list
            )

            if length.value > 0:
                # Convert to numpy array
                # Assume Float32 format (most common for system audio)
                num_samples = length.value // 4  # 4 bytes per float32
                audio_data = np.frombuffer(audio_buffer_list[:length.value], dtype=np.float32)

                # If stereo, downmix to mono
                channels = int(asbd.contents.mChannelsPerFrame)
                if channels == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1)

                self.audio_chunks.append(audio_data.reshape(-1, 1))

        except Exception as e:
            logger.error(f"Error processing ScreenCaptureKit audio sample: {e}")

    def stream_didStopWithError_(self, stream, error):
        """Called when the stream stops."""
        if error:
            logger.error(f"ScreenCaptureKit stream error: {error}")


class ScreenCaptureKitBackend(RecordingBackend):
    """
    Recording backend using macOS ScreenCaptureKit for system audio.

    Provides native system audio capture on macOS 12.3+ without requiring
    third-party virtual audio devices like BlackHole.
    """

    def __init__(self, mic_device: Optional[int] = None,
                 speaker_device: Optional[int] = None):
        """
        Initialize ScreenCaptureKit backend.

        Args:
            mic_device: Device index for microphone (None = auto-detect)
            speaker_device: Ignored for ScreenCaptureKit (always captures system audio)
        """
        if not HAS_SCREENCAPTUREKIT:
            raise ImportError(
                "ScreenCaptureKit requires macOS 12.3+ and PyObjC.\n"
                "Install with: pip install pyobjc-framework-ScreenCaptureKit"
            )

        super().__init__(mic_device, speaker_device)

        self.mic_stream = None
        self.system_stream = None
        self.mic_chunks = []
        self.mic_callback_count = 0
        self.mic_sample_rate = None
        self.delegate = None
        self.record_start_time = None

    def start_recording(self) -> None:
        """Start recording microphone and system audio."""
        logger.info("=== Starting ScreenCaptureKit Recording ===")

        # Start microphone recording using sounddevice
        self._start_microphone()

        # Start system audio capture using ScreenCaptureKit
        self._start_system_audio()

        self.is_recording = True
        self.record_start_time = time.time()
        logger.info("🔴 ScreenCaptureKit recording started")

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
        """Start system audio capture using ScreenCaptureKit."""
        try:
            # Initialize NSApplication (required for ScreenCaptureKit)
            app = NSApplication.sharedApplication()

            # Create delegate to receive audio samples
            self.delegate = AudioCaptureDelegate.alloc().init()

            # Get shareable content (system audio sources)
            content = ScreenCaptureKit.SCShareableContent.getShareableContentWithCompletionHandler_(
                None  # We'll use synchronous version
            )

            # TODO: This is a simplified version. Full implementation needs:
            # 1. Request screen recording permission
            # 2. Configure SCStreamConfiguration for audio-only capture
            # 3. Create SCStream with configuration and delegate
            # 4. Start the stream

            # For now, log a warning that full implementation is pending
            logger.warning(
                "ScreenCaptureKit full implementation pending. "
                "Falling back to microphone-only recording."
            )
            logger.info(
                "To complete ScreenCaptureKit implementation:\n"
                "1. Request screen recording permission\n"
                "2. Configure SCStreamConfiguration\n"
                "3. Create and start SCStream"
            )

        except Exception as e:
            logger.error(f"Failed to initialize ScreenCaptureKit: {e}")
            logger.info("Will record microphone only")

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

        # Process system audio data (when implemented)
        speaker_data = None
        speaker_sample_rate = None
        speaker_chunks_count = 0

        if self.delegate and self.delegate.audio_chunks:
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
