#!/usr/bin/env python3
"""
Comprehensive recording test for FonixFlow.
Tests microphone, system audio, and combined recording.
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def test_recording():
    print("=" * 70)
    print("🎙️  FONIXFLOW RECORDING TEST")
    print("=" * 70)
    print()

    # Step 1: Import dependencies
    print("Step 1: Importing dependencies...")
    print("-" * 70)

    try:
        import sounddevice as sd
        import numpy as np
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        from gui.workers import RecordingWorker
        from gui.utils import get_audio_devices
        print("✅ All dependencies imported successfully")
    except Exception as e:
        print(f"❌ Failed to import dependencies: {e}")
        print("\nPlease run: pip install -r requirements.txt")
        return

    print()

    # Step 2: List devices
    print("Step 2: Detecting audio devices...")
    print("-" * 70)

    try:
        mics, speakers = get_audio_devices()

        print(f"\n📱 Microphones found: {len(mics)}")
        for idx, name in mics[:3]:  # Show top 3
            print(f"   [{idx}] {name}")

        print(f"\n🔊 System audio devices found: {len(speakers)}")
        for idx, name in speakers[:3]:  # Show top 3
            print(f"   [{idx}] {name}")

        if not mics and not speakers:
            print("\n❌ No audio devices found!")
            print("   Please connect audio devices and run diagnose_audio.py")
            return

        # Select devices for testing
        mic_device = mics[0][0] if mics else None
        speaker_device = speakers[0][0] if speakers else None

        print(f"\n✅ Will use:")
        if mic_device is not None:
            print(f"   Microphone: [{mic_device}] {mics[0][1]}")
        if speaker_device is not None:
            print(f"   System Audio: [{speaker_device}] {speakers[0][1]}")

    except Exception as e:
        print(f"❌ Error detecting devices: {e}")
        import traceback
        traceback.print_exc()
        return

    print()

    # Step 3: Test recordings
    print("Step 3: Running recording tests...")
    print("-" * 70)

    # Create output directory
    output_dir = Path.home() / "FonixFlow" / "Recordings" / "Tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}\n")

    # Create Qt Application (required for QThread workers)
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Test configurations
    tests = []

    if mic_device is not None:
        tests.append({
            'name': 'Microphone Only',
            'mic': mic_device,
            'speaker': None,
            'duration': 5,
            'description': 'Speak into your microphone'
        })

    if speaker_device is not None:
        tests.append({
            'name': 'System Audio Only',
            'mic': None,
            'speaker': speaker_device,
            'duration': 5,
            'description': 'Play audio from YouTube/music/etc.'
        })

    if mic_device is not None and speaker_device is not None:
        tests.append({
            'name': 'Microphone + System Audio',
            'mic': mic_device,
            'speaker': speaker_device,
            'duration': 5,
            'description': 'Speak while playing audio (for meetings)'
        })

    if not tests:
        print("❌ No tests to run (no devices available)")
        return

    # Run each test
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(tests)}: {test['name']}")
        print(f"{'='*70}")
        print(f"📝 {test['description']}")
        print(f"⏱️  Duration: {test['duration']} seconds")
        print()

        input(f"Press ENTER to start test {i}...")

        # Recording state
        result = {'success': False, 'path': None, 'error': None}

        def on_complete(path, duration):
            result['success'] = True
            result['path'] = path
            print(f"\n✅ Recording complete: {path} ({duration:.1f}s)")
            QTimer.singleShot(500, app.quit)

        def on_error(msg):
            result['error'] = msg
            print(f"\n❌ Recording error: {msg}")
            QTimer.singleShot(500, app.quit)

        def on_level(mic_level, speaker_level):
            # Display audio levels
            mic_bar = '█' * int(mic_level * 20)
            spk_bar = '█' * int(speaker_level * 20)
            print(f"\r🎤 {mic_bar:<20} | 🔊 {spk_bar:<20}", end='', flush=True)

        # Create worker
        worker = RecordingWorker(
            output_dir=str(output_dir),
            mic_device=test['mic'],
            speaker_device=test['speaker'],
            filter_settings={
                'noise_gate_enabled': True,
                'noise_gate_threshold': -32.0,
                'rnnoise_enabled': False,  # Disable for faster processing
                'use_enhanced_compressor': True
            }
        )

        worker.recording_complete.connect(on_complete)
        worker.recording_error.connect(on_error)
        worker.audio_level.connect(on_level)

        # Start recording
        print(f"🔴 Recording for {test['duration']} seconds...")
        print("Audio levels:")
        worker.start()

        # Stop after duration
        QTimer.singleShot(test['duration'] * 1000, worker.stop)

        # Safety timeout
        QTimer.singleShot((test['duration'] + 5) * 1000, app.quit)

        # Run event loop
        app.exec()

        print()  # New line after level display

        # Check result
        if result['success']:
            print(f"✅ Test {i} PASSED")
            print(f"   File: {result['path']}")

            # Analyze the file
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(result['path'])
                print(f"   Duration: {len(audio)/1000:.1f}s")
                print(f"   Sample rate: {audio.frame_rate}Hz")
                print(f"   Channels: {audio.channels}")
            except Exception as e:
                print(f"   ⚠️  Could not analyze file: {e}")
        else:
            print(f"❌ Test {i} FAILED")
            if result['error']:
                print(f"   Error: {result['error']}")

        print()

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"\nAll test recordings saved to: {output_dir}")
    print("\n✅ Next steps:")
    print("   1. Listen to the recordings to verify audio quality")
    print("   2. For system audio tests, make sure audio was actually playing")
    print("   3. If system audio is silent, check AUDIO_SETUP.md for configuration")
    print("\n💡 Tips for identifying the right system audio device:")
    print("   - Windows: Look for 'Stereo Mix' or device with '[Output Loopback]'")
    print("   - macOS: Look for 'BlackHole' or 'Soundflower'")
    print("   - Linux: Look for devices with 'monitor' or '.monitor' in the name")
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_recording()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
