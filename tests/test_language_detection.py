"""
Unit tests for transcription.language_detection module.
"""
import pytest


class TestLanguageNames:
    """Tests for LANGUAGE_NAMES constant."""

    def test_language_names_is_dict(self):
        from transcription.language_detection import LANGUAGE_NAMES
        assert isinstance(LANGUAGE_NAMES, dict)

    def test_common_languages_present(self):
        from transcription.language_detection import LANGUAGE_NAMES
        for code in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']:
            assert code in LANGUAGE_NAMES

    def test_unknown_language(self):
        from transcription.language_detection import LANGUAGE_NAMES
        assert 'unknown' in LANGUAGE_NAMES
        assert LANGUAGE_NAMES['unknown'] == 'Unknown'

    def test_all_values_are_strings(self):
        from transcription.language_detection import LANGUAGE_NAMES
        for key, value in LANGUAGE_NAMES.items():
            assert isinstance(key, str)
            assert isinstance(value, str)


class TestStopwords:
    """Tests for STOPWORDS constant."""

    def test_stopwords_is_dict(self):
        from transcription.language_detection import STOPWORDS
        assert isinstance(STOPWORDS, dict)

    def test_stopwords_are_frozensets(self):
        from transcription.language_detection import STOPWORDS
        for key, value in STOPWORDS.items():
            assert isinstance(value, frozenset)

    def test_english_stopwords(self):
        from transcription.language_detection import STOPWORDS
        assert 'en' in STOPWORDS
        assert 'the' in STOPWORDS['en']
        assert 'and' in STOPWORDS['en']


class TestDiacritics:
    """Tests for DIACRITICS constant."""

    def test_diacritics_is_dict(self):
        from transcription.language_detection import DIACRITICS
        assert isinstance(DIACRITICS, dict)

    def test_english_has_no_diacritics(self):
        from transcription.language_detection import DIACRITICS
        assert 'en' in DIACRITICS
        assert len(DIACRITICS['en']) == 0
