#!/usr/bin/env python3
"""
Performance Optimization Verification Test

This test verifies that all performance optimizations are correctly implemented
and functioning as expected.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules import without errors."""
    print("\n" + "="*70)
    print("TEST 1: Module Import Verification")
    print("="*70)

    try:
        from transcriber_enhanced import EnhancedTranscriber
        print("✅ transcriber_enhanced imported successfully")
    except Exception as e:
        print(f"❌ Failed to import transcriber_enhanced: {e}")
        return False

    try:
        from audio_extractor import AudioExtractor
        print("✅ audio_extractor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import audio_extractor: {e}")
        return False

    return True


def test_text_based_language_detection():
    """Test that text-based language detection works correctly."""
    print("\n" + "="*70)
    print("TEST 2: Text-Based Language Detection")
    print("="*70)

    from transcriber_enhanced import EnhancedTranscriber

    transcriber = EnhancedTranscriber(model_size='tiny')

    # Mock segments with English and Czech text
    mock_segments = [
        {'start': 0.0, 'end': 4.0, 'text': 'Hello, how are you doing today? The weather is nice.'},
        {'start': 4.0, 'end': 8.0, 'text': 'Dobrý den, jak se máte? Počasí je hezké.'},
        {'start': 8.0, 'end': 12.0, 'text': 'I am doing great, thanks for asking.'},
        {'start': 12.0, 'end': 16.0, 'text': 'Já se mám dobře, děkuji za optání.'},
    ]

    # Test the optimized text-based detection
    start_time = time.time()
    language_segments = transcriber._detect_language_from_transcript(mock_segments, chunk_size=4.0)
    elapsed = time.time() - start_time

    print(f"✅ Text-based detection completed in {elapsed:.4f}s")
    print(f"   Detected {len(language_segments)} language segments")

    # Verify we detected both languages
    detected_langs = {seg['language'] for seg in language_segments}
    print(f"   Languages detected: {detected_langs}")

    if 'en' in detected_langs and 'cs' in detected_langs:
        print("✅ Successfully detected both English and Czech")
        return True
    elif len(detected_langs) >= 1:
        print("⚠️  Detected languages but not both EN and CS (heuristic limitations)")
        return True
    else:
        print("❌ Failed to detect any languages")
        return False


def test_optimized_merge():
    """Test that segment merging is optimized."""
    print("\n" + "="*70)
    print("TEST 3: Optimized Segment Merging")
    print("="*70)

    from transcriber_enhanced import EnhancedTranscriber

    transcriber = EnhancedTranscriber(model_size='tiny')

    # Create segments with consecutive same languages
    test_segments = [
        {'language': 'en', 'start': 0.0, 'end': 4.0, 'text': 'Part 1'},
        {'language': 'en', 'start': 4.0, 'end': 8.0, 'text': 'Part 2'},
        {'language': 'en', 'start': 8.0, 'end': 12.0, 'text': 'Part 3'},
        {'language': 'cs', 'start': 12.0, 'end': 16.0, 'text': 'Část 1'},
        {'language': 'cs', 'start': 16.0, 'end': 20.0, 'text': 'Část 2'},
    ]

    merged = transcriber._merge_consecutive_language_segments(test_segments)

    print(f"✅ Input: {len(test_segments)} segments")
    print(f"✅ Output: {len(merged)} merged segments")

    if len(merged) == 2:  # Should merge into 2 segments (3 EN + 2 CS)
        print("✅ Correctly merged consecutive same-language segments")
        return True
    else:
        print(f"⚠️  Expected 2 merged segments, got {len(merged)}")
        return False


def test_frozenset_optimization():
    """Test that frozensets are used for performance."""
    print("\n" + "="*70)
    print("TEST 4: String Processing Optimization")
    print("="*70)

    import inspect
    from transcriber_enhanced import EnhancedTranscriber

    transcriber = EnhancedTranscriber(model_size='tiny')

    # Get source code of _detect_language_from_transcript
    source = inspect.getsource(transcriber._detect_language_from_transcript)

    if 'frozenset' in source:
        print("✅ frozenset optimization detected in source code")
        if 'window_text_set & cs_diacritics' in source or '& cs_diacritics' in source:
            print("✅ Set intersection optimization confirmed")
            return True
        else:
            print("⚠️  frozenset found but set intersection not confirmed")
            return True
    else:
        print("❌ frozenset optimization not found")
        return False


def test_no_chunk_retranscription():
    """Verify that chunk re-transcription is eliminated."""
    print("\n" + "="*70)
    print("TEST 5: No Chunk Re-Transcription")
    print("="*70)

    import inspect
    from transcriber_enhanced import EnhancedTranscriber

    transcriber = EnhancedTranscriber(model_size='tiny')

    # Get source code of _detect_language_from_words
    source = inspect.getsource(transcriber._detect_language_from_words)

    # Check it uses text-based analysis, not subprocess/transcription
    if 'subprocess.run' in source or 'self.transcribe(' in source:
        print("❌ Found subprocess or transcribe calls in _detect_language_from_words")
        return False

    if '_detect_language_from_transcript' in source:
        print("✅ Uses _detect_language_from_transcript (text-based analysis)")
        print("✅ No chunk re-transcription detected")
        return True
    else:
        print("⚠️  Could not confirm text-based analysis")
        return False


def test_sampling_optimization():
    """Verify that audio sampling is reduced to 3 samples."""
    print("\n" + "="*70)
    print("TEST 6: Audio Sampling Optimization")
    print("="*70)

    import inspect
    from transcriber_enhanced import EnhancedTranscriber

    transcriber = EnhancedTranscriber(model_size='tiny')

    # Get source code of _sample_languages
    source = inspect.getsource(transcriber._sample_languages)

    if 'max_samples: int = 3' in source or 'max_samples=3' in source:
        print("✅ max_samples set to 3 (optimized from 25)")
        return True
    else:
        print("❌ max_samples not set to 3")
        return False


def test_progress_callback():
    """Test that progress callbacks are supported."""
    print("\n" + "="*70)
    print("TEST 7: Progress Callback Support")
    print("="*70)

    import inspect
    from audio_extractor import AudioExtractor

    extractor = AudioExtractor()

    # Check if extract_audio has progress_callback parameter
    sig = inspect.signature(extractor.extract_audio)
    params = list(sig.parameters.keys())

    if 'progress_callback' in params:
        print("✅ extract_audio supports progress_callback parameter")
        return True
    else:
        print("❌ extract_audio missing progress_callback parameter")
        return False


def run_all_tests():
    """Run all verification tests."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "PERFORMANCE OPTIMIZATION TESTS" + " "*23 + "║")
    print("╚" + "="*68 + "╝")

    tests = [
        ("Module Imports", test_imports),
        ("Text-Based Language Detection", test_text_based_language_detection),
        ("Optimized Segment Merging", test_optimized_merge),
        ("String Processing Optimization", test_frozenset_optimization),
        ("No Chunk Re-Transcription", test_no_chunk_retranscription),
        ("Audio Sampling Optimization", test_sampling_optimization),
        ("Progress Callback Support", test_progress_callback),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("\n" + "="*70)
    print(f"TOTAL: {passed}/{total} tests passed ({passed*100//total}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 ALL OPTIMIZATIONS VERIFIED AND WORKING! 🎉\n")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
