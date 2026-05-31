"""
Unit tests for app.transcriber module.
"""
import pytest
import os
import sys
import threading
from unittest.mock import patch, MagicMock


class TestProgressInterceptor:
    """Tests for ProgressInterceptor class."""

    def test_init(self):
        from app.transcriber import ProgressInterceptor
        mock_stderr = MagicMock()
        interceptor = ProgressInterceptor(mock_stderr, base_percent=50, range_percent=45)
        assert interceptor.original_stderr == mock_stderr
        assert interceptor.base_percent == 50
        assert interceptor.range_percent == 45
        assert interceptor.buffer == ""

    def test_write_forwards_to_original_stderr(self):
        from app.transcriber import ProgressInterceptor
        mock_stderr = MagicMock()
        interceptor = ProgressInterceptor(mock_stderr)
        interceptor.write("hello")
        mock_stderr.write.assert_called_once_with("hello")

    def test_write_with_none_stderr(self):
        from app.transcriber import ProgressInterceptor
        interceptor = ProgressInterceptor(None)
        # Should not raise
        interceptor.write("hello")

    def test_write_parses_progress(self):
        from app.transcriber import ProgressInterceptor
        callback = MagicMock()
        interceptor = ProgressInterceptor(MagicMock(), progress_callback=callback, base_percent=50, range_percent=45)
        interceptor.write("  50%|████▌     | 10/20")
        callback.assert_called_once()
        args = callback.call_args[0]
        assert "50%" in args[0]
        assert args[1] == 50 + int((50 / 100.0) * 45)

    def test_flush_forwards(self):
        from app.transcriber import ProgressInterceptor
        mock_stderr = MagicMock()
        interceptor = ProgressInterceptor(mock_stderr)
        interceptor.flush()
        mock_stderr.flush.assert_called_once()


class TestModelCache:
    """Tests for model cache eviction."""

    def test_cache_constants_exist(self):
        from app.transcriber import _MAX_CACHED_MODELS, _GLOBAL_MODEL_CACHE, _GLOBAL_CACHE_ACCESS_ORDER, _GLOBAL_CACHE_LOCK
        assert _MAX_CACHED_MODELS == 2
        assert isinstance(_GLOBAL_MODEL_CACHE, dict)
        assert isinstance(_GLOBAL_CACHE_ACCESS_ORDER, list)
        assert isinstance(_GLOBAL_CACHE_LOCK, type(threading.Lock()))

    def test_license_xor_key_exists(self):
        from app.transcriber import LICENSE_XOR_KEY
        assert isinstance(LICENSE_XOR_KEY, bytes)
        assert len(LICENSE_XOR_KEY) > 0


class TestTranscriber:
    """Tests for Transcriber class."""

    def test_model_sizes(self):
        from app.transcriber import Transcriber
        assert 'tiny' in Transcriber.MODEL_SIZES
        assert 'base' in Transcriber.MODEL_SIZES
        assert 'small' in Transcriber.MODEL_SIZES
        assert 'medium' in Transcriber.MODEL_SIZES
        assert 'large' in Transcriber.MODEL_SIZES
        assert 'tiny.en' in Transcriber.MODEL_SIZES

    def test_speed_factors(self):
        from app.transcriber import Transcriber
        for size in ['tiny', 'base', 'small', 'medium', 'large']:
            assert size in Transcriber.SPEED_FACTORS
            assert 'cpu' in Transcriber.SPEED_FACTORS[size]
            assert 'cuda' in Transcriber.SPEED_FACTORS[size]

    def test_estimate_transcription_time(self):
        from app.transcriber import Transcriber
        result = Transcriber.estimate_transcription_time(100, 'base', 'cpu')
        assert result['total_seconds'] > 0
        assert result['transcription_seconds'] > 0
        assert result['formatted_time'] != 'Unknown'

    def test_estimate_transcription_time_zero_duration(self):
        from app.transcriber import Transcriber
        result = Transcriber.estimate_transcription_time(0, 'base', 'cpu')
        assert result['total_seconds'] is None
        assert result['formatted_time'] == 'Unknown'

    def test_format_estimated_time_seconds(self):
        from app.transcriber import Transcriber
        assert Transcriber._format_estimated_time(30) == "30 seconds"

    def test_format_estimated_time_minutes(self):
        from app.transcriber import Transcriber
        assert Transcriber._format_estimated_time(90) == "1m 30s"

    def test_format_estimated_time_hours(self):
        from app.transcriber import Transcriber
        assert Transcriber._format_estimated_time(3660) == "1h 1m"

    def test_format_estimated_time_none(self):
        from app.transcriber import Transcriber
        assert Transcriber._format_estimated_time(None) == "Unknown"

    def test_get_model_description(self):
        from app.transcriber import Transcriber
        desc = Transcriber.get_model_description('base')
        assert 'description' in desc
        assert 'speed' in desc
        assert 'accuracy' in desc
        assert 'use_case' in desc

    def test_get_model_description_en_variant(self):
        from app.transcriber import Transcriber
        desc = Transcriber.get_model_description('base.en')
        assert 'English-only' in desc['description']

    def test_format_timestamp(self):
        from app.transcriber import Transcriber
        t = Transcriber.__new__(Transcriber)
        assert t._format_timestamp(0) == "00:00:00,000"
        assert t._format_timestamp(61.5) == "00:01:01,500"
        assert t._format_timestamp(3661.123) == "01:01:01,123"

    def test_subprocess_run_wrapper_exists(self):
        from transcription.enhanced import _subprocess_run
        assert callable(_subprocess_run)
