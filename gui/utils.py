"""
GUI utility functions.
"""

import logging
import platform

logger = logging.getLogger(__name__)


def get_platform():
    """Get the current operating system platform."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


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
    Get lists of available audio input devices with platform-specific logic.

    Returns:
        tuple: (microphone_devices, loopback_devices)
            Each is a list of tuples: [(device_index, device_name), ...]
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()

        microphone_devices = []
        loopback_devices = []

        current_platform = get_platform()

        logger.info("=== Audio Device Detection ===")
        logger.info(f"Platform: {current_platform}")
        logger.info(f"Total devices found: {len(devices)}")

        # Platform-specific loopback device keywords
        loopback_keywords = {
            'windows': ['stereo mix', 'loopback', 'wave out mix', 'what u hear', 'mixer'],
            'macos': ['blackhole', 'soundflower', 'loopback', 'aggregate device'],
            'linux': ['monitor', 'loopback', 'pulse', 'alsa loopback']
        }

        # Get keywords for current platform (with fallback)
        platform_keywords = loopback_keywords.get(current_platform, [])
        all_keywords = platform_keywords + ['stereo mix', 'loopback', 'monitor', 'blackhole', 'soundflower']
        # Remove duplicates while preserving order
        keywords = list(dict.fromkeys(all_keywords))

        for idx, device in enumerate(devices):
            # Log all device info for debugging
            logger.info(f"Device {idx}: {device['name']}")
            logger.info(f"  - Input channels: {device['max_input_channels']}")
            logger.info(f"  - Output channels: {device['max_output_channels']}")
            logger.info(f"  - Default sample rate: {device.get('default_samplerate', 'N/A')}")
            logger.info(f"  - Host API: {device.get('hostapi', 'N/A')}")

            if device['max_input_channels'] > 0:
                device_name = device['name']
                device_name_lower = device_name.lower()

                # Check if it's a loopback/system audio device
                is_loopback = any(kw in device_name_lower for kw in keywords)

                # Platform-specific heuristics
                if current_platform == 'macos':
                    # On macOS, check for aggregate devices or specific patterns
                    if 'aggregate' in device_name_lower or 'multi-output' in device_name_lower:
                        is_loopback = True

                elif current_platform == 'linux':
                    # On Linux, PulseAudio monitor devices are loopback
                    if '.monitor' in device_name_lower or 'monitor of' in device_name_lower:
                        is_loopback = True

                if is_loopback:
                    loopback_devices.append((idx, device_name))
                    logger.info(f"  → Categorized as: LOOPBACK/SYSTEM AUDIO")
                else:
                    microphone_devices.append((idx, device_name))
                    logger.info(f"  → Categorized as: MICROPHONE")

        logger.info(f"Summary: {len(microphone_devices)} microphone(s), {len(loopback_devices)} loopback device(s)")
        logger.info("=== End Device Detection ===")

        return microphone_devices, loopback_devices

    except Exception as e:
        logger.error(f"Error getting audio devices: {e}", exc_info=True)
        return [], []


def get_platform_audio_setup_help():
    """
    Get platform-specific setup instructions for audio devices.

    Returns:
        dict: Setup instructions and recommendations for current platform
    """
    current_platform = get_platform()

    help_info = {
        'macos': {
            'loopback_install': [
                "macOS doesn't have built-in system audio capture.",
                "Install a virtual audio device:",
                "",
                "Option 1: BlackHole (Recommended - Free & Open Source)",
                "  brew install blackhole-2ch",
                "  or download from: https://github.com/ExistentialAudio/BlackHole",
                "",
                "Option 2: Soundflower (Alternative)",
                "  https://github.com/mattingalls/Soundflower",
                "",
                "After installation:",
                "  1. Restart this app",
                "  2. Click 'Refresh Devices'",
                "  3. Select 'BlackHole 2ch' or 'Soundflower' as Speaker/System device",
            ],
            'permissions': [
                "If microphone doesn't appear:",
                "  1. Open System Settings (or System Preferences)",
                "  2. Go to Privacy & Security → Microphone",
                "  3. Enable permission for this app or Terminal",
                "  4. Click 'Refresh Devices'",
            ]
        },
        'windows': {
            'loopback_install': [
                "Enable Stereo Mix for system audio capture:",
                "",
                "Method 1: Enable Stereo Mix (Built-in on most systems)",
                "  1. Right-click speaker icon in system tray",
                "  2. Select 'Sounds' or 'Sound Settings'",
                "  3. Go to 'Recording' tab",
                "  4. Right-click in empty space",
                "  5. Check 'Show Disabled Devices'",
                "  6. Right-click 'Stereo Mix' and select 'Enable'",
                "  7. Click 'Refresh Devices' in this app",
                "",
                "Method 2: Virtual Audio Cable (if Stereo Mix unavailable)",
                "  Download VB-Audio Virtual Cable:",
                "  https://vb-audio.com/Cable/",
            ],
            'permissions': [
                "If microphone doesn't appear:",
                "  1. Open Settings → Privacy → Microphone",
                "  2. Enable 'Allow apps to access your microphone'",
                "  3. Enable permission for this app",
                "  4. Click 'Refresh Devices'",
            ]
        },
        'linux': {
            'loopback_install': [
                "Linux audio loopback setup (PulseAudio/PipeWire):",
                "",
                "PulseAudio:",
                "  Load the loopback module:",
                "  pactl load-module module-loopback",
                "",
                "  To make it permanent, add to /etc/pulse/default.pa:",
                "  load-module module-loopback",
                "",
                "PipeWire:",
                "  Virtual devices usually work out of the box",
                "  Monitor devices (.monitor) capture application audio",
                "",
                "ALSA Loopback:",
                "  sudo modprobe snd-aloop",
            ],
            'permissions': [
                "If microphone doesn't appear:",
                "  1. Check your audio system (PulseAudio/PipeWire/ALSA)",
                "  2. Verify microphone is not muted in system settings",
                "  3. Run: arecord -l  (to list recording devices)",
                "  4. Click 'Refresh Devices'",
            ]
        }
    }

    return help_info.get(current_platform, {
        'loopback_install': ["Platform-specific instructions not available."],
        'permissions': ["Check your system's audio settings."]
    })

