"""
Language Detection Module

This module contains language detection heuristics and utilities for
identifying languages in transcribed text.
"""

import logging
import tempfile
import os
import subprocess
from typing import Dict, List, Optional, Any
from transcriber import Transcriber

logger = logging.getLogger(__name__)

# Language code to name mapping
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'pl': 'Polish',
    'nl': 'Dutch',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'he': 'Hebrew',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'tr': 'Turkish',
    'cs': 'Czech',
    'ro': 'Romanian',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
    'el': 'Greek',
    'hi': 'Hindi',
    'id': 'Indonesian',
    'uk': 'Ukrainian',
    'unknown': 'Unknown'
}

# Stopwords dictionaries for language detection
STOPWORDS = {
    'en': frozenset(["the","and","is","are","to","of","in","that","for","you","it","on","with","this","be","have","at","or","as","i","we","they","was","were","will","would","can","could","a","an","from","by","about","what","which","who","how","do","does","did","not","if","there","their","them","our","your"]),
    'es': frozenset(["el","la","los","las","un","una","unos","unas","de","y","en","a","que","por","con","para","como","es","su","al","lo","se","del","más","pero","sus","le","ya","o","este","sí","porque","esta","entre","cuando","muy","sin","sobre","también","me","hasta","hay","donde","quien","desde","todo","nos","durante","todos","uno","les","ni","contra","otros","ese","eso","ante","ellos","e","esto","mí","antes","algunos","qué","unos","yo","otro","otras","otra"]),
    'fr': frozenset(["le","la","les","un","une","des","du","de","et","en","à","que","il","elle","nous","vous","ils","elles","au","aux","avec","par","sur","pas","plus","mais","ou","comme","son","sa","ses","leur","leurs","est","sont","été","être","a","ont","avait","avais","avais","fut","fûmes","fûtes","furent"]),
    'de': frozenset(["der","die","das","ein","eine","eines","einer","einem","den","dem","des","und","zu","mit","auf","für","von","im","ist","war","wurde","werden","wie","als","auch","an","bei","nach","vor","aus","durch","über","unter","zwischen","gegen","ohne","um","am","aber","nur","noch","schon","man","sein","ihre","ihr","seine","uns","euch","sie","wir","du","er","es"]),
    'it': frozenset(["il","lo","la","i","gli","le","un","una","uno","di","a","da","in","con","su","per","tra","fra","che","non","più","ma","come","se","quando","dove","chi","quale","quelli","questo","questa","questi","queste","sono","era","erano","essere","avere","ha","hanno","abbiamo","avete","avevano"]),
    'pt': frozenset(["o","a","os","as","um","uma","uns","umas","de","da","do","das","dos","em","por","para","com","sem","sobre","entre","mas","ou","se","que","quando","como","onde","quem","qual","quais","este","esta","estes","estas","aquele","aquela","aqueles","aquelas","foi","eram","ser","ter","tem","têm","tinha","tínhamos","tinham"]),
    'pl': frozenset(["i","w","z","na","do","od","za","po","przez","dla","o","u","pod","nad","przed","bez","czy","nie","tak","ale","lub","albo","to","ten","ta","te","ci","co","który","która","które","którzy","być","jest","są","był","była","było","byli","były"]),
    'nl': frozenset(["de","het","een","en","van","op","in","naar","met","voor","door","over","onder","tussen","tegen","zonder","om","maar","of","als","ook","bij","tot","uit","aan","te","er","je","jij","hij","zij","wij","jullie","zij","ik","ben","is","zijn","was","waren"]),
    'ru': frozenset(["и","в","во","не","что","он","на","я","с","со","как","а","то","все","она","так","его","но","да","ты","к","у","же","вы","за","бы","по","ее","мне","было","вот","от","меня","еще","нет","о","из","ему","теперь","когда","даже","ну","вдруг","ли","если","уже","или","ни","быть","был","него","до","вас","нибудь","опять","уж","вам","ведь","там","потом","себя","ничего","ей","может","они","тут","где","есть","надо","ней","для","мы","тебя","их","чем","была","сам","чтоб","без","будто","чего","раз","тоже","себе","под","будет","ж","тогда","кто","этот"]),
    'cs': frozenset(["a","i","že","co","jak","když","ale","už","proto","tak","by","byl","byla","bylo","byli","aby","jsem","jsme","jste","jsi","být","mít","ten","to","ta","tento","tato","toto","se","si","na","v","ve","z","ze","do","s","o","u","k","pro","který","která","které","kteří","protože","je","není","může","tady","tam","taky","ještě"]),
}

