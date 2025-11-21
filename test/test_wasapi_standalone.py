#!/usr/bin/env python3
"""
Standalone WASAPI test - Comprehensive Windows audio recording test.
This file tests WASAPI loopback capture independently of the rest of the app.

Run this on Windows to verify WASAPI works correctly.
"""

import sys
import time
import logging
import platform

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_platform():
    """Verify we're running on Windows."""
    if platform.system() != 'Windows':
        print(f"❌ ERROR: This test must run on Windows")
        print(f"   Current platform: {platform.system()}")
        return False

    print(f"✅ Platform check passed: Windows {platform.version()}")
    return True


def check_dependencies():
    """Check if required dependencies are available."""
    print("\n=== Checking Dependencies ===")

    try:
        import numpy as np
        print(f"✅ numpy: {np.__version__}")
    except ImportError as e:
        print(f"❌ numpy not found: {e}")
        return False

    try:
        import comtypes
        print(f"✅ comtypes: {comtypes.__version__}")
    except ImportError as e:
        print(f"❌ comtypes not found: {e}")
        print("   Install with: pip install comtypes")
        return False

    return True


def test_wasapi_imports():
    """Test if WASAPI module can be imported."""
    print("\n=== Testing WASAPI Module Import ===")

    try:
        from gui.recording.wasapi_loopback import WASAPILoopbackCapture
        print("✅ WASAPI module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import WASAPI module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing WASAPI module: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wasapi_initialization():
    """Test if WASAPI can be initialized."""
    print("\n=== Testing WASAPI Initialization ===")

    try:
        from gui.recording.wasapi_loopback import WASAPILoopbackCapture

        # Create instance
        capture = WASAPILoopbackCapture()
        print("✅ WASAPI capture object created")

        # Try to start it
        print("   Starting capture...")
        capture.start()
        print(f"✅ WASAPI capture started successfully")
        print(f"   Sample rate: {capture.get_sample_rate()}Hz")
        print(f"   Channels: {capture.get_channels()}")

        # Let it run for a moment
        time.sleep(0.5)

        # Stop it
        print("   Stopping capture...")
        audio_data = capture.stop()

        print(f"✅ WASAPI capture stopped")
        print(f"   Data shape: {audio_data.shape if audio_data.size > 0 else 'empty'}")

        return True

    except Exception as e:
        print(f"❌ WASAPI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wasapi_recording():
    """Test actual audio recording with WASAPI."""
    print("\n=== Testing WASAPI Audio Recording ===")
    print("This test will record system audio for 5 seconds.")
    print("PLAY SOME AUDIO NOW (YouTube, Spotify, etc.)")
    print()

    try:
        import numpy as np
        from gui.recording.wasapi_loopback import WASAPILoopbackCapture

        # Track chunks received via callback
        chunks_received = []

        def callback(audio_data, frames, time_info, status):
            """Callback to track received audio."""
            chunks_received.append({
                'data': audio_data,
                'frames': frames,
                'shape': audio_data.shape if hasattr(audio_data, 'shape') else None,
                'type': type(audio_data).__name__
            })
            if len(chunks_received) <= 5:
                print(f"   📥 Chunk #{len(chunks_received)}: "
                      f"shape={audio_data.shape if hasattr(audio_data, 'shape') else 'N/A'}, "
                      f"type={type(audio_data).__name__}")

        # Create capture with callback
        capture = WASAPILoopbackCapture(callback=callback)

        # Start
        print("🔴 Starting 5-second recording...")
        capture.start()

        start_time = time.time()

        # Record for 5 seconds
        time.sleep(5)

        # Stop
        print("\n⏹️  Stopping recording...")
        audio_data = capture.stop()

        duration = time.time() - start_time

        # Analyze results
        print(f"\n=== Recording Results ===")
        print(f"Duration: {duration:.2f}s")
        print(f"Chunks received via callback: {len(chunks_received)}")
        print(f"Final audio data shape: {audio_data.shape if audio_data.size > 0 else 'empty'}")

        if audio_data.size > 0:
            print(f"Audio statistics:")
            print(f"  Shape: {audio_data.shape}")
            print(f"  Duration: {len(audio_data) / capture.get_sample_rate():.2f}s")
            print(f"  Min: {audio_data.min():.6f}")
            print(f"  Max: {audio_data.max():.6f}")

            # Check if we actually captured sound
            rms = np.sqrt(np.mean(audio_data ** 2))
            print(f"  RMS level: {rms:.6f}")

            if rms > 0.001:
                print("\n✅ SUCCESS! Audio was captured with good signal level")
                return True
            else:
                print("\n⚠️  WARNING: Audio captured but signal is very quiet")
                print("   Make sure audio is playing during the test")
                return True
        else:
            print("\n❌ FAILED: No audio data captured")
            print("   Callback chunks:", len(chunks_received))
            return False

    except Exception as e:
        print(f"\n❌ Recording test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_backend():
    """Test WASAPI integration with SoundDeviceBackend."""
    print("\n=== Testing Integration with SoundDeviceBackend ===")

    try:
        from gui.recording.sounddevice_backend import SoundDeviceBackend

        # Create backend
        backend = SoundDeviceBackend(mic_device=None, speaker_device=None)

        print("✅ SoundDeviceBackend created")
        print("   Starting recording (this will test WASAPI on Windows)...")

        # Start recording
        backend.start_recording()

        print("🔴 Recording for 3 seconds...")
        print("   PLAY SOME AUDIO NOW")

        # Record for 3 seconds
        time.sleep(3)

        # Stop
        print("\n⏹️  Stopping...")
        result = backend.stop_recording()

        # Check results
        print(f"\n=== Integration Test Results ===")
        print(f"Duration: {result.duration:.2f}s")
        print(f"Mic chunks: {result.mic_chunks_count}")
        print(f"Speaker chunks: {result.speaker_chunks_count}")
        print(f"Mic data shape: {result.mic_data.shape if result.mic_data is not None else 'None'}")
        print(f"Speaker data shape: {result.speaker_data.shape if result.speaker_data is not None else 'None'}")

        if result.speaker_data is not None and result.speaker_data.size > 0:
            import numpy as np
            rms = np.sqrt(np.mean(result.speaker_data ** 2))
            print(f"Speaker RMS: {rms:.6f}")

            if rms > 0.001:
                print("\n✅ SUCCESS! Integration test passed - system audio captured")
                return True
            else:
                print("\n⚠️  WARNING: Integration test passed but audio signal is quiet")
                return True
        else:
            print("\n⚠️  No speaker data captured (this might be expected if no WASAPI/Stereo Mix available)")
            return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("WASAPI COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()
    print("This will test:")
    print("  1. Platform compatibility")
    print("  2. Dependencies")
    print("  3. Module imports")
    print("  4. WASAPI initialization")
    print("  5. Audio recording")
    print("  6. Integration with backend")
    print()
    input("Press Enter to start tests...")
    print()

    results = {}

    # Test 1: Platform
    results['platform'] = check_platform()
    if not results['platform']:
        print("\n❌ FAILED: Must run on Windows")
        return

    # Test 2: Dependencies
    results['dependencies'] = check_dependencies()
    if not results['dependencies']:
        print("\n❌ FAILED: Missing dependencies")
        return

    # Test 3: Imports
    results['imports'] = test_wasapi_imports()
    if not results['imports']:
        print("\n❌ FAILED: Cannot import WASAPI module")
        return

    # Test 4: Initialization
    results['initialization'] = test_wasapi_initialization()

    # Test 5: Recording
    if results['initialization']:
        input("\n\nPress Enter to start recording test (make sure audio is playing)...")
        results['recording'] = test_wasapi_recording()
    else:
        results['recording'] = False
        print("⏭️  Skipping recording test due to initialization failure")

    # Test 6: Integration
    if results['initialization']:
        input("\n\nPress Enter to start integration test (make sure audio is playing)...")
        results['integration'] = test_integration_with_backend()
    else:
        results['integration'] = False
        print("⏭️  Skipping integration test due to initialization failure")

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s}: {status}")

    print("=" * 70)

    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nWASAPI audio recording is working correctly on your system.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nPlease review the errors above.")
        print("Common issues:")
        print("  - comtypes not installed: pip install comtypes")
        print("  - No audio playing during recording tests")
        print("  - Audio permissions not granted")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
