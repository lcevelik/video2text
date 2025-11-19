"""
Abstract base class for audio recording backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable
import numpy as np


@dataclass
class RecordingResult:
    """Result of a recording session."""
    mic_data: np.ndarray  # Audio data from microphone
    speaker_data: Optional[np.ndarray]  # Audio data from system/speaker (if available)
    mic_sample_rate: int  # Sample rate of mic recording
    speaker_sample_rate: Optional[int]  # Sample rate of speaker recording
    duration: float  # Duration in seconds
    mic_chunks_count: int  # Number of mic chunks collected
    speaker_chunks_count: int  # Number of speaker chunks collected


class RecordingBackend(ABC):
    """
    Abstract base class for audio recording backends.

    Backends handle the platform-specific details of capturing
    microphone and system audio.
    """

    def __init__(self, mic_device: Optional[int] = None,
                 speaker_device: Optional[int] = None):
        """
        Initialize the recording backend.

        Args:
            mic_device: Device index for microphone (None = auto-detect)
            speaker_device: Device index for system audio (None = auto-detect)
        """
        self.mic_device = mic_device
        self.speaker_device = speaker_device
        self.is_recording = False
        self.mic_level = 0.0  # Current mic level (0.0-1.0)
        self.speaker_level = 0.0  # Current speaker level (0.0-1.0)

    @abstractmethod
    def start_recording(self) -> None:
        """
        Start the recording streams.

        Raises:
            RuntimeError: If streams cannot be opened
        """
        pass

    @abstractmethod
    def stop_recording(self) -> RecordingResult:
        """
        Stop recording and return the collected audio data.

        Returns:
            RecordingResult with audio data and metadata

        Raises:
            RuntimeError: If no data was captured
        """
        pass

    @abstractmethod
    def get_backend_name(self) -> str:
        """Return the name of this backend (e.g., 'sounddevice', 'screencapturekit')."""
        pass

    def get_audio_levels(self) -> tuple:
        """
        Get current audio levels for VU meters.

        Returns:
            Tuple of (mic_level, speaker_level) where each is 0.0-1.0
        """
        return (self.mic_level, self.speaker_level)

    def cleanup(self) -> None:
        """Clean up resources. Override if needed."""
        pass
