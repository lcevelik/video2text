"""
GUI utility functions.
"""

import logging
import platform
import re

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
        import sounddevice as sd  # type: ignore
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


def _get_hostapi_names(sd):
    """Return a map of hostapi index -> name (e.g., 0: 'MME', 1: 'Windows WASAPI')."""
    try:
        hostapis = sd.query_hostapis()
        return {i: api.get('name', str(i)) for i, api in enumerate(hostapis)}
    except Exception:
        return {}


def _simplify_device_label(name: str) -> str:
    """Make long, vendor-heavy device names shorter and friendlier for display.

    Rules:
    - remove excessive qualifiers in square/round brackets
    - trim repeated words like 'Output Loopback'
    - shorten common vendor/device phrases
    """
    original = name
    s = name
    # Remove trailing device number markers like (#47)
    s = re.sub(r"\s*\(#\d+\)$", "", s)
    # Normalize 'Output Loopback' tag position
    s = s.replace("[Output Loopback]", "— System Output")
    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s).strip()

    # Shorten some verbose vendor strings
    replacements = {
        "NVIDIA High Definition Audio": "NVIDIA Audio",
        "Realtek(R) Audio": "Realtek Audio",
        "Realtek USB": "Realtek USB",
        "Steam Streaming Speakers": "Steam Speakers",
        "Steam Streaming Microphone": "Steam Mic",
        "Blackmagic DeckLink": "Blackmagic",
        "HyperX Virtual Surround Sound": "HyperX Surround",
        "Hands-Free AG" : "Hands-Free",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    # If label still too long, keep the leading part before the first bracket
    if len(s) > 64 and "(" in s:
        s = s.split("(")[0].strip()

    # Fallback to original if we made it empty by accident
    return s or original


def _normalize_key(name: str) -> str:
    """Normalization key for deduplication.
    Lowercase, strip bracketed suffixes and common tokens so
    'Speakers (Realtek Audio) [Output Loopback]' == 'Speakers (Realtek Audio)'.
    """
    s = name.lower()
    s = s.replace("[output loopback]", "")
    s = re.sub(r"\(#\d+\)", "", s)
    s = re.sub(r"\[.*?\]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _rank_device(name: str, hostapi_name: str, is_loopback: bool) -> int:
    """Higher score => shown earlier (more user-friendly)."""
    score = 0
    n = name.lower()
    # Prefer WASAPI on Windows
    if 'wasapi' in hostapi_name.lower():
        score += 50
    # Known useful system sources
    for kw, pts in [
        ("stereo mix", 200),
        ("cable output", 180),
        ("speakers", 120),
        ("headphone", 110),
        ("earphone", 105),
        ("default", 100),
    ]:
        if kw in n:
            score += pts
    # Deprioritize noisy/uncommon devices
    for kw, pts in [
        ("blackmagic", -60),
        ("steam", -50),
        ("nvidia", -40),
        ("display", -30),
        ("hands-free", -30),
        ("iphone", -30),
        ("wave", -15),
    ]:
        if kw in n:
            score += pts
    # Loopback/system audio goes above regular inputs in the speaker list
    if is_loopback:
        score += 20
    return score


def _dedupe_and_format(device_entries, sd, is_loopback: bool):
    """Given a list of (idx, name), dedupe by normalized key, prefer WASAPI, and format labels.

    Returns list of (idx, display_label) sorted by rank.
    """
    hostapi_names = _get_hostapi_names(sd)

    picked = {}
    for idx, name in device_entries:
        try:
            info = sd.query_devices(idx)
            hostapi_name = hostapi_names.get(info.get('hostapi'), '')
        except Exception:
            hostapi_name = ''
        key = _normalize_key(name)

        # Prefer WASAPI variant when duplicates exist
        prefer = 'wasapi' in hostapi_name.lower()
        if key not in picked:
            picked[key] = (idx, name, hostapi_name)
        else:
            old_idx, old_name, old_api = picked[key]
            if prefer and 'wasapi' not in old_api.lower():
                picked[key] = (idx, name, hostapi_name)

    # Build list with simplified labels and ranking
    formatted = []
    for idx, name, hostapi_name in picked.values():
        label = _simplify_device_label(name)
        # Exclude only truly problematic devices (reduced from previous aggressive filtering)
        exclude_keywords = [
            'steam streaming',  # More specific to avoid false positives
            'iphone',
        ]
        low = label.lower()
        if any(k in low for k in exclude_keywords):
            continue
        if '()' in label or re.search(r"\(\s*\)", label):
            # Skip empty-named parentheses variants like "Output ()"
            continue
        # Add short hint for system sources
        if is_loopback:
            if "— System Output" not in label:
                # Mark clearly in UI this is for capturing playback
                label = f"{label} — System Output"
        score = _rank_device(label, hostapi_name, is_loopback)
        formatted.append((score, idx, label))

    # Sort by score desc, then name
    formatted.sort(key=lambda t: (-t[0], t[2]))
    # Limit list to top-N to avoid overwhelming users (increased from 6/8 to show more options)
    limit = 10 if is_loopback else 12
    top = formatted[:limit]
    return [(idx, label) for _, idx, label in top]


def get_audio_devices():
    """
    Get lists of available audio input devices with OBS-style detection logic.

    OBS Approach:
    - Microphones: Devices with input channels (not loopback/monitor)
    - System Audio: OUTPUT devices (captured via loopback) OR input monitor devices

    Returns:
        tuple: (microphone_devices, loopback_devices)
            Each is a list of tuples: [(device_index, device_name), ...]
    """
    try:
        import sounddevice as sd  # type: ignore
        devices = sd.query_devices()

        microphone_devices = []
        loopback_devices = []

        current_platform = get_platform()

        logger.info("=== OBS-Style Audio Device Detection ===")
        logger.info(f"Platform: {current_platform}")
        logger.info(f"Total devices found: {len(devices)}")

        # Platform-specific loopback/monitor device keywords
        loopback_keywords = {
            'windows': ['stereo mix', 'loopback', 'wave out mix', 'what u hear', 'what you hear', 'mixer'],
            'macos': ['blackhole', 'soundflower', 'loopback', 'aggregate device', 'multi-output'],
            'linux': ['monitor', 'loopback', 'pulse', 'alsa loopback']
        }

        # Get keywords for current platform (with fallback)
        platform_keywords = loopback_keywords.get(current_platform, [])
        all_keywords = platform_keywords + ['stereo mix', 'loopback', 'monitor', 'blackhole', 'soundflower']
        keywords = list(dict.fromkeys(all_keywords))  # Remove duplicates

        for idx, device in enumerate(devices):
            device_name = device['name']
            device_name_lower = device_name.lower()
            input_channels = device['max_input_channels']
            output_channels = device['max_output_channels']

            # Log all device info for debugging
            logger.info(f"Device {idx}: {device_name}")
            logger.info(f"  - Input channels: {input_channels}")
            logger.info(f"  - Output channels: {output_channels}")
            logger.info(f"  - Default sample rate: {device.get('default_samplerate', 'N/A')}")
            logger.info(f"  - Host API: {device.get('hostapi', 'N/A')}")

            # Skip devices with no channels at all
            if input_channels == 0 and output_channels == 0:
                logger.info(f"  → SKIPPED: No input or output channels")
                continue

            # Check if device name matches loopback keywords
            matches_loopback_keyword = any(kw in device_name_lower for kw in keywords)

            # Platform-specific heuristics for loopback detection
            platform_loopback_hint = False
            if current_platform == 'macos':
                # macOS: aggregate devices or multi-output are usually virtual audio routers
                if 'aggregate' in device_name_lower or 'multi-output' in device_name_lower:
                    platform_loopback_hint = True
            elif current_platform == 'linux':
                # Linux: .monitor suffix or "Monitor of" prefix indicates PulseAudio monitor
                if '.monitor' in device_name_lower or 'monitor of' in device_name_lower:
                    platform_loopback_hint = True

            # OBS-STYLE CATEGORIZATION
            # ======================

            # CASE 1: Output-only device (OBS uses these for loopback capture)
            # Windows WASAPI: eRender devices with AUDCLNT_STREAMFLAGS_LOOPBACK
            # These are your speakers/headphones that we capture FROM
            if output_channels > 0 and input_channels == 0:
                # Pure output device - perfect for loopback/system audio capture
                loopback_devices.append((idx, f"{device_name} [Output Loopback]"))
                logger.info(f"  → Categorized as: SYSTEM AUDIO (Output Device - Loopback)")

            # CASE 2: Input device that matches loopback/monitor keywords
            # Linux: PulseAudio monitor sources (e.g., "Monitor of Built-in Audio")
            # Windows: Virtual cables (e.g., "VB-Cable Output", "Stereo Mix")
            # macOS: Virtual devices (e.g., "BlackHole 2ch", "Soundflower")
            elif input_channels > 0 and (matches_loopback_keyword or platform_loopback_hint):
                loopback_devices.append((idx, device_name))
                logger.info(f"  → Categorized as: SYSTEM AUDIO (Monitor/Virtual Device)")

            # CASE 3: Regular input device (microphone, line-in)
            elif input_channels > 0:
                microphone_devices.append((idx, device_name))
                logger.info(f"  → Categorized as: MICROPHONE")

            # CASE 4: Both input and output (aggregate/full-duplex device)
            # Treat as microphone unless it matches loopback keywords
            else:
                if matches_loopback_keyword or platform_loopback_hint:
                    loopback_devices.append((idx, device_name))
                    logger.info(f"  → Categorized as: SYSTEM AUDIO (Aggregate Device)")
                else:
                    microphone_devices.append((idx, device_name))
                    logger.info(f"  → Categorized as: MICROPHONE (Full-Duplex)")

        # Post-process: simplify, dedupe, rank for end-user friendliness
        mic_simple = _dedupe_and_format(microphone_devices, sd, is_loopback=False)
        loop_simple = _dedupe_and_format(loopback_devices, sd, is_loopback=True)

        logger.info(f"Summary (simplified): {len(mic_simple)} mic(s), {len(loop_simple)} system source(s)")
        logger.info("=== End OBS-Style Device Detection ===")

        return mic_simple, loop_simple

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

