"""
Audio Processor for enhanced transcription.
Handles in-memory audio loading and chunk extraction for faster processing.
"""

import logging
import tempfile
from typing import Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Processes audio files with optimized in-memory operations."""

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize the audio processor.

        Args:
            sample_rate: Sample rate for audio processing (Whisper uses 16kHz)
        """
        self.sample_rate = sample_rate
        self._audio_cache = None
        self._audio_cache_path = None

    def load_audio_to_memory(self, audio_path: str) -> Tuple[Optional[np.ndarray], float]:
        """
        Load audio file into memory for faster chunk extraction.

        OPTIMIZATION: Loading audio once and slicing in memory is much faster than
        extracting each chunk with ffmpeg (eliminates file I/O overhead).

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (audio_data as numpy array or None, total_duration in seconds)
        """
        try:
            import librosa
        except ImportError:
            logger.warning("librosa not available, falling back to ffmpeg extraction")
            return None, 0.0

        try:
            # Load audio at 16kHz mono (Whisper's expected format)
            logger.debug(f"Loading audio into memory: {audio_path}")
            audio_data, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            total_duration = len(audio_data) / sr
            logger.debug(f"Audio loaded: {total_duration:.1f}s, {len(audio_data)} samples")

            # Cache for reuse
            self._audio_cache = audio_data
            self._audio_cache_path = audio_path

            return audio_data, total_duration
        except Exception as e:
            logger.warning(f"Failed to load audio into memory: {e}, falling back to ffmpeg")
            return None, 0.0

    def extract_audio_chunk_from_memory(
        self,
        audio_data: np.ndarray,
        start: float,
        end: float
    ) -> Tuple[Optional[str], float]:
        """
        Extract audio chunk from in-memory data and save to temp file.

        OPTIMIZATION: Slicing in-memory array is much faster than ffmpeg extraction.

        Args:
            audio_data: Audio data as numpy array
            start: Start time in seconds
            end: End time in seconds

        Returns:
            Tuple of (temp_file_path or None, chunk_duration)
        """
        try:
            import soundfile as sf
        except ImportError:
            logger.warning("soundfile not available, cannot extract from memory")
            return None, 0.0

        try:
            start_sample = int(start * self.sample_rate)
            end_sample = int(end * self.sample_rate)
            chunk_data = audio_data[start_sample:end_sample]

            # Write to temp file for Whisper
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_path = temp_audio.name

            sf.write(temp_path, chunk_data, self.sample_rate)
            duration = len(chunk_data) / self.sample_rate

            return temp_path, duration
        except Exception as e:
            logger.warning(f"Failed to extract chunk from memory: {e}")
            return None, 0.0

    def get_cached_audio(self, audio_path: str) -> Optional[np.ndarray]:
        """
        Get cached audio data if available.

        Args:
            audio_path: Path to check cache for

        Returns:
            Cached audio data or None
        """
        if self._audio_cache_path == audio_path and self._audio_cache is not None:
            return self._audio_cache
        return None

    def clear_cache(self):
        """Clear audio cache to free memory."""
        self._audio_cache = None
        self._audio_cache_path = None
