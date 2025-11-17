"""
SoundDevice backend for cross-platform audio recording.

Supports:
- macOS: BlackHole 2ch for system audio
- Windows: WASAPI loopback
- Linux: PulseAudio monitors
"""

import logging
import time
import numpy as np
from typing import Optional
from .base import RecordingBackend, RecordingResult

logger = logging.getLogger(__name__)

# Sentinel for following system default output (Windows WASAPI loopback)
DEFAULT_SPEAKER_FOLLOW_SYSTEM = -2


class SoundDeviceBackend(RecordingBackend):
    """
    Recording backend using sounddevice library.

    This is the cross-platform implementation that works with:
    - BlackHole 2ch on macOS
    - WASAPI loopback on Windows
    - PulseAudio monitors on Linux
    """

    def __init__(self, mic_device: Optional[int] = None,
                 speaker_device: Optional[int] = None):
        """
        Initialize SoundDevice backend.

        Args:
            mic_device: Device index for microphone (None = auto-detect)
            speaker_device: Device index for system audio (None = auto-detect,
                           DEFAULT_SPEAKER_FOLLOW_SYSTEM for Windows default output)
        """
        super().__init__(mic_device, speaker_device)

        self.mic_stream = None
        self.speaker_stream = None
        self.mic_chunks = []
        self.speaker_chunks = []
        self.mic_callback_count = 0
        self.mic_sample_rate = None
        self.speaker_sample_rate = None
        self.record_start_time = None

    def start_recording(self) -> None:
        """Start recording microphone and system audio."""
        import sounddevice as sd

        logger.info("=== Starting SoundDevice Recording ===")

        devices = sd.query_devices()
        logger.info(f"Total devices available: {len(devices)}")

        # Find and open microphone
        mic_device = self._find_microphone_device(devices)
        self._open_microphone_stream(mic_device, devices)

        # Find and open system audio / loopback device
        loopback_device = self._find_loopback_device(devices, mic_device)
        if loopback_device is not None:
            self._open_loopback_stream(loopback_device, devices)

        self.is_recording = True
        self.record_start_time = time.time()
        logger.info(f"🔴 Recording started at {self.record_start_time}")

    def _find_microphone_device(self, devices) -> int:
        """Find suitable microphone device."""
        import sounddevice as sd

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
                                 for kw in ['stereo mix', 'loopback', 'monitor']):
                            mic_device = idx
                            break

        if mic_device is None:
            raise RuntimeError("No microphone found")

        return mic_device

    def _open_microphone_stream(self, mic_device: int, devices) -> None:
        """Open microphone input stream."""
        import sounddevice as sd

        def mic_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Mic callback status: {status}")
            if self.is_recording:
                self.mic_chunks.append(indata.copy())
                self.mic_callback_count += 1

        # Get device info and try sample rates
        mic_info = devices[mic_device]
        mic_capture_rate = int(mic_info.get('default_samplerate', 0) or 0)
        candidate_rates = [r for r in [mic_capture_rate, 48000, 44100, 32000, 16000]
                          if r and r > 0]

        open_errors = []
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
                open_errors.append(str(e))
                logger.debug(f"Failed to open mic at {rate}Hz: {e}")
                continue

        # If we get here, all rates failed
        error_details = "\n".join([f"  - {rate}Hz: {err}"
                                   for rate, err in zip(candidate_rates, open_errors)])
        raise RuntimeError(
            f"Could not open microphone with any sample rate.\n\n"
            f"Tried: {', '.join(str(r) for r in candidate_rates)}Hz\n\n"
            f"Errors:\n{error_details}"
        )

    def _find_loopback_device(self, devices, mic_device: int) -> Optional[int]:
        """Find suitable loopback/monitor device for system audio."""
        import sounddevice as sd
        from gui.utils import get_platform

        loopback_device = None
        is_macos = get_platform() == 'macos'

        if is_macos:
            # On macOS, look for BlackHole as the system audio source
            for idx, device in enumerate(devices):
                if 'blackhole 2ch' in device.get('name', '').lower():
                    loopback_device = idx
                    logger.info(f"Found BlackHole 2ch for system audio capture: "
                              f"{device.get('name','')}")
                    break

            if loopback_device is None:
                logger.warning("BlackHole 2ch not found. System audio will not be recorded.")
                logger.info("Please install BlackHole for system audio recording on macOS: "
                          "https://github.com/ExistentialAudio/BlackHole")
                return None

        else:
            # Use specified device or auto-detect
            loopback_device = self.speaker_device

            if loopback_device is None:
                # Auto-detect loopback device
                # 1) Prefer input-capable devices with loopback/monitor names
                for idx, device in enumerate(devices):
                    if idx == mic_device:
                        continue
                    try:
                        device_name_lower = str(device.get('name', '')).lower()
                        matches_loopback = any(kw in device_name_lower
                                             for kw in ['stereo mix', 'loopback', 'monitor',
                                                       'speakers wave', 'blackhole',
                                                       'soundflower', 'steam'])
                        if device.get('max_input_channels', 0) > 0 and matches_loopback:
                            loopback_device = idx
                            logger.info(f"Auto-detected loopback device (monitor/input): "
                                      f"{device.get('name','')}")
                            break
                    except Exception:
                        continue

                # 2) Fallback: WASAPI output-only devices
                if loopback_device is None:
                    for idx, device in enumerate(devices):
                        if idx == mic_device:
                            continue
                        try:
                            if (device.get('max_output_channels', 0) > 0 and
                                device.get('max_input_channels', 0) == 0):
                                ha_idx = device.get('hostapi', None)
                                ha_name = ''
                                try:
                                    if ha_idx is not None:
                                        ha_name = sd.query_hostapis()[ha_idx]['name'].lower()
                                except Exception:
                                    ha_name = ''
                                if 'wasapi' in ha_name:
                                    loopback_device = idx
                                    logger.info(f"Auto-detected WASAPI output for loopback: "
                                              f"{device.get('name','')}")
                                    break
                        except Exception:
                            continue

        return loopback_device

    def _open_loopback_stream(self, loopback_device: int, devices) -> None:
        """Open system audio / loopback stream."""
        import sounddevice as sd
        from gui.utils import get_platform

        def speaker_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Speaker callback status: {status}")
            if self.is_recording:
                # Downmix to mono if stereo
                if indata.shape[1] > 1:
                    mono_data = np.mean(indata, axis=1, keepdims=True)
                else:
                    mono_data = indata
                self.speaker_chunks.append(mono_data.copy())

        try:
            # Resolve device for Windows "follow system"
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
                            logger.info(f"Follow-system fallback selected output device idx {i}: "
                                      f"{d.get('name','')} ")
                            break

                    if target_device is None:
                        logger.warning("No usable default output device found for loopback; "
                                     "skipping speaker capture")
                        return

            if target_device is None:
                logger.warning("No valid loopback device; skipping speaker capture")
                return

            # Get device info
            loopback_info = devices[target_device]

            # Determine channel count and sample rate
            if (loopback_info['max_output_channels'] > 0 and
                loopback_info['max_input_channels'] == 0):
                # Pure output device - check if WASAPI
                try:
                    ha_name = sd.query_hostapis()[loopback_info['hostapi']]['name'].lower()
                except Exception:
                    ha_name = ''

                if 'wasapi' not in ha_name:
                    logger.info("Skipping non-WASAPI output device for loopback")
                    return

                loopback_channels = min(loopback_info['max_output_channels'], 2)
                speaker_rate = int(loopback_info.get('default_samplerate',
                                                    self.mic_sample_rate or 16000)
                                 or (self.mic_sample_rate or 16000))
                logger.info(f"Opening loopback stream on WASAPI output with "
                          f"{loopback_channels} channel(s)")

                # Configure WASAPI loopback
                extra = sd.WasapiSettings(loopback=True)
            else:
                # Input monitor device
                loopback_channels = min(loopback_info['max_input_channels'], 2)
                speaker_rate = int(loopback_info.get('default_samplerate',
                                                    self.mic_sample_rate or 16000)
                                 or (self.mic_sample_rate or 16000))
                logger.info(f"Opening loopback stream on input device with "
                          f"{loopback_channels} channel(s)")
                extra = None

            if loopback_channels == 0:
                logger.warning("Loopback device has 0 channels; skipping speaker capture")
                return

            self.speaker_stream = sd.InputStream(
                device=target_device,
                samplerate=speaker_rate,
                channels=loopback_channels,
                callback=speaker_callback,
                extra_settings=extra
            )
            self.speaker_stream.start()
            self.speaker_sample_rate = speaker_rate

            logger.info(f"✅ Speaker stream opened: device {target_device}, "
                       f"rate {speaker_rate}Hz, channels {loopback_channels}")

        except Exception as e:
            logger.warning(f"Could not open loopback stream on device {loopback_device}: {e}")
            logger.info("Recording will continue with microphone only")

    def stop_recording(self) -> RecordingResult:
        """Stop recording and return collected audio."""
        import sounddevice as sd

        self.is_recording = False
        duration = time.time() - self.record_start_time if self.record_start_time else 0

        logger.info(f"⏹️  Recording stopped. Duration: {duration:.1f}s")
        logger.info(f"Mic callbacks fired: {self.mic_callback_count}")
        logger.info(f"Mic chunks collected: {len(self.mic_chunks)}")
        logger.info(f"Speaker chunks collected: {len(self.speaker_chunks)}")

        # Stop streams
        if self.mic_stream:
            self.mic_stream.stop()
            self.mic_stream.close()

        if self.speaker_stream:
            self.speaker_stream.stop()
            self.speaker_stream.close()

        # Process microphone data
        if not self.mic_chunks:
            raise RuntimeError(
                f"No audio samples captured!\n\n"
                f"Debug info:\n"
                f"- Mic callbacks fired: {self.mic_callback_count}\n"
                f"- Recording duration: {duration:.1f}s\n"
                f"- Device: {self.mic_device}\n\n"
                f"Try:\n"
                f"1. Check if microphone is working in other apps\n"
                f"2. Try a different microphone from the dropdown\n"
                f"3. Run: python diagnose_audio.py"
            )

        mic_data = np.concatenate(self.mic_chunks, axis=0)
        logger.info(f"Mic data shape: {mic_data.shape}, size: {mic_data.size}")

        if mic_data.size == 0:
            raise RuntimeError("Mic data is empty after concatenation!")

        # Process speaker data
        speaker_data = None
        if self.speaker_chunks:
            logger.info(f"Processing speaker chunks: {len(self.speaker_chunks)} chunks")
            speaker_data = np.concatenate(self.speaker_chunks, axis=0)
            logger.info(f"Speaker data shape after concatenate: {speaker_data.shape}, "
                       f"size: {speaker_data.size}")

            if speaker_data.size == 0:
                speaker_data = None

        return RecordingResult(
            mic_data=mic_data,
            speaker_data=speaker_data,
            mic_sample_rate=self.mic_sample_rate,
            speaker_sample_rate=self.speaker_sample_rate,
            duration=duration,
            mic_chunks_count=len(self.mic_chunks),
            speaker_chunks_count=len(self.speaker_chunks)
        )

    def get_backend_name(self) -> str:
        """Return backend name."""
        return "sounddevice"

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.mic_stream:
            try:
                self.mic_stream.stop()
                self.mic_stream.close()
            except:
                pass

        if self.speaker_stream:
            try:
                self.speaker_stream.stop()
                self.speaker_stream.close()
            except:
                pass
