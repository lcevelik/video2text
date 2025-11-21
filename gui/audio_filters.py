"""
Audio filters inspired by OBS Studio for professional audio processing.

Includes:
- RNNoise: Neural network noise suppression
- Noise Gate: Threshold-based silence removal
- Enhanced Compressor: OBS-style envelope-following dynamics
"""

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class NoiseGate:
    """
    Threshold-based noise gate with attack, release, and hold times.
    Inspired by OBS Studio's noise gate filter.
    """

    def __init__(self, threshold_db=-32.0, attack_ms=25.0, release_ms=150.0, hold_ms=200.0, sample_rate=16000):
        """
        Initialize noise gate.

        Args:
            threshold_db: Gate opens above this level (dB)
            attack_ms: Time to fully open gate (milliseconds)
            release_ms: Time to fully close gate (milliseconds)
            hold_ms: Time to keep gate open after signal drops (milliseconds)
            sample_rate: Audio sample rate
        """
        self.threshold = self._db_to_linear(threshold_db)
        self.sample_rate = sample_rate

        # Convert times to sample counts
        self.attack_frames = int((attack_ms / 1000.0) * sample_rate)
        self.release_frames = int((release_ms / 1000.0) * sample_rate)
        self.hold_frames = int((hold_ms / 1000.0) * sample_rate)

        # State
        self.envelope = 0.0
        self.hold_counter = 0
        self.is_open = False

        logger.info(f"NoiseGate initialized: threshold={threshold_db}dB, attack={attack_ms}ms, release={release_ms}ms, hold={hold_ms}ms")

    @staticmethod
    def _db_to_linear(db):
        """Convert dB to linear amplitude."""
        return 10.0 ** (db / 20.0)

    def process(self, audio_data):
        """
        Apply noise gate to audio.

        Args:
            audio_data: numpy array (frames, channels) or (frames,)

        Returns:
            Processed audio data
        """
        if audio_data.size == 0:
            return audio_data

        # Ensure 2D array
        is_1d = audio_data.ndim == 1
        if is_1d:
            audio_data = audio_data.reshape(-1, 1)

        output = np.zeros_like(audio_data)
        frames = audio_data.shape[0]

        # Calculate attack/release coefficients (per sample)
        attack_coeff = 1.0 / max(1, self.attack_frames)
        release_coeff = 1.0 / max(1, self.release_frames)

        for i in range(frames):
            # Calculate RMS of current frame
            frame_rms = np.sqrt(np.mean(audio_data[i] ** 2))

            # Determine if gate should be open
            should_open = frame_rms > self.threshold

            if should_open:
                self.hold_counter = self.hold_frames
                if not self.is_open:
                    self.is_open = True

            # Apply hold time
            if self.hold_counter > 0:
                self.hold_counter -= 1
                should_open = True
            else:
                if self.is_open and not should_open:
                    self.is_open = False

            # Smooth envelope transition
            target = 1.0 if should_open else 0.0
            if self.envelope < target:
                # Attack
                self.envelope += attack_coeff
                self.envelope = min(self.envelope, 1.0)
            elif self.envelope > target:
                # Release
                self.envelope -= release_coeff
                self.envelope = max(self.envelope, 0.0)

            # Apply gate
            output[i] = audio_data[i] * self.envelope

        return output.reshape(-1) if is_1d else output


