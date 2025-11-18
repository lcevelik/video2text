"""
Audio Processing Module

This module contains utilities for audio sampling, chunking, and
in-memory processing for faster transcription.
"""

import logging
import tempfile
import os
import subprocess
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from transcriber import Transcriber

logger = logging.getLogger(__name__)


def sample_languages(
    transcriber: Any,
    audio_path: str,
    sample_window: float = 4.0,
    max_samples: int = 3,
    min_interval: float = 300.0,
    progress_callback=None
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Sample the audio at strategic points to estimate language distribution.

    OPTIMIZED: Reduced from 3-25 samples to just 3 strategic samples (start, middle, end).
    This is sufficient for determining single vs multi-language and saves 8-15 seconds.

    Args:
        transcriber: Transcriber instance to use
        audio_path: Path to audio file
        sample_window: Window size in seconds
        max_samples: Maximum number of samples
        min_interval: Minimum interval between samples
        progress_callback: Optional progress callback

    Returns:
        Tuple of (sample_records, total_duration)
        sample_records: List[{'time': seconds, 'language': str}]
    """
    # Get total duration
    try:
        ffprobe_cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        duration_output = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT)
        total_duration = float(duration_output.decode().strip())
    except Exception as e:
        logger.warning(f"Duration probe failed: {e}; falling back to single sample")
        total_duration = 0

    if total_duration <= 0:
        # Single probe at start only
        temp_sample = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_sample.close()
        try:
            ffmpeg_cmd = ['ffmpeg', '-y', '-i', audio_path, '-t', str(sample_window), '-ar', '16000', '-ac', '1', temp_sample.name]
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            r = transcriber.transcribe(temp_sample.name, language=None, word_timestamps=False)
            return ([{'time': 0.0, 'language': r.get('language', 'unknown')}], 0.0)
        finally:
            if os.path.exists(temp_sample.name):
                os.unlink(temp_sample.name)

    # OPTIMIZED: Just 3 strategic samples - beginning, middle, end
    points = []
    points.append(min(2.0, total_duration * 0.05))  # Near beginning (2s or 5% in)
    points.append(total_duration / 2.0)  # Middle
    points.append(max(total_duration - sample_window - 2, total_duration * 0.95))  # Near end

    # Filter to valid range
    points = [p for p in points if 0 <= p < total_duration - sample_window]
    if not points:
        points = [0]  # Fallback to start

    sample_records = []
    for idx, start_time in enumerate(points):
        temp_sample = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_sample.close()
        try:
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(sample_window),
                '-ar', '16000', '-ac', '1', temp_sample.name
            ]
            subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
            if progress_callback:
                progress_callback(f"Language sampling {idx+1}/{len(points)} @ {start_time:.0f}s")
            r = transcriber.transcribe(temp_sample.name, language=None, word_timestamps=False)
            lang = r.get('language', 'unknown')
            sample_records.append({'time': start_time, 'language': lang})
            logger.debug(f"Sample {idx+1}: t={start_time:.1f}s lang={lang}")
        except Exception as e:
            logger.warning(f"Sample failed at {start_time:.1f}s: {e}")
        finally:
            if os.path.exists(temp_sample.name):
                os.unlink(temp_sample.name)

    logger.info(f"Optimized sampling complete: {len(sample_records)} samples (reduced from up to 25)")
    return sample_records, total_duration


def classify_language_mode(
    samples: List[Dict[str, Any]],
    total_duration: float,
    late_ratio: float = 0.85,
    min_secondary_hits: int = 1
) -> Dict[str, Any]:
    """
    Classify language mode based on samples.

    OPTIMIZED: Adjusted for smaller sample size (3 samples instead of up to 25).
    Now requires only 1 secondary hit instead of 2, since we have fewer samples.

    Args:
        samples: List of language samples
        total_duration: Total audio duration
        late_ratio: Threshold for hybrid classification
        min_secondary_hits: Minimum hits for secondary language

    Returns:
        Dict with keys: mode (single|mixed|hybrid), primary_language, secondary_languages, transition_time
        hybrid means second language appears only late (after late_ratio * duration).
    """
    if not samples:
        return {'mode': 'single', 'primary_language': None, 'secondary_languages': [], 'transition_time': None}

    # Tally languages
    from collections import Counter
    langs = [s['language'] for s in samples]
    counts = Counter(langs)
    primary = counts.most_common(1)[0][0]
    secondary_candidates = [l for l in counts if l != primary]

    if not secondary_candidates:
        return {'mode': 'single', 'primary_language': primary, 'secondary_languages': [], 'transition_time': None}

    # Verify secondary hits (lowered threshold for optimized 3-sample approach)
    valid_secondaries = []
    earliest_secondary_time = None
    for sec in secondary_candidates:
        hits = [s for s in samples if s['language'] == sec]
        if len(hits) >= min_secondary_hits:
            valid_secondaries.append(sec)
            tmin = min(h['time'] for h in hits)
            if earliest_secondary_time is None or tmin < earliest_secondary_time:
                earliest_secondary_time = tmin

    if not valid_secondaries:
        # Treat as single if secondaries too sparse
        return {'mode': 'single', 'primary_language': primary, 'secondary_languages': [], 'transition_time': None}

    # Decide hybrid vs mixed
    if earliest_secondary_time and total_duration > 0 and earliest_secondary_time / total_duration >= late_ratio:
        mode = 'hybrid'
    else:
        mode = 'mixed'

    return {
        'mode': mode,
        'primary_language': primary,
        'secondary_languages': valid_secondaries,
        'transition_time': earliest_secondary_time
    }


def load_audio_to_memory(audio_path: str, sample_rate: int = 16000) -> Tuple[Optional[np.ndarray], float]:
    """
    Load audio file into memory for faster chunk extraction.

    OPTIMIZATION: Loading audio once and slicing in memory is much faster than
    extracting each chunk with ffmpeg (eliminates file I/O overhead).

    Args:
        audio_path: Path to audio file
        sample_rate: Target sample rate (default: 16000 for Whisper)

    Returns:
        Tuple of (audio_data as numpy array, total_duration in seconds)
    """
    try:
        import librosa
    except ImportError:
        logger.warning("librosa not available, falling back to ffmpeg extraction")
        return None, 0.0

    try:
        # Load audio at 16kHz mono (Whisper's expected format)
        logger.debug(f"Loading audio into memory: {audio_path}")
        audio_data, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
        total_duration = len(audio_data) / sr
        logger.debug(f"Audio loaded: {total_duration:.1f}s, {len(audio_data)} samples")
        return audio_data, total_duration
    except Exception as e:
        logger.warning(f"Failed to load audio into memory: {e}, falling back to ffmpeg")
        return None, 0.0


def extract_audio_chunk_from_memory(
    audio_data: np.ndarray,
    start: float,
    end: float,
    sample_rate: int = 16000
) -> Tuple[str, float]:
    """
    Extract audio chunk from in-memory data and save to temp file.

    OPTIMIZATION: Slicing in-memory array is much faster than ffmpeg extraction.

    Args:
        audio_data: Audio data as numpy array
        start: Start time in seconds
        end: End time in seconds
        sample_rate: Sample rate of audio data

    Returns:
        Tuple of (temp_file_path, chunk_duration)
    """
    import soundfile as sf

    start_sample = int(start * sample_rate)
    end_sample = int(end * sample_rate)
    chunk_data = audio_data[start_sample:end_sample]

    # Write to temp file for Whisper
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_path = temp_audio.name

    sf.write(temp_path, chunk_data, sample_rate)
    duration = len(chunk_data) / sample_rate

    return temp_path, duration


def process_chunk_sequential(
    transcriber: Any,
    audio_path: str,
    chunk_start: float,
    chunk_end: float,
    allowed_languages: Optional[List[str]]
) -> Optional[Dict[str, Any]]:
    """
    Process a single audio chunk sequentially (no threading).

    Args:
        transcriber: Transcriber instance to use
        audio_path: Path to audio file
        chunk_start: Start time in seconds
        chunk_end: End time in seconds
        allowed_languages: List of allowed language codes

    Returns:
        Segment dict or None if failed
    """
    chunk_duration = chunk_end - chunk_start

    if chunk_duration < 0.1:
        return None

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_path = temp_audio.name

    try:
        # Extract chunk using ffmpeg with timeout
        subprocess.run([
            'ffmpeg', '-y', '-i', audio_path,
            '-ss', str(chunk_start),
            '-t', str(chunk_duration),
            '-ar', '16000', '-ac', '1',
            temp_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=30)

        # Transcribe this chunk
        chunk_result = transcriber.transcribe(
            temp_path,
            language=None,
            progress_callback=None
        )

        detected_lang = chunk_result.get('language', 'unknown')
        transcribed_text = chunk_result.get('text', '').strip()

        # Only include if language is in allowed list and has text
        if (not allowed_languages or detected_lang in allowed_languages) and transcribed_text:
            return {
                'language': detected_lang,
                'start': chunk_start,
                'end': chunk_end,
                'text': transcribed_text
            }
    except subprocess.TimeoutExpired:
        logger.warning(f"FFmpeg timeout (30s) extracting chunk [{chunk_start:.1f}-{chunk_end:.1f}s]", exc_info=True)
    except Exception as e:
        logger.warning(f"Failed to process chunk [{chunk_start:.1f}-{chunk_end:.1f}s]: {e}", exc_info=True)
    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

    return None


def process_chunk_from_memory(
    transcriber: Any,
    audio_data: np.ndarray,
    chunk_start: float,
    chunk_end: float,
    allowed_languages: Optional[List[str]],
    sample_rate: int = 16000
) -> Optional[Dict[str, Any]]:
    """
    Process a single audio chunk from in-memory data.

    Args:
        transcriber: Transcriber instance to use
        audio_data: Audio data as numpy array
        chunk_start: Start time in seconds
        chunk_end: End time in seconds
        allowed_languages: List of allowed language codes
        sample_rate: Sample rate of audio data

    Returns:
        Segment dict or None if failed
    """
    try:
        import soundfile as sf
    except ImportError:
        logger.warning("soundfile not available, cannot use in-memory processing")
        return None

    try:
        # Extract chunk from memory
        temp_path, chunk_duration = extract_audio_chunk_from_memory(
            audio_data, chunk_start, chunk_end, sample_rate
        )

        if chunk_duration < 0.1:
            return None

        try:
            # Transcribe this chunk
            chunk_result = transcriber.transcribe(
                temp_path,
                language=None,
                progress_callback=None
            )

            detected_lang = chunk_result.get('language', 'unknown')
            transcribed_text = chunk_result.get('text', '').strip()

            # Only include if language is in allowed list and has text
            if (not allowed_languages or detected_lang in allowed_languages) and transcribed_text:
                return {
                    'language': detected_lang,
                    'start': chunk_start,
                    'end': chunk_end,
                    'text': transcribed_text
                }
        finally:
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"Failed to process chunk from memory [{chunk_start:.1f}-{chunk_end:.1f}s]: {e}", exc_info=True)

    return None
