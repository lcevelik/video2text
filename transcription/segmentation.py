"""
Audio Segmentation Module

This module contains logic for two-pass comprehensive audio segmentation
with pipelined execution for multi-language transcription.
"""

import logging
import tempfile
import os
import subprocess
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from app.transcriber import Transcriber
from tools.resource_locator import get_ffmpeg_path

logger = logging.getLogger(__name__)


def merge_consecutive_language_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge consecutive segments that have the same language.

    OPTIMIZED: Reduced unnecessary copying - only copy when needed.

    Args:
        segments: List of language segments

    Returns:
        Merged list with consecutive same-language segments combined
    """
    if not segments:
        return []

    merged = []
    # Start with a copy of the first segment for merging (optimized with list accumulation)
    current = {
        'language': segments[0]['language'],
        'start': segments[0]['start'],
        'end': segments[0]['end'],
        '_texts': [segments[0]['text']]  # Accumulate texts in list
    }

    for segment in segments[1:]:
        if segment['language'] == current['language']:
            # Same language - merge with current (accumulate text efficiently)
            current['end'] = segment['end']
            current['_texts'].append(segment['text'])
        else:
            # Different language - finalize current and start new
            current['text'] = ' '.join(current['_texts'])
            del current['_texts']
            merged.append(current)
            # Create new current segment (only copy when switching languages)
            current = {
                'language': segment['language'],
                'start': segment['start'],
                'end': segment['end'],
                '_texts': [segment['text']]
            }

    # Finalize and add the last segment
    current['text'] = ' '.join(current['_texts'])
    del current['_texts']
    merged.append(current)

    return merged


def retranscribe_segments(
    transcriber: Any,
    audio_path: str,
    segments: List[Dict[str, Any]],
    progress_callback=None
) -> List[Dict[str, Any]]:
    """
    Re-transcribe each segment individually to detect its specific language.

    This is the KEY to true multi-language transcription. By transcribing
    each segment separately, Whisper can detect the correct language for that
    specific segment instead of assuming one language for the entire audio.

    Args:
        transcriber: Transcriber instance to use
        audio_path: Path to the full audio file
        segments: List of segments from initial transcription
        progress_callback: Optional callback for progress updates

    Returns:
        List of language segments with accurate per-segment language detection
    """
    language_segments = []
    total_segments = len(segments)

    logger.info(f"Re-transcribing {total_segments} segments for accurate language detection")

    for i, segment in enumerate(segments):
        start_time = segment.get('start', 0)
        end_time = segment.get('end', 0)
        duration = end_time - start_time

        if duration < 0.1:  # Skip very short segments
            continue

        # Progress update
        if progress_callback and i % 5 == 0:  # Update every 5 segments
            progress_callback(f"Language detection: {i+1}/{total_segments} segments")

        # Extract audio segment using ffmpeg
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_path = temp_audio.name

        try:
            # Use ffmpeg to extract the specific time range
            ffmpeg_path = get_ffmpeg_path()
            subprocess.run([
                ffmpeg_path, '-i', audio_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-ar', '16000',  # Whisper expects 16kHz
                '-ac', '1',       # Mono
                '-y',             # Overwrite
                temp_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            # Transcribe this segment alone to detect its language
            segment_result = transcriber.transcribe(
                temp_path,
                language=None,  # Auto-detect for THIS segment
                progress_callback=None  # Don't spam progress for each segment
            )

            detected_lang = segment_result.get('language', 'unknown')
            transcribed_text = segment_result.get('text', '').strip()

            logger.debug(f"Segment {i}: {detected_lang} - {transcribed_text[:50]}...")

            # Add to our language segments
            language_segments.append({
                'language': detected_lang,
                'start': start_time,
                'end': end_time,
                'text': transcribed_text
            })

        except Exception as e:
            logger.error(f"Failed to re-transcribe segment {i}: {e}")
            # Fallback: use original segment text with unknown language
            language_segments.append({
                'language': 'unknown',
                'start': start_time,
                'end': end_time,
                'text': segment.get('text', '').strip()
            })
        finally:
            # Always clean up temp file
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")

    # Merge consecutive segments with the same language
    merged_segments = merge_consecutive_language_segments(language_segments)

    logger.info(f"Detected {len(set(s['language'] for s in merged_segments))} unique languages")

    return merged_segments


# Note: The two-pass pipelined segmentation is complex and tightly integrated with the EnhancedTranscriber class.
# It remains in the main enhanced.py file for now to avoid circular dependencies and maintain model caching logic.
# Future refactoring could extract it with careful dependency management.
