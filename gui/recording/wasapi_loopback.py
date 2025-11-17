"""
WASAPI Loopback Capture for Windows

This module implements system audio capture using Windows Audio Session API (WASAPI)
in loopback mode, allowing direct capture of the audio stream going to the speakers
without requiring Stereo Mix or virtual audio cables.

This is the same approach used by OBS, Discord, and other professional applications.
"""

import logging
import threading
import time
import numpy as np
from typing import Optional, Callable
from ctypes import POINTER, cast, c_float, c_int16, c_uint8
import comtypes

logger = logging.getLogger(__name__)


class WASAPILoopbackCapture:
    """
    Captures system audio using WASAPI loopback mode.

    This directly accesses the Windows audio subsystem to capture the digital
    audio stream before it reaches the speakers, providing:
    - No dependency on Stereo Mix or virtual cables
    - Better audio quality (no analog conversion)
    - Lower latency
    - Works on all Windows Vista+ systems
    """

    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize WASAPI loopback capture.

        Args:
            callback: Function to call with captured audio data (numpy array)
        """
        self.callback = callback
        self.is_capturing = False
        self.capture_thread = None
        self.audio_chunks = []
        self.sample_rate = None
        self.channels = None

        # COM interfaces (will be initialized in start())
        self.device_enumerator = None
        self.device = None
        self.audio_client = None
        self.capture_client = None
        self.wave_format = None

    def start(self) -> None:
        """Start capturing system audio."""
        if self.is_capturing:
            logger.warning("WASAPI capture already running")
            return

        logger.info("🔴 Starting WASAPI loopback capture...")

        try:
            # Initialize COM
            comtypes.CoInitialize()

            # Import Windows audio interfaces
            from comtypes import CLSCTX_ALL, GUID

            try:
                from pycaw.constants import CLSID_MMDeviceEnumerator
                import pycaw.api.mmdeviceapi as mmdeviceapi
                import pycaw.api.audioclient as audioclient
            except ImportError:
                logger.error("pycaw library not found. Install with: pip install pycaw comtypes")
                raise

            # Define GUIDs that pycaw doesn't provide
            IID_IAudioClient = GUID('{1CB9AD4C-DBFA-4c32-B178-C2F568A703B2}')
            IID_IAudioCaptureClient = GUID('{C8ADBD64-E71E-48a0-A4DE-185C395CD317}')

            # Get device enumerator
            self.device_enumerator = comtypes.CoCreateInstance(
                CLSID_MMDeviceEnumerator,
                mmdeviceapi.IMMDeviceEnumerator,
                CLSCTX_ALL
            )

            # Get default audio endpoint (speakers/headphones)
            # eRender = 0 (output device), eConsole = 0 (default device role)
            self.device = self.device_enumerator.GetDefaultAudioEndpoint(
                0,  # eRender - output device
                0   # eConsole - console role
            )

            device_id = self.device.GetId()
            logger.info(f"Using default output device: {device_id}")

            # Activate audio client
            self.audio_client = self.device.Activate(
                IID_IAudioClient,
                CLSCTX_ALL,
                None
            )

            # Get the audio format
            self.wave_format = self.audio_client.GetMixFormat()

            # Log audio format details
            self.sample_rate = self.wave_format.contents.nSamplesPerSec
            self.channels = self.wave_format.contents.nChannels
            bits_per_sample = self.wave_format.contents.wBitsPerSample

            logger.info(f"Audio format: {self.sample_rate}Hz, {self.channels}ch, {bits_per_sample}bit")

            # Initialize audio client in loopback mode
            AUDCLNT_STREAMFLAGS_LOOPBACK = 0x00020000
            AUDCLNT_SHAREMODE_SHARED = 0

            # Reference time units (100-nanosecond intervals)
            # 10,000,000 = 1 second
            buffer_duration = 10000000  # 1 second

            self.audio_client.Initialize(
                AUDCLNT_SHAREMODE_SHARED,
                AUDCLNT_STREAMFLAGS_LOOPBACK,
                buffer_duration,
                0,  # Periodicity (must be 0 for shared mode)
                self.wave_format,
                None  # Audio session GUID
            )

            # Get the capture client
            self.capture_client = self.audio_client.GetService(
                IID_IAudioCaptureClient
            )

            # Start the audio client
            self.audio_client.Start()

            # Start capture thread
            self.is_capturing = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()

            logger.info("✅ WASAPI loopback capture started successfully")

        except Exception as e:
            logger.error(f"❌ Failed to start WASAPI capture: {e}", exc_info=True)
            self.cleanup()
            raise

    def _capture_loop(self) -> None:
        """Main capture loop running in separate thread."""
        logger.info("WASAPI capture loop started")

        try:
            while self.is_capturing:
                try:
                    # Get next packet size
                    packet_length = self.capture_client.GetNextPacketSize()

                    while packet_length > 0:
                        # Get the buffer
                        data_pointer, num_frames, flags, position, qpc_position = \
                            self.capture_client.GetBuffer()

                        if num_frames > 0:
                            # Convert pointer to numpy array based on format
                            total_samples = num_frames * self.channels

                            if self.wave_format.contents.wBitsPerSample == 32:
                                # Float32 format - most common for WASAPI
                                buffer = (c_float * total_samples).from_address(data_pointer)
                                audio_data = np.frombuffer(buffer, dtype=np.float32).copy()
                            elif self.wave_format.contents.wBitsPerSample == 16:
                                # Int16 format - convert to float32
                                buffer = (c_int16 * total_samples).from_address(data_pointer)
                                audio_data = np.frombuffer(buffer, dtype=np.int16).astype(np.float32) / 32768.0
                            else:
                                # Unsupported format - log and skip
                                logger.warning(f"Unsupported bit depth: {self.wave_format.contents.wBitsPerSample}")
                                self.capture_client.ReleaseBuffer(num_frames)
                                packet_length = self.capture_client.GetNextPacketSize()
                                continue

                            # Reshape to (frames, channels)
                            audio_data = audio_data.reshape(num_frames, self.channels)

                            # Store chunk
                            self.audio_chunks.append(audio_data.copy())

                            # Call callback if provided
                            if self.callback:
                                self.callback(audio_data, num_frames, None, None)

                            # Log first few chunks for debugging
                            if len(self.audio_chunks) <= 3:
                                logger.info(f"📥 WASAPI chunk #{len(self.audio_chunks)}: "
                                          f"{audio_data.shape}, "
                                          f"min={audio_data.min():.6f}, "
                                          f"max={audio_data.max():.6f}")

                        # Release the buffer
                        self.capture_client.ReleaseBuffer(num_frames)

                        # Get next packet size
                        packet_length = self.capture_client.GetNextPacketSize()

                    # Small delay to prevent CPU spinning
                    time.sleep(0.01)

                except Exception as e:
                    if self.is_capturing:
                        logger.error(f"Error in capture loop: {e}", exc_info=True)
                    break

        finally:
            logger.info("WASAPI capture loop ended")

    def stop(self) -> np.ndarray:
        """
        Stop capturing and return all captured audio.

        Returns:
            numpy array of captured audio data, shape (samples, channels)
        """
        logger.info("⏹️  Stopping WASAPI capture...")

        self.is_capturing = False

        # Wait for capture thread to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)

        # Stop audio client
        if self.audio_client:
            try:
                self.audio_client.Stop()
            except:
                pass

        # Cleanup COM interfaces
        self.cleanup()

        # Concatenate all chunks
        if self.audio_chunks:
            audio_data = np.concatenate(self.audio_chunks, axis=0)
            logger.info(f"✅ WASAPI capture stopped. Captured {len(self.audio_chunks)} chunks, "
                       f"total shape: {audio_data.shape}")
            return audio_data
        else:
            logger.warning("No audio chunks captured")
            return np.array([])

    def cleanup(self) -> None:
        """Release COM resources."""
        self.capture_client = None
        self.audio_client = None
        self.device = None
        self.device_enumerator = None

        try:
            comtypes.CoUninitialize()
        except:
            pass

    def get_sample_rate(self) -> Optional[int]:
        """Get the sample rate of captured audio."""
        return self.sample_rate

    def get_channels(self) -> Optional[int]:
        """Get the number of channels in captured audio."""
        return self.channels


def test_wasapi_capture():
    """Test WASAPI loopback capture."""
    print("Testing WASAPI loopback capture...")
    print("Play some audio and press Ctrl+C to stop...")

    capture = WASAPILoopbackCapture()

    try:
        capture.start()

        # Capture for 5 seconds
        time.sleep(5)

        audio_data = capture.stop()

        print(f"\nCaptured audio:")
        print(f"  Shape: {audio_data.shape}")
        print(f"  Sample rate: {capture.get_sample_rate()}Hz")
        print(f"  Channels: {capture.get_channels()}")
        print(f"  Duration: {len(audio_data) / capture.get_sample_rate():.2f}s")
        print(f"  Min: {audio_data.min():.6f}")
        print(f"  Max: {audio_data.max():.6f}")

        # Check if we actually captured sound
        rms = np.sqrt(np.mean(audio_data ** 2))
        print(f"  RMS level: {rms:.6f}")

        if rms > 0.001:
            print("\n✅ Successfully captured system audio!")
        else:
            print("\n⚠️  Captured audio but signal is very quiet. Make sure audio is playing.")

    except KeyboardInterrupt:
        print("\nStopping...")
        audio_data = capture.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_wasapi_capture()
