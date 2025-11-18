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
from ctypes import (
    POINTER, Structure, c_float, c_int16, c_uint16, c_uint32, c_uint64,
    c_int64, c_void_p, byref, cast
)
import comtypes
from comtypes import GUID, COMMETHOD, IUnknown, HRESULT

logger = logging.getLogger(__name__)


# ===== Windows Audio Constants =====
CLSID_MMDeviceEnumerator = GUID('{BCDE0395-E52F-467C-8E3D-C4579291692E}')
IID_IMMDeviceEnumerator = GUID('{A95664D2-9614-4F35-A746-DE8DB63617E6}')
IID_IMMDevice = GUID('{D666063F-1587-4E43-81F1-B948E807363F}')
IID_IAudioClient = GUID('{1CB9AD4C-DBFA-4c32-B178-C2F568A703B2}')
IID_IAudioCaptureClient = GUID('{C8ADBD64-E71E-48a0-A4DE-185C395CD317}')

# EDataFlow enum
eRender = 0  # Audio rendering (output)
eCapture = 1  # Audio capture (input)
eAll = 2

# ERole enum
eConsole = 0
eMultimedia = 1
eCommunications = 2

# Audio client flags
AUDCLNT_STREAMFLAGS_LOOPBACK = 0x00020000
AUDCLNT_SHAREMODE_SHARED = 0


# ===== COM Structures =====
class WAVEFORMATEX(Structure):
    _fields_ = [
        ('wFormatTag', c_uint16),
        ('nChannels', c_uint16),
        ('nSamplesPerSec', c_uint32),
        ('nAvgBytesPerSec', c_uint32),
        ('nBlockAlign', c_uint16),
        ('wBitsPerSample', c_uint16),
        ('cbSize', c_uint16),
    ]


# ===== COM Interfaces =====
class IMMDeviceEnumerator(IUnknown):
    _iid_ = IID_IMMDeviceEnumerator
    _methods_ = [
        COMMETHOD([], HRESULT, 'EnumAudioEndpoints'),
        COMMETHOD([], HRESULT, 'GetDefaultAudioEndpoint',
                  (['in'], c_uint32, 'dataFlow'),
                  (['in'], c_uint32, 'role'),
                  (['out'], POINTER(POINTER(IUnknown)), 'ppDevice')),
    ]


class IMMDevice(IUnknown):
    _iid_ = IID_IMMDevice
    _methods_ = [
        COMMETHOD([], HRESULT, 'Activate',
                  (['in'], POINTER(GUID), 'iid'),
                  (['in'], c_uint32, 'dwClsCtx'),
                  (['in'], c_void_p, 'pActivationParams'),
                  (['out'], POINTER(c_void_p), 'ppInterface')),
        COMMETHOD([], HRESULT, 'OpenPropertyStore'),
        COMMETHOD([], HRESULT, 'GetId',
                  (['out'], POINTER(c_void_p), 'ppstrId')),
        COMMETHOD([], HRESULT, 'GetState'),
    ]


class IAudioClient(IUnknown):
    _iid_ = IID_IAudioClient
    _methods_ = [
        COMMETHOD([], HRESULT, 'Initialize',
                  (['in'], c_uint32, 'ShareMode'),
                  (['in'], c_uint32, 'StreamFlags'),
                  (['in'], c_int64, 'hnsBufferDuration'),
                  (['in'], c_int64, 'hnsPeriodicity'),
                  (['in'], POINTER(WAVEFORMATEX), 'pFormat'),
                  (['in'], POINTER(GUID), 'AudioSessionGuid')),
        COMMETHOD([], HRESULT, 'GetBufferSize'),
        COMMETHOD([], HRESULT, 'GetStreamLatency'),
        COMMETHOD([], HRESULT, 'GetCurrentPadding'),
        COMMETHOD([], HRESULT, 'IsFormatSupported'),
        COMMETHOD([], HRESULT, 'GetMixFormat',
                  (['out'], POINTER(POINTER(WAVEFORMATEX)), 'ppDeviceFormat')),
        COMMETHOD([], HRESULT, 'GetDevicePeriod'),
        COMMETHOD([], HRESULT, 'Start'),
        COMMETHOD([], HRESULT, 'Stop'),
        COMMETHOD([], HRESULT, 'Reset'),
        COMMETHOD([], HRESULT, 'SetEventHandle'),
        COMMETHOD([], HRESULT, 'GetService',
                  (['in'], POINTER(GUID), 'riid'),
                  (['out'], POINTER(c_void_p), 'ppv')),
    ]