class EnhancedCompressor:
    """
    Advanced dynamics compressor with envelope-following.
    Inspired by OBS Studio's compressor filter.
    """

    def __init__(self, threshold_db=-18.0, ratio=3.0, attack_ms=6.0, release_ms=60.0,
                 output_gain_db=0.0, sample_rate=16000):
        """
        Initialize compressor.

        Args:
            threshold_db: Compression starts above this level (dB)
            ratio: Compression ratio (1.0 = no compression, higher = more compression)
            attack_ms: Time to respond to level increases (milliseconds)
            release_ms: Time to respond to level decreases (milliseconds)
            output_gain_db: Makeup gain applied after compression (dB)
            sample_rate: Audio sample rate
        """
        self.threshold_db = threshold_db
        self.threshold = self._db_to_linear(threshold_db)
        self.ratio = max(1.0, ratio)
        self.output_gain = self._db_to_linear(output_gain_db)
        self.sample_rate = sample_rate

        # Calculate envelope coefficients (OBS method)
        self.attack_coeff = self._time_to_coeff(attack_ms / 1000.0)
        self.release_coeff = self._time_to_coeff(release_ms / 1000.0)

        # State
        self.envelope = 0.0

        logger.info(f"EnhancedCompressor initialized: threshold={threshold_db}dB, ratio={ratio}:1, "
                   f"attack={attack_ms}ms, release={release_ms}ms, gain={output_gain_db}dB")

    def _time_to_coeff(self, time_seconds):
        """Convert time constant to exponential coefficient (OBS method)."""
        if time_seconds <= 0:
            return 0.0
        return np.exp(-1.0 / (self.sample_rate * time_seconds))

    @staticmethod
    def _db_to_linear(db):
        """Convert dB to linear amplitude."""
        return 10.0 ** (db / 20.0)

    @staticmethod
    def _linear_to_db(linear):
        """Convert linear amplitude to dB."""
        return 20.0 * np.log10(max(1e-10, linear))

    def process(self, audio_data):
        """
        Apply compression to audio.

        Args:
            audio_data: numpy array (frames, channels) or (frames,)

        Returns:
            Compressed audio data
        """
        if audio_data.size == 0:
            return audio_data

        # Ensure 2D array
        is_1d = audio_data.ndim == 1
        if is_1d:
            audio_data = audio_data.reshape(-1, 1)

        output = np.zeros_like(audio_data)
        frames = audio_data.shape[0]

        for i in range(frames):
            # Calculate RMS of current frame
            frame_rms = np.sqrt(np.mean(audio_data[i] ** 2))

            # Envelope follower with attack/release
            if frame_rms > self.envelope:
                # Attack
                self.envelope = self.attack_coeff * self.envelope + (1.0 - self.attack_coeff) * frame_rms
            else:
                # Release
                self.envelope = self.release_coeff * self.envelope + (1.0 - self.release_coeff) * frame_rms

            # Calculate gain reduction
            if self.envelope > self.threshold:
                # Convert to dB for ratio calculation
                envelope_db = self._linear_to_db(self.envelope)

                # Amount over threshold
                over_db = envelope_db - self.threshold_db

                # Apply ratio (slope calculation)
                gain_reduction_db = over_db * (1.0 - 1.0 / self.ratio)

                # Convert back to linear
                gain = self._db_to_linear(-gain_reduction_db)
            else:
                gain = 1.0

            # Apply compression and output gain
            output[i] = audio_data[i] * gain * self.output_gain

        return output.reshape(-1) if is_1d else output


