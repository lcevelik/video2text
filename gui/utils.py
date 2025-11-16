"""
GUI utility functions.
"""

import logging

logger = logging.getLogger(__name__)


def check_audio_input_devices() -> bool:
    """
    Check if audio input devices are available (utility function).

    Returns:
        bool: True if input devices are available, False otherwise
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()

        # Check for any input device
        has_input = any(d['max_input_channels'] > 0 for d in devices)

        if has_input:
            logger.info(f"Audio devices available: {sum(1 for d in devices if d['max_input_channels'] > 0)} input device(s)")
            return True
        else:
            logger.warning("No audio input devices found")
            return False

    except Exception as e:
        logger.error(f"Error checking audio devices: {e}")
        return False


def get_audio_devices():
    """
    Get lists of available audio input devices.

    Returns:
        tuple: (microphone_devices, loopback_devices)
            Each is a list of tuples: [(device_index, device_name), ...]
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()

        microphone_devices = []
        loopback_devices = []

        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                device_name = device['name']
                device_name_lower = device_name.lower()

                # Check if it's a loopback/system audio device
                if any(kw in device_name_lower for kw in ['stereo mix', 'loopback', 'monitor', 'blackhole', 'soundflower']):
                    loopback_devices.append((idx, device_name))
                else:
                    microphone_devices.append((idx, device_name))

        logger.info(f"Found {len(microphone_devices)} microphone(s) and {len(loopback_devices)} loopback device(s)")
        return microphone_devices, loopback_devices

    except Exception as e:
        logger.error(f"Error getting audio devices: {e}")
        return [], []