class IAudioCaptureClient(IUnknown):
    _iid_ = IID_IAudioCaptureClient
    _methods_ = [
        COMMETHOD([], HRESULT, 'GetBuffer',
                  (['out'], POINTER(c_void_p), 'ppData'),
                  (['out'], POINTER(c_uint32), 'pNumFramesToRead'),
                  (['out'], POINTER(c_uint32), 'pdwFlags'),
                  (['out'], POINTER(c_uint64), 'pu64DevicePosition'),
                  (['out'], POINTER(c_uint64), 'pu64QPCPosition')),
        COMMETHOD([], HRESULT, 'ReleaseBuffer',
                  (['in'], c_uint32, 'NumFramesRead')),
        COMMETHOD([], HRESULT, 'GetNextPacketSize',
                  (['out'], POINTER(c_uint32), 'pNumFramesInNextPacket')),
    ]


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
            try:
                comtypes.CoInitialize()
            except OSError as e:
                # COM may already be initialized in this thread, which is fine
                logger.debug(f"COM initialization note: {e}")
            except Exception as e:
                logger.error(f"Failed to initialize COM: {e}")
                raise

            # Create device enumerator
            self.device_enumerator = comtypes.CoCreateInstance(
                CLSID_MMDeviceEnumerator,
                IMMDeviceEnumerator,
                comtypes.CLSCTX_ALL
            )

            # Get default audio output device (speakers/headphones)
            # With comtypes, out parameters are returned, not passed
            self.device = self.device_enumerator.GetDefaultAudioEndpoint(
                eRender,  # Output device
                eConsole   # Console role
            )
            logger.info("Got default audio output device")

            # Activate audio client
            # comtypes returns the interface pointer directly
            audio_client_ptr = self.device.Activate(
                IID_IAudioClient,
                comtypes.CLSCTX_ALL,
                None
            )
            self.audio_client = cast(audio_client_ptr, POINTER(IAudioClient))
            logger.info("Audio client activated")

            # Get the mix format
            # comtypes returns the pointer directly
            self.wave_format = self.audio_client.GetMixFormat()

            # Log audio format details
            self.sample_rate = self.wave_format.contents.nSamplesPerSec
            self.channels = self.wave_format.contents.nChannels
            bits_per_sample = self.wave_format.contents.wBitsPerSample

            logger.info(f"Audio format: {self.sample_rate}Hz, {self.channels}ch, {bits_per_sample}bit")

            # Initialize audio client in loopback mode
            buffer_duration = 10000000  # 1 second in 100-nanosecond units

            # comtypes raises exception on error, no need to check HRESULT
            self.audio_client.Initialize(
                AUDCLNT_SHAREMODE_SHARED,
                AUDCLNT_STREAMFLAGS_LOOPBACK,
                buffer_duration,
                0,  # Periodicity (must be 0 for shared mode)
                self.wave_format,
                None  # Audio session GUID
            )

            logger.info("Audio client initialized in loopback mode")

            # Get the capture client
            # comtypes returns the interface pointer directly
            capture_client_ptr = self.audio_client.GetService(IID_IAudioCaptureClient)
            self.capture_client = cast(capture_client_ptr, POINTER(IAudioCaptureClient))
            logger.info("Capture client obtained")

            # Start the audio client
            # comtypes raises exception on error
            self.audio_client.Start()
            logger.info("Audio client started")

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
                    # comtypes returns the value directly
                    packet_length = self.capture_client.GetNextPacketSize()

                    while packet_length > 0:
                        # Get the buffer
                        # comtypes returns all out parameters as a tuple
                        data_pointer, num_frames, flags, device_position, qpc_position = \
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
                            try:
                                audio_data = audio_data.reshape(num_frames, self.channels)
                            except ValueError as e:
                                logger.error(f"Failed to reshape audio data: {e}")
                                logger.error(f"  Expected: ({num_frames}, {self.channels})")
                                logger.error(f"  Got: {audio_data.shape}")
                                self.capture_client.ReleaseBuffer(num_frames)
                                packet_length = self.capture_client.GetNextPacketSize()
                                continue

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
                        # comtypes raises exception on error
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