# Diacritics for language detection
DIACRITICS = {
    'en': frozenset(),
    'es': frozenset("áéíóúüñÁÉÍÓÚÜÑ"),
    'fr': frozenset("àâäéèêëîïôöùûüÿçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇ"),
    'de': frozenset("äöüßÄÖÜ"),
    'it': frozenset("àèéìîòóùÀÈÉÌÎÒÓÙ"),
    'pt': frozenset("áâãàçéêíóôõúÁÂÃÀÇÉÊÍÓÔÕÚ"),
    'pl': frozenset("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"),
    'nl': frozenset("éèëïöüÉÈËÏÖÜ"),
    'ru': frozenset(),
    'cs': frozenset("áéíóúůýčďěňřšťžÁÉÍÓÚŮÝČĎĚŇŘŠŤŽ"),
}


def guess_language_from_text(text: str) -> str:
    """
    Guess language from text using character patterns.

    Args:
        text: Text to analyze

    Returns:
        Guessed language code
    """
    if not text:
        return 'unknown'

    # Check for specific character ranges
    has_cjk = any('\u4e00' <= char <= '\u9fff' or
                  '\u3040' <= char <= '\u309f' or
                  '\u30a0' <= char <= '\u30ff' or
                  '\uac00' <= char <= '\ud7af' for char in text)

    has_arabic = any('\u0600' <= char <= '\u06ff' for char in text)
    has_cyrillic = any('\u0400' <= char <= '\u04ff' for char in text)
    has_hebrew = any('\u0590' <= char <= '\u05ff' for char in text)
    has_thai = any('\u0e00' <= char <= '\u0e7f' for char in text)

    if has_cjk:
        # Could be Chinese, Japanese, or Korean
        if any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
            return 'ja'  # Japanese
        elif any('\uac00' <= char <= '\ud7af' for char in text):
            return 'ko'  # Korean
        else:
            return 'zh'  # Chinese
    elif has_arabic:
        return 'ar'
    elif has_cyrillic:
        return 'ru'
    elif has_hebrew:
        return 'he'
    elif has_thai:
        return 'th'
    else:
        # Default to Latin-based (could be any European language)
        return 'en'


