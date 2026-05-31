"""
Unit tests for transcription.formatters module.
"""
import pytest


class TestFormatters:
    """Tests for transcription formatters."""

    def test_format_vtt_timestamp_zero(self):
        from transcription.formatters import format_vtt_timestamp
        assert format_vtt_timestamp(0) == "00:00:00.000"

    def test_format_vtt_timestamp_seconds(self):
        from transcription.formatters import format_vtt_timestamp
        assert format_vtt_timestamp(61.5) == "00:01:01.500"

    def test_format_vtt_timestamp_hours(self):
        from transcription.formatters import format_vtt_timestamp
        assert format_vtt_timestamp(3661.123) == "01:01:01.123"

    def test_format_timestamp_readable(self):
        from transcription.formatters import format_timestamp_readable
        result = format_timestamp_readable(61)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_calculate_quality_score(self):
        from transcription.formatters import calculate_quality_score
        result = {'segments': [{'text': 'hello world', 'start': 0, 'end': 1}]}
        score = calculate_quality_score(result)
        assert isinstance(score, float)
        assert 0 <= score <= 100
