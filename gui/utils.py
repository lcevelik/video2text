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

