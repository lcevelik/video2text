"""
Audio processing utilities for normalization, resampling, and mixing.
"""

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio processing operations like resampling, normalization, and mixing."""

    @staticmethod
    def normalize_audio(audio_data: np.ndarray, target_rms: float = 0.15) -> np.ndarray:
        """
        Normalize audio to target RMS level with intelligent AGC.

        Args:
            audio_data: numpy array of audio samples
            target_rms: target RMS level (0.15 = good speech level, ~-16.5dB)

        Returns:
            Normalized audio data
        """
        # Handle empty input
        if audio_data is None or audio_data.size == 0:
            return audio_data

        # Ensure float format to prevent clipping/wrapping issues with int
        audio_data = audio_data.astype(np.float32)

        # Calculate current RMS
        current_rms = np.sqrt(np.mean(audio_data**2))

        # Avoid division by zero
        if current_rms < 0.0001:
            return audio_data

        # Calculate gain needed to reach target RMS
        gain = target_rms / current_rms

        # Limit maximum gain to prevent amplifying noise excessively
        # Max gain of 10x (~20dB boost) for very quiet audio
        gain = min(gain, 10.0)

        # Apply gain
        normalized = audio_data * gain

        # Soft clipping to prevent hard clipping artifacts
        # This will gently compress peaks instead of harsh clipping
        normalized = np.tanh(normalized)

        return normalized

    @staticmethod
    def apply_compression(audio_data: np.ndarray, threshold: float = 0.6,
                         ratio: float = 3.0) -> np.ndarray:
        """
        Apply dynamic range compression to control peaks while maintaining loudness.

        Args:
            audio_data: numpy array of audio samples
            threshold: level above which compression kicks in (0.6 = -4.4dB)
            ratio: compression ratio (3.0 means 3:1 compression)

        Returns:
            Compressed audio data
        """
        # Handle empty input
        if audio_data is None or audio_data.size == 0:
            return audio_data

        # Work with absolute values for compression
        abs_audio = np.abs(audio_data)

        # Calculate compression for samples above threshold
        # Samples below threshold pass through unchanged
        mask = abs_audio > threshold

        if np.any(mask):
            # Amount above threshold
            over = abs_audio[mask] - threshold

            # Compress the overage
            compressed_over = over / ratio

            # Reconstruct: threshold + compressed overage
            abs_audio[mask] = threshold + compressed_over

        # Apply compressed envelope back to original signal (preserving sign)
        sign = np.sign(audio_data)
        compressed = sign * abs_audio

        # Normalize to target level (~-6dB for good headroom)
        target_level = 0.5
        if compressed.size == 0:
            return compressed
        current_peak = np.max(np.abs(compressed))
        if current_peak > 0:
            compressed = compressed * (target_level / current_peak)

        return compressed

    @staticmethod
    def resample(audio_data: np.ndarray, from_rate: int,
                 to_rate: int) -> np.ndarray:
        """
        Resample audio from one sample rate to another.

        Args:
            audio_data: Input audio data
            from_rate: Source sample rate
            to_rate: Target sample rate

        Returns:
            Resampled audio data

        Raises:
            ValueError: If resampling fails
        """
        if audio_data is None or audio_data.size == 0:
            return audio_data

        if not from_rate or not to_rate or int(from_rate) == int(to_rate):
            return audio_data

        try:
            from scipy.signal import resample_poly
            import math

            fr = int(from_rate)
            tr = int(to_rate)
            g = math.gcd(fr, tr)
            up = tr // g
            down = fr // g
            mono = audio_data.squeeze()

            logger.debug(f"Resampling: {fr}Hz -> {tr}Hz (up={up}, down={down}), "
                        f"input shape: {audio_data.shape}")

            y = resample_poly(mono, up, down)
            result = y.reshape(-1, 1)

            logger.debug(f"Resample result shape: {result.shape}")
            return result

        except Exception as e:
            logger.warning(f"resample_poly failed ({e}), falling back to linear interpolation")

            try:
                mono = audio_data.squeeze()
                new_len = int(round(len(mono) * float(to_rate) / float(from_rate)))
                x_old = np.linspace(0, 1, len(mono), endpoint=False)
                x_new = np.linspace(0, 1, new_len, endpoint=False)
                y = np.interp(x_new, x_old, mono)
                result = y.reshape(-1, 1)

                logger.debug(f"Fallback resample result shape: {result.shape}")
                return result

            except Exception as e2:
                logger.error(f"Both resampling methods failed: {e2}")
                raise ValueError(f"Failed to resample audio: {e2}") from e2

    @staticmethod
    def mix_audio(mic_data: np.ndarray, speaker_data: Optional[np.ndarray],
                  mic_rate: int, speaker_rate: Optional[int],
                  target_rate: int = 16000) -> np.ndarray:
        """
        Mix microphone and speaker audio into a single stream.

        Args:
            mic_data: Microphone audio data
            speaker_data: Speaker audio data (can be None)
            mic_rate: Microphone sample rate
            speaker_rate: Speaker sample rate
            target_rate: Target sample rate for output

        Returns:
            Mixed audio at target sample rate
        """
        logger.info(f"Mixing audio - Mic: {mic_data.shape if mic_data is not None else 'None'}, "
                   f"Speaker: {speaker_data.shape if speaker_data is not None else 'None'}")

        # Resample mic to final rate if needed
        if mic_rate and mic_rate != target_rate:
            logger.info(f"Resampling mic from {mic_rate}Hz to {target_rate}Hz")
            mic_data = AudioProcessor.resample(mic_data, mic_rate, target_rate)

        # If no speaker data, return mic only
        if speaker_data is None or speaker_data.size == 0:
            logger.info("No speaker data, using mic-only")
            return mic_data

        # Resample speaker to final rate if needed
        if speaker_rate and speaker_rate != target_rate:
            logger.info(f"Resampling speaker from {speaker_rate}Hz to {target_rate}Hz")
            speaker_data = AudioProcessor.resample(speaker_data, speaker_rate, target_rate)
            logger.info(f"Speaker data shape after resample: {speaker_data.shape}")

        # Align lengths before mixing
        logger.info(f"Aligning audio lengths - Mic: {len(mic_data)}, Speaker: {len(speaker_data)}")
        max_len = max(len(mic_data), len(speaker_data))

        if len(mic_data) < max_len:
            mic_data = np.pad(mic_data, ((0, max_len - len(mic_data)), (0, 0)))

        if len(speaker_data) < max_len:
            speaker_data = np.pad(speaker_data, ((0, max_len - len(speaker_data)), (0, 0)))

        logger.info(f"Mixing audio - Mic shape: {mic_data.shape}, Speaker shape: {speaker_data.shape}")

        # Mix by averaging to prevent clipping before normalization
        final_data = (mic_data + speaker_data) / 2.0

        logger.info(f"Mixed audio shape: {final_data.shape}")
        return final_data

    @staticmethod
    def apply_safety_limiting(audio_data: np.ndarray, max_level: float = 0.98) -> np.ndarray:
        """
        Apply safety limiting to prevent clipping.

        Args:
            audio_data: Input audio data
            max_level: Maximum allowed level (0.98 default)

        Returns:
            Limited audio data
        """
        if audio_data is None or audio_data.size == 0:
            return audio_data

        max_val = np.max(np.abs(audio_data))
        if max_val > max_level:
            audio_data = audio_data / max_val * max_level

        return audio_data