def detect_language_from_transcript(
    segments: List[Dict[str, Any]],
    chunk_size: float = 2.0,
    audio_path: Optional[str] = None,
    allowed_languages: Optional[List[str]] = None,
    audio_fallback_model: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """
    Heuristic segmentation using existing segment text (no extra audio passes).

    Restricted to allowed languages if provided. Chooses a single best language per window.

    Args:
        segments: List of transcript segments
        chunk_size: Size of time windows in seconds
        audio_path: Optional path to audio file for fallback detection
        allowed_languages: Optional list of allowed language codes
        audio_fallback_model: Optional cached model for audio fallback

    Returns:
        List of language segments with detected languages
    """
    if not segments:
        return []

    end_time = segments[-1].get('end', 0)
    windows = []
    t = 0.0
    while t < end_time:
        windows.append((t, min(t + chunk_size, end_time)))
        t += chunk_size

    # Filter stopwords and diacritics by allowed languages
    stopwords = STOPWORDS
    diacritics = DIACRITICS

    if allowed_languages:
        stopwords = {k: v for k, v in STOPWORDS.items() if k in allowed_languages}
        diacritics = {k: v for k, v in DIACRITICS.items() if k in allowed_languages}

    heuristic_langs = set(stopwords.keys())
    needs_audio_fallback = bool(allowed_languages) and any(lang not in heuristic_langs for lang in allowed_languages)

    classified = []
    seg_index = 0
    prev_lang = None

    for (ws, we) in windows:
        texts = []
        idx = seg_index
        while idx < len(segments) and segments[idx].get('start', 0) < we:
            if segments[idx].get('end', 0) > ws:
                texts.append(segments[idx].get('text', ''))
            idx += 1
        seg_index = idx
        window_text = ' '.join(texts).strip()

        if not window_text:
            continue

        lower = window_text.lower()
        words = [w.strip(".,!?;:") for w in lower.split() if w.strip()]

        if not words:
            continue

        window_text_set = set(window_text)
        lang_scores = {}

        for lang_code, stops in stopwords.items():
            stop_hits = sum(1 for w in words if w in stops)
            diacritic_hits = len(window_text_set & diacritics.get(lang_code, frozenset()))
            # Weight stopwords more heavily (2x) as they're more reliable indicators
            score = (stop_hits * 2) + diacritic_hits
            lang_scores[lang_code] = score

        # Choose best language (single) with threshold
        best_lang = None
        best_score = 0
        for lc, sc in lang_scores.items():
            if sc > best_score:
                best_lang = lc
                best_score = sc

        # Log scoring for debugging
        if lang_scores:
            logger.debug(f"Window [{ws:.1f}-{we:.1f}s] heuristic scores: {lang_scores} | best: {best_lang}({best_score}) | text: {window_text[:50]}...")

        # If heuristic is uncertain, use audio fallback
        use_audio_fallback = False
        if audio_path and needs_audio_fallback:
            use_audio_fallback = (best_score < 5)
        elif audio_path and (best_lang is None or best_score == 0):
            use_audio_fallback = True
        elif audio_path and allowed_languages and len(allowed_languages) > 1:
            sorted_scores = sorted(lang_scores.items(), key=lambda x: x[1], reverse=True)
            if len(sorted_scores) >= 2:
                best_score_val = sorted_scores[0][1]
                second_score_val = sorted_scores[1][1]
                if best_score_val > 0 and (best_score_val - second_score_val) / best_score_val < 0.3:
                    use_audio_fallback = True
                    logger.debug(f"Window [{ws:.1f}-{we:.1f}s] scores too close ({best_score_val:.1f} vs {second_score_val:.1f}), using audio fallback")

        if use_audio_fallback and audio_fallback_model:
            try:
                detected = classify_language_window_audio(
                    audio_path, ws, we,
                    allowed_languages if allowed_languages else list(LANGUAGE_NAMES.keys()),
                    audio_fallback_model
                )
                if detected:
                    logger.debug(f"Window [{ws:.1f}-{we:.1f}s] audio fallback detected: {detected} (heuristic was: {best_lang})")
                    best_lang = detected
                    best_score = 100
            except Exception as _af_err:
                logger.debug(f"Audio fallback classification failed: {_af_err}")

        if best_lang is None or best_score == 0:
            # Fallback inherit previous or use first allowed language
            best_lang = prev_lang if prev_lang else ('unknown' if not allowed_languages else allowed_languages[0])

        prev_lang = best_lang
        classified.append({'language': best_lang, 'start': ws, 'end': we, 'text': window_text})

    # Merge adjacent same-language windows
    merged = []
    for seg in classified:
        if merged and merged[-1]['language'] == seg['language']:
            merged[-1]['end'] = seg['end']
            if '_texts' not in merged[-1]:
                merged[-1]['_texts'] = [merged[-1]['text']]
            merged[-1]['_texts'].append(seg['text'])
        else:
            merged.append(seg.copy())

    for m in merged:
        if '_texts' in m:
            m['text'] = ' '.join(m['_texts'])
            del m['_texts']

    logger.info(f"Fast transcript-based segmentation produced {len(merged)} segments (languages: {sorted({m['language'] for m in merged})})")
    return merged


def classify_language_window_audio(
    audio_path: str,
    start: float,
    end: float,
    allowed_languages: Optional[List[str]] = None,
    model_instance: Optional[Any] = None,
    model_name: str = 'tiny'
) -> Optional[str]:
    """
    Classify a window's language via a quick audio-based check.

    Args:
        audio_path: Path to audio file
        start: Start time in seconds
        end: End time in seconds
        allowed_languages: Optional list of allowed language codes
        model_instance: Optional cached model instance
        model_name: Model size to use if no instance provided

    Returns:
        Language code or None if detection fails
    """
    duration = max(0.1, end - start)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_path = temp_audio.name

    try:
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', audio_path,
            '-ss', str(start),
            '-t', str(duration),
            '-ar', '16000', '-ac', '1', temp_path
        ]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        if model_instance:
            r = model_instance.transcribe(temp_path, language=None, word_timestamps=False)
        else:
            transcriber = Transcriber(model_size=model_name)
            r = transcriber.transcribe(temp_path, language=None, word_timestamps=False)

        lang = r.get('language', 'unknown')
        if allowed_languages:
            if lang not in allowed_languages:
                return None
        return lang
    except Exception as e:
        logger.debug(f"Window audio classification failed: {e}")
        return None
    finally:
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
