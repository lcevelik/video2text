"""
Modular audio recording system with pluggable backends.

Supports:
- sounddevice backend (cross-platform with BlackHole/WASAPI)
- ScreenCaptureKit backend (macOS 12.3+ native system audio)
"""

from .base import RecordingBackend, RecordingResult
from .audio_processor import AudioProcessor
from .sounddevice_backend import SoundDeviceBackend

# Try to import ScreenCaptureKit backend (macOS only)
try:
    from .screencapturekit_backend import ScreenCaptureKitBackend
    HAS_SCREENCAPTUREKIT = True
except ImportError:
    ScreenCaptureKitBackend = None
    HAS_SCREENCAPTUREKIT = False

__all__ = [
    'RecordingBackend',
    'RecordingResult',
    'AudioProcessor',
    'SoundDeviceBackend',
    'ScreenCaptureKitBackend',
    'HAS_SCREENCAPTUREKIT',
]