class RNNoise:
    """
    Neural network-based noise suppression.
    Uses rnnoise library if available, otherwise falls back to spectral subtraction.
    """

    def __init__(self, sample_rate=16000):
        """
        Initialize RNNoise processor.

        Args:
            sample_rate: Audio sample rate (RNNoise works at 48kHz internally)
        """
        self.sample_rate = sample_rate
        self.target_rate = 48000  # RNNoise operates at 48kHz
        self.frame_size = 480  # RNNoise processes 10ms frames at 48kHz
        self.rnnoise_state = None
        self.has_rnnoise = False

        try:
            import rnnoise
            self.rnnoise_state = rnnoise.RNNoise()
            self.has_rnnoise = True
            logger.info("RNNoise initialized successfully")
        except ImportError:
            logger.warning("RNNoise library not available. Install with: pip install rnnoise")
            logger.info("Falling back to spectral subtraction noise reduction")
            self.has_rnnoise = False

    def process(self, audio_data):
        """
        Apply noise suppression to audio.

        Args:
            audio_data: numpy array (frames,) mono audio

        Returns:
            Denoised audio data
        """
        if audio_data.size == 0:
            return audio_data

        if self.has_rnnoise:
            return self._process_rnnoise(audio_data)
        else:
            return self._process_spectral_subtraction(audio_data)

    def _process_rnnoise(self, audio_data):
        """Process audio using RNNoise library."""
        # Resample to 48kHz if needed
        if self.sample_rate != self.target_rate:
            from scipy import signal
            num_samples = int(len(audio_data) * self.target_rate / self.sample_rate)
            audio_48k = signal.resample(audio_data, num_samples)
        else:
            audio_48k = audio_data.copy()

        # Convert to int16 (RNNoise expects this)
        audio_int16 = (audio_48k * 32768.0).astype(np.int16)

        # Process in 10ms frames
        output = []
        for i in range(0, len(audio_int16), self.frame_size):
            frame = audio_int16[i:i + self.frame_size]

            # Pad last frame if needed
            if len(frame) < self.frame_size:
                frame = np.pad(frame, (0, self.frame_size - len(frame)))

            # Process with RNNoise
            denoised_frame = self.rnnoise_state.process_frame(frame)
            output.append(denoised_frame)

        # Concatenate frames
        output = np.concatenate(output)[:len(audio_int16)]

        # Convert back to float
        output = output.astype(np.float32) / 32768.0

        # Resample back to original rate if needed
        if self.sample_rate != self.target_rate:
            from scipy import signal
            output = signal.resample(output, len(audio_data))

        return output

    def _process_spectral_subtraction(self, audio_data):
        """
        Fallback noise reduction using spectral subtraction.
        Simple but effective for basic noise reduction.
        """
        try:
            from scipy import signal as scipy_signal

            # Use Short-Time Fourier Transform
            f, t, Zxx = scipy_signal.stft(audio_data, fs=self.sample_rate, nperseg=256)

            # Estimate noise (first 10% of signal assumed to be noise)
            noise_frames = max(1, int(0.1 * Zxx.shape[1]))
            noise_spectrum = np.mean(np.abs(Zxx[:, :noise_frames]), axis=1, keepdims=True)

            # Spectral subtraction
            magnitude = np.abs(Zxx)
            phase = np.angle(Zxx)

            # Subtract noise spectrum with floor
            cleaned_magnitude = np.maximum(magnitude - 2.0 * noise_spectrum, 0.1 * magnitude)

            # Reconstruct signal
            cleaned_Zxx = cleaned_magnitude * np.exp(1j * phase)
            _, output = scipy_signal.istft(cleaned_Zxx, fs=self.sample_rate, nperseg=256)

            return output[:len(audio_data)]

        except ImportError:
            logger.warning("scipy not available for spectral subtraction, returning original audio")
            return audio_data


class AudioFilterChain:
    """
    Manages a chain of audio filters applied in sequence.
    """

    def __init__(self, sample_rate=16000):
        """
        Initialize filter chain.

        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        self.filters = []
        logger.info(f"AudioFilterChain initialized at {sample_rate}Hz")

    def add_noise_gate(self, enabled=True, **kwargs):
        """Add noise gate to chain."""
        if enabled:
            self.filters.append(NoiseGate(sample_rate=self.sample_rate, **kwargs))
            logger.info("Added NoiseGate to filter chain")

    def add_rnnoise(self, enabled=True):
        """Add RNNoise to chain."""
        if enabled:
            self.filters.append(RNNoise(sample_rate=self.sample_rate))
            logger.info("Added RNNoise to filter chain")

    def add_compressor(self, enabled=True, **kwargs):
        """Add compressor to chain."""
        if enabled:
            self.filters.append(EnhancedCompressor(sample_rate=self.sample_rate, **kwargs))
            logger.info("Added EnhancedCompressor to filter chain")

    def process(self, audio_data):
        """
        Process audio through all filters in chain.

        Args:
            audio_data: numpy array of audio samples

        Returns:
            Filtered audio data
        """
        output = audio_data.copy()
        for filter_obj in self.filters:
            output = filter_obj.process(output)
        return output

    def clear(self):
        """Remove all filters from chain."""
        self.filters.clear()
        logger.info("Filter chain cleared")
