"""
ScreenCaptureKit backend for macOS native system audio capture.

Requires macOS 12.3+ (Monterey or later) and PyObjC.
This provides native system audio capture WITHOUT requiring BlackHole or other virtual devices.

This is the COMPLETE implementation for native macOS audio capture.
"""

import logging
import time
import numpy as np
from typing import Optional
from .base import RecordingBackend, RecordingResult

logger = logging.getLogger(__name__)

# Try to import PyObjC and ScreenCaptureKit
HAS_SCREENCAPTUREKIT = False
AudioCaptureDelegate = None
ScreenCaptureKitBackend = None

try:
    import sounddevice as sd  # For microphone
    import objc
    from Foundation import NSObject, NSError
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
            self.sample_rate = 48000  # Default, will be updated from actual stream
            self.channels = 2
            return self

        def stream_didOutputSampleBuffer_ofType_(self, stream, sample_buffer, output_type):
            """
            Called when ScreenCaptureKit outputs a new sample buffer.

            Args:
                stream: SCStream instance
                sample_buffer: CMSampleBuffer containing audio data
                output_type: SCStreamOutputType (1 = audio)
            """
            if not self.is_recording:
                return

            try:
                # Check if this is audio (SCStreamOutputTypeAudio = 1)
                if output_type != 1:
                    return

                # Get audio format description
                format_desc = AVFoundation.CMSampleBufferGetFormatDescription(sample_buffer)
                if format_desc is None:
                    logger.warning("No format description in sample buffer")
                    return

                # Get audio stream basic description
                # Note: This returns a pointer to the ASBD struct
                asbd_ptr = AVFoundation.CMAudioFormatDescriptionGetStreamBasicDescription(format_desc)
                if asbd_ptr is None:
                    logger.warning("No audio stream basic description")
                    return

                # Extract sample rate and channel count from the ASBD
                # The ASBD is a C struct, access fields using attribute names
                if self.sample_rate == 48000:  # First time only
                    try:
                        # Try to access as struct
                        self.sample_rate = int(asbd_ptr.mSampleRate)
                        self.channels = int(asbd_ptr.mChannelsPerFrame)
                    except AttributeError:
                        # If that fails, ASBD might be accessed differently in PyObjC
                        # Extract basic format information from format description instead
                        try:
                            # Get audio format list (alternative method)
                            audio_format_list = AVFoundation.CMAudioFormatDescriptionGetFormatList(format_desc)
                            if audio_format_list:
                                # Use first format
                                first_format = audio_format_list[0]
                                self.sample_rate = int(first_format.mSampleRate)
                                self.channels = int(first_format.mChannelsPerFrame)
                            else:
                                # Fall back to 48kHz stereo (standard for system audio)
                                logger.warning("Could not extract ASBD, using defaults: 48kHz, 2 channels")
                                self.sample_rate = 48000
                                self.channels = 2
                        except:
                            # Last resort: use defaults
                            logger.warning("Failed to get audio format, using defaults: 48kHz, 2 channels")
                            self.sample_rate = 48000
                            self.channels = 2

                    logger.info(f"ScreenCaptureKit audio: {self.sample_rate}Hz, {self.channels} channels")

                # Get audio buffer from sample buffer
                block_buffer = AVFoundation.CMSampleBufferGetDataBuffer(sample_buffer)
                if block_buffer is None:
                    return

                # Get the raw audio data from CMBlockBuffer
                # ScreenCaptureKit provides Float32 PCM audio data
                try:
                    # Get buffer length
                    buffer_length = AVFoundation.CMBlockBufferGetDataLength(block_buffer)
                    if buffer_length == 0:
                        return

                    # Allocate buffer to copy data into
                    buffer = objc.allocate_buffer(buffer_length)

                    # Copy data from block buffer
                    status = AVFoundation.CMBlockBufferCopyDataBytes(
                        block_buffer,
                        0,  # offsetToData
                        buffer_length,  # dataLength
                        buffer  # destination
                    )

                    if status != 0:
                        logger.warning(f"CMBlockBufferCopyDataBytes failed with status {status}")
                        return

                    # Convert to numpy array (Float32 PCM)
                    audio_data = np.frombuffer(buffer, dtype=np.float32, count=buffer_length // 4)

                except Exception as e:
                    logger.debug(f"Failed to extract audio buffer: {e}")
                    return

                # Handle stereo -> mono conversion
                if self.channels == 2 and len(audio_data) >= 2:
                    # Reshape to (samples, channels) and average to mono
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1)

                # Store as column vector for consistency
                if len(audio_data) > 0:
                    self.audio_chunks.append(audio_data.reshape(-1, 1))

            except Exception as e:
                logger.error(f"Error processing ScreenCaptureKit audio: {e}", exc_info=True)

        def stream_didStopWithError_(self, stream, error):
            """Called when the stream stops."""
            if error:
                logger.error(f"ScreenCaptureKit stream error: {error}")
            else:
                logger.info("ScreenCaptureKit stream stopped normally")

    class ScreenCaptureKitBackend(RecordingBackend):
        """
        Recording backend using macOS ScreenCaptureKit for native system audio.

        Captures:
        - Microphone: via sounddevice (standard input)
        - System audio: via ScreenCaptureKit (no BlackHole needed!)

        Requires:
        - macOS 12.3+ (Monterey or later)
        - PyObjC with ScreenCaptureKit framework
        - Screen recording permission
        """

        def __init__(self, mic_device: Optional[int] = None,
                     speaker_device: Optional[int] = None):
            """
            Initialize ScreenCaptureKit backend.

            Args:
                mic_device: Device index for microphone (None = auto-detect)
                speaker_device: Ignored (ScreenCaptureKit captures system audio directly)
            """
            super().__init__(mic_device, speaker_device)

            self.mic_stream = None
            self.screen_stream = None
            self.mic_chunks = []
            self.mic_callback_count = 0
            self.mic_sample_rate = None
            self.delegate = None
            self.record_start_time = None

        def start_recording(self) -> None:
            """Start recording microphone and system audio."""
            logger.info("=== Starting ScreenCaptureKit Recording ===")

            # Start microphone first
            self._start_microphone()

            # Start system audio via ScreenCaptureKit
            self._start_system_audio()

            self.is_recording = True
            self.record_start_time = time.time()
            logger.info("🔴 ScreenCaptureKit recording started (mic + system audio)")

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
                            # Skip virtual devices
                            if not any(kw in device_name_lower
                                     for kw in ['blackhole', 'loopback', 'virtual']):
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

            # Try to open mic stream
            mic_info = devices[mic_device]
            mic_rate = int(mic_info.get('default_samplerate', 0) or 48000)
            candidate_rates = [r for r in [mic_rate, 48000, 44100, 16000] if r > 0]

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
                    return
                except Exception as e:
                    logger.debug(f"Failed to open mic at {rate}Hz: {e}")

            raise RuntimeError("Could not open microphone")

        def _start_system_audio(self) -> None:
            """
            Start system audio capture using ScreenCaptureKit.

            This captures all system audio natively without requiring BlackHole!
            """
            try:
                # Initialize NSApplication (required for ScreenCaptureKit)
                app = NSApplication.sharedApplication()

                # Check if we can use ScreenCaptureKit (basic check)
                # The actual permission check happens when we try to start the stream
                logger.info("Initializing ScreenCaptureKit for system audio capture")
                logger.info("Note: This requires Screen Recording permission")
                logger.info("If this is the first time, macOS will prompt for permission")

                # Create and initialize delegate
                self.delegate = AudioCaptureDelegate.alloc().init()
                logger.info("Created ScreenCaptureKit delegate")

                # Get shareable content (asynchronously)
                # We need displays to create a proper content filter
                def content_completion(content, error):
                    if error:
                        logger.error(f"Failed to get shareable content: {error}")
                        return

                    if not content:
                        logger.error("No shareable content available")
                        return

                    logger.info("Got shareable content, configuring stream...")

                    # Get the main display for audio capture
                    displays = content.displays()
                    if not displays or len(displays) == 0:
                        logger.error("No displays found for ScreenCaptureKit")
                        return

                    main_display = displays[0]
                    logger.info(f"Using display: {main_display.displayID()}")

                    # Create stream configuration for audio-only capture
                    config = SCKit.SCStreamConfiguration.alloc().init()

                    # Configure for audio capture
                    config.setCapturesAudio_(True)  # Enable audio capture
                    config.setExcludesCurrentProcessAudio_(True)  # Don't capture our own app

                    # Set high quality audio
                    config.setChannelCount_(2)  # Stereo
                    config.setSampleRate_(48000)  # 48kHz (standard for system audio)

                    # Minimize video capture (we only want audio)
                    config.setWidth_(2)  # Minimum width (1 causes issues)
                    config.setHeight_(2)  # Minimum height
                    # Set minimum frame rate for video (we don't care about video, only audio)
                    try:
                        # Create CMTime for 1 fps (value=1, timescale=1)
                        min_frame_interval = AVFoundation.CMTimeMake(1, 1)
                        config.setMinimumFrameInterval_(min_frame_interval)
                    except:
                        pass  # Not critical, we only need audio
                    config.setQueueDepth_(3)  # Small queue

                    # Create content filter with the main display
                    # This captures all audio from this display (system audio)
                    content_filter = SCKit.SCContentFilter.alloc().initWithDisplay_excludingWindows_(
                        main_display,
                        []  # Don't exclude any windows
                    )

                    if not content_filter:
                        logger.error("Failed to create content filter")
                        return

                    logger.info("Created content filter for display audio")

                    # Create stream
                    self.screen_stream = SCKit.SCStream.alloc().initWithFilter_configuration_delegate_(
                        content_filter,
                        config,
                        self.delegate
                    )

                    if self.screen_stream is None:
                        logger.error("Failed to create ScreenCaptureKit stream")
                        return

                    logger.info("Created SCStream, starting capture...")

                    # Add audio output to the stream
                    # This is CRITICAL for audio capture
                    try:
                        self.screen_stream.addStreamOutput_type_sampleHandlerQueue_error_(
                            self.delegate,
                            1,  # SCStreamOutputTypeAudio
                            None,  # Use default queue
                            None
                        )
                        logger.info("Added audio output handler to stream")
                    except Exception as e:
                        logger.warning(f"Could not add stream output (may not be needed): {e}")

                    # Start the stream
                    def start_completion(error):
                        if error:
                            logger.error(f"Failed to start stream: {error}")
                            logger.info("Check System Settings → Privacy & Security → Screen Recording")
                        else:
                            logger.info("✅ ScreenCaptureKit system audio stream started")

                    self.screen_stream.startCaptureWithCompletionHandler_(start_completion)

                # Get shareable content
                SCKit.SCShareableContent.getShareableContentWithCompletionHandler_(content_completion)

                # Give it a moment to initialize
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Failed to start ScreenCaptureKit: {e}", exc_info=True)
                logger.warning("Will record microphone only")

        def stop_recording(self) -> RecordingResult:
            """Stop recording and return collected audio."""
            self.is_recording = False
            duration = time.time() - self.record_start_time if self.record_start_time else 0

            logger.info(f"⏹️  Recording stopped. Duration: {duration:.1f}s")

            # Stop ScreenCaptureKit stream first
            if self.screen_stream:
                try:
                    def stop_completion(error):
                        if error:
                            logger.error(f"Error stopping stream: {error}")

                    self.screen_stream.stopCaptureWithCompletionHandler_(stop_completion)
                    time.sleep(0.2)  # Allow stream to stop
                except Exception as e:
                    logger.warning(f"Error stopping ScreenCaptureKit stream: {e}")

            # Stop microphone
            if self.mic_stream:
                self.mic_stream.stop()
                self.mic_stream.close()

            logger.info(f"Mic chunks collected: {len(self.mic_chunks)}")
            logger.info(f"System audio chunks collected: {len(self.delegate.audio_chunks) if self.delegate else 0}")

            # Process microphone data
            if not self.mic_chunks:
                raise RuntimeError("No audio samples captured from microphone")

            mic_data = np.concatenate(self.mic_chunks, axis=0)
            logger.info(f"Mic data: {mic_data.shape}, {mic_data.size} samples")

            # Process system audio data
            speaker_data = None
            speaker_sample_rate = None
            speaker_chunks_count = 0

            if self.delegate and self.delegate.audio_chunks:
                speaker_data = np.concatenate(self.delegate.audio_chunks, axis=0)
                speaker_sample_rate = self.delegate.sample_rate
                speaker_chunks_count = len(self.delegate.audio_chunks)
                logger.info(f"System audio data: {speaker_data.shape}, {speaker_data.size} samples")

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

            if self.screen_stream:
                try:
                    self.screen_stream.stopCaptureWithCompletionHandler_(lambda error: None)
                except:
                    pass

except ImportError as e:
    HAS_SCREENCAPTUREKIT = False
    logger.debug(f"ScreenCaptureKit not available: {e}")

    # Create stub class when PyObjC is not installed
    class ScreenCaptureKitBackend:
        """Stub class when ScreenCaptureKit is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "ScreenCaptureKit requires macOS 12.3+ and PyObjC.\n"
                "Install with: pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation pyobjc-framework-Cocoa"
            )
