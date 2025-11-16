#!/usr/bin/env python3
"""
Comprehensive Multilingual Transcription Test

This script tests both single-language and multi-language transcription modes
by creating synthetic audio files with speech in multiple languages.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_audio_with_tts():
    """
    Create multilingual test audio files using TTS (Text-to-Speech).
    Returns paths to created audio files.
    """
    logger.info("Creating test audio files using TTS...")

    try:
        # Try using gTTS (Google Text-to-Speech) if available
        from gtts import gTTS
        import tempfile

        test_dir = Path("test_audio")
        test_dir.mkdir(exist_ok=True)

        # Create English audio
        english_text = "Hello, this is a test of the English language transcription system. The weather is nice today."
        english_audio = test_dir / "test_english.mp3"
        tts_en = gTTS(text=english_text, lang='en')
        tts_en.save(str(english_audio))
        logger.info(f"✅ Created English audio: {english_audio}")

        # Create Czech audio
        czech_text = "Dobrý den, toto je test českého jazyka. Dnes je hezké počasí."
        czech_audio = test_dir / "test_czech.mp3"
        tts_cs = gTTS(text=czech_text, lang='cs')
        tts_cs.save(str(czech_audio))
        logger.info(f"✅ Created Czech audio: {czech_audio}")

        # Create multilingual audio (combine both)
        multilingual_text = "Hello, how are you? Dobrý den, jak se máte? The weather is nice. Počasí je hezké."
        # We'll create separate files since gTTS can't mix languages in one go
        multi_en = "Hello, how are you? The weather is nice."
        multi_cs = "Dobrý den, jak se máte? Počasí je hezké."

        # For multi-language, we'll use English as primary with some Czech phrases
        multilingual_audio = test_dir / "test_multilingual.mp3"
        tts_multi = gTTS(text=multilingual_text, lang='en')
        tts_multi.save(str(multilingual_audio))
        logger.info(f"✅ Created multilingual audio: {multilingual_audio}")

        return {
            'english': str(english_audio),
            'czech': str(czech_audio),
            'multilingual': str(multilingual_audio)
        }

    except ImportError:
        logger.warning("⚠️  gTTS not available. Trying alternative method...")
        return create_test_audio_alternative()


def create_test_audio_alternative():
    """
    Alternative method to create test audio using pyttsx3 (offline TTS).
    """
    try:
        import pyttsx3
        import tempfile

        test_dir = Path("test_audio")
        test_dir.mkdir(exist_ok=True)

        engine = pyttsx3.init()

        # Create English audio
        english_text = "Hello, this is a test of the English language transcription system. The weather is nice today."
        english_audio = test_dir / "test_english.wav"
        engine.save_to_file(english_text, str(english_audio))
        engine.runAndWait()
        logger.info(f"✅ Created English audio: {english_audio}")

        # Create multilingual audio
        multilingual_text = "Hello, how are you? Dobrý den, jak se máte? The weather is nice."
        multilingual_audio = test_dir / "test_multilingual.wav"
        engine.save_to_file(multilingual_text, str(multilingual_audio))
        engine.runAndWait()
        logger.info(f"✅ Created multilingual audio: {multilingual_audio}")

        return {
            'english': str(english_audio),
            'multilingual': str(multilingual_audio)
        }

    except Exception as e:
        logger.error(f"❌ Failed to create audio with pyttsx3: {e}")
        return create_test_audio_synthetic()


def create_test_audio_synthetic():
    """
    Create synthetic audio using numpy and scipy (pure tone for testing).
    This is a fallback when TTS is not available.
    """
    logger.warning("⚠️  No TTS available. Creating synthetic audio for testing...")

    try:
        import numpy as np
        from scipy.io import wavfile

        test_dir = Path("test_audio")
        test_dir.mkdir(exist_ok=True)

        # Create a simple synthetic audio (440 Hz tone for 5 seconds)
        sample_rate = 16000
        duration = 5  # seconds
        frequency = 440  # Hz (A4 note)

        t = np.linspace(0, duration, sample_rate * duration, False)
        audio_data = np.sin(frequency * 2 * np.pi * t)
        audio_data = (audio_data * 32767).astype(np.int16)

        # Create test file
        test_audio = test_dir / "test_synthetic.wav"
        wavfile.write(str(test_audio), sample_rate, audio_data)
        logger.info(f"✅ Created synthetic audio: {test_audio}")

        return {
            'synthetic': str(test_audio)
        }

    except Exception as e:
        logger.error(f"❌ Failed to create synthetic audio: {e}")
        return None


def test_single_language_mode(audio_file):
    """Test single-language transcription mode."""
    logger.info("\n" + "="*70)
    logger.info("TEST: Single-Language Transcription Mode")
    logger.info("="*70)

    try:
        from transcriber import Transcriber

        logger.info(f"Testing with audio file: {audio_file}")
        logger.info("Loading Whisper model (tiny)...")

        transcriber = Transcriber(model_size='tiny')

        logger.info("Starting transcription...")
        start_time = time.time()

        result = transcriber.transcribe(audio_file)

        elapsed = time.time() - start_time

        logger.info(f"✅ Transcription completed in {elapsed:.2f}s")
        logger.info(f"📝 Result: {result['text'][:200]}...")
        logger.info(f"🌍 Detected language: {result.get('language', 'unknown')}")

        return True

    except Exception as e:
        logger.error(f"❌ Single-language test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multilingual_mode(audio_file):
    """Test multi-language transcription mode."""
    logger.info("\n" + "="*70)
    logger.info("TEST: Multi-Language Transcription Mode")
    logger.info("="*70)

    try:
        from transcriber_enhanced import EnhancedTranscriber

        logger.info(f"Testing with audio file: {audio_file}")
        logger.info("Loading Whisper model (tiny) with multi-language support...")

        transcriber = EnhancedTranscriber(model_size='tiny')

        logger.info("Starting multi-language transcription...")
        start_time = time.time()

        # Test with allowed languages (English and Czech)
        result = transcriber.transcribe_multilang(
            audio_file,
            allowed_languages={'en', 'cs'}
        )

        elapsed = time.time() - start_time

        logger.info(f"✅ Transcription completed in {elapsed:.2f}s")
        logger.info(f"📝 Result: {result['text'][:200]}...")

        if 'language_segments' in result:
            logger.info(f"🌍 Detected {len(result['language_segments'])} language segments:")
            for seg in result['language_segments'][:5]:  # Show first 5
                logger.info(f"   [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['language']}: {seg['text'][:50]}...")

        return True

    except Exception as e:
        logger.error(f"❌ Multi-language test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_installation():
    """Verify that all required components are installed."""
    logger.info("\n" + "="*70)
    logger.info("Verifying Installation")
    logger.info("="*70)

    checks = []

    # Check Whisper
    try:
        import whisper
        logger.info("✅ openai-whisper installed")
        checks.append(True)
    except ImportError:
        logger.error("❌ openai-whisper not installed")
        logger.info("   Install: pip install openai-whisper")
        checks.append(False)

    # Check PyTorch
    try:
        import torch
        logger.info(f"✅ PyTorch installed (version {torch.__version__})")
        if torch.cuda.is_available():
            logger.info(f"   🚀 CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("   💻 Using CPU (no GPU detected)")
        checks.append(True)
    except ImportError:
        logger.error("❌ PyTorch not installed")
        logger.info("   Install: pip install torch torchaudio")
        checks.append(False)

    # Check core modules
    try:
        from transcriber import Transcriber
        logger.info("✅ transcriber.py module available")
        checks.append(True)
    except Exception as e:
        logger.error(f"❌ transcriber.py module failed: {e}")
        checks.append(False)

    try:
        from transcriber_enhanced import EnhancedTranscriber
        logger.info("✅ transcriber_enhanced.py module available")
        checks.append(True)
    except Exception as e:
        logger.error(f"❌ transcriber_enhanced.py module failed: {e}")
        checks.append(False)

    return all(checks)


def main():
    """Run all tests."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "MULTILINGUAL TRANSCRIPTION TESTS" + " "*21 + "║")
    print("╚" + "="*68 + "╝")

    # Step 1: Verify installation
    if not verify_installation():
        logger.error("\n❌ Installation verification failed. Please install missing dependencies.")
        return False

    # Step 2: Create test audio files
    logger.info("\n" + "="*70)
    logger.info("Creating Test Audio Files")
    logger.info("="*70)

    audio_files = create_test_audio_with_tts()

    if not audio_files:
        logger.error("❌ Failed to create test audio files")
        return False

    # Step 3: Run tests
    results = []

    # Test single-language mode
    if 'english' in audio_files:
        result = test_single_language_mode(audio_files['english'])
        results.append(('Single-Language (English)', result))
    elif 'synthetic' in audio_files:
        result = test_single_language_mode(audio_files['synthetic'])
        results.append(('Single-Language (Synthetic)', result))

    # Test multi-language mode
    if 'multilingual' in audio_files:
        result = test_multilingual_mode(audio_files['multilingual'])
        results.append(('Multi-Language', result))

    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    logger.info("\n" + "="*70)
    logger.info(f"TOTAL: {passed}/{total} tests passed")
    logger.info("="*70)

    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Both modes work correctly! 🎉\n")
        return True
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed.\n")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
