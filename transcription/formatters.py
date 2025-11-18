"""
Formatting Utilities Module

This module contains utilities for formatting transcription results,
timestamps, timelines, and reports.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Language code to name mapping (imported from language_detection)
from transcription.language_detection import LANGUAGE_NAMES


def format_timestamp_readable(seconds: float) -> str:
    """
    Format timestamp in readable format (MM:SS).

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def format_vtt_timestamp(seconds: float) -> str:
    """
    Format seconds as VTT timestamp (HH:MM:SS.mmm).

    Args:
        seconds: Time in seconds

    Returns:
        Formatted VTT timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def create_language_timeline(language_segments: List[Dict[str, Any]]) -> str:
    """
    Create a human-readable language timeline.

    Args:
        language_segments: List of language segments

    Returns:
        Formatted timeline string
    """
    timeline = []
    for segment in language_segments:
        start_str = format_timestamp_readable(segment['start'])
        end_str = format_timestamp_readable(segment['end'])
        lang_code = segment['language']
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())

        timeline.append(
            f"[{start_str} - {end_str}] Language: {lang_name} ({lang_code.upper()})"
        )

    return '\n'.join(timeline)


def format_as_vtt(transcription_result: Dict[str, Any]) -> str:
    """
    Format transcription result as VTT subtitle file.

    Args:
        transcription_result: Result dictionary from transcribe()

    Returns:
        VTT formatted subtitle content
    """
    segments = transcription_result.get('segments', [])
    vtt_content = ["WEBVTT\n"]

    for i, segment in enumerate(segments, start=1):
        start_time = format_vtt_timestamp(segment['start'])
        end_time = format_vtt_timestamp(segment['end'])
        text = segment['text'].strip()

        vtt_content.append(f"{start_time} --> {end_time}\n{text}\n")

    return "\n".join(vtt_content)


def format_multilang_report(result: Dict[str, Any]) -> str:
    """
    Format a detailed multi-language transcription report.

    Args:
        result: Enhanced transcription result with language info

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 60)
    report.append("MULTI-LANGUAGE TRANSCRIPTION REPORT")
    report.append("=" * 60)
    report.append("")

    # Overall info
    detected_lang = result.get('language', 'unknown')
    report.append(f"Primary Language: {detected_lang.upper()}")
    report.append("")

    # Language segments
    if 'language_segments' in result:
        segments = result['language_segments']
        report.append(f"Language Segments Detected: {len(segments)}")
        report.append("")

        for i, seg in enumerate(segments, 1):
            start_str = format_timestamp_readable(seg['start'])
            end_str = format_timestamp_readable(seg['end'])
            lang = seg['language']

            report.append(f"Segment {i}: {lang.upper()} [{start_str} - {end_str}]")
            report.append(f"  {seg['text'][:100]}...")
            report.append("")

    # Timeline
    if 'language_timeline' in result:
        report.append("Language Timeline:")
        report.append("-" * 60)
        report.append(result['language_timeline'])
        report.append("")

    report.append("=" * 60)

    return "\n".join(report)


def calculate_quality_score(result: Dict[str, Any]) -> float:
    """
    Calculate transcription quality score.

    Args:
        result: Transcription result

    Returns:
        Quality score (0.0 to 1.0)
    """
    segments = result.get('segments', [])
    if not segments:
        return 0.0

    total_confidence = 0.0
    count = 0

    for segment in segments:
        # Use no_speech_prob as quality indicator
        no_speech = segment.get('no_speech_prob', 0.0)
        confidence = 1.0 - no_speech

        # Also consider segment length (very short segments might be noise)
        duration = segment.get('end', 0) - segment.get('start', 0)
        text_length = len(segment.get('text', '').strip())

        # Penalize very short segments with little text
        if duration < 0.5 and text_length < 3:
            confidence *= 0.5

        total_confidence += confidence
        count += 1

    avg_confidence = total_confidence / count if count > 0 else 0.0

    logger.info(f"Calculated quality score: {avg_confidence:.3f}")
    return avg_confidence
