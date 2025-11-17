#!/usr/bin/env python3
"""
Quick debug script to test recording with full logging output.
This shows exactly what's happening during recording.
"""
import sys
import os
import logging
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

def main():
    print("=" * 70)
    print("🔍 RECORDING DEBUG TEST WITH FULL LOGGING")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Show detailed logs of recording process")
    print("  2. Reveal exactly where the issue is")
    print("  3. Record for 3 seconds")
    print()

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from gui.workers import RecordingWorker
    from gui.utils import get_audio_devices

    # Get devices
    print("Detecting devices...")
    mics, speakers = get_audio_devices()

    if not mics:
        print("❌ No microphone found!")
        print("   Please connect a microphone and try again.")
        return

    print(f"\n✅ Using microphone: [{mics[0][0]}] {mics[0][1]}")
    if speakers:
        print(f"✅ Using speaker: [{speakers[0][0]}] {speakers[0][1]}")
    else:
        print("⚠️  No system audio device (will record mic only)")

    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Output directory
    output_dir = Path.home() / "Video2Text" / "Recordings" / "Debug"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Create worker
    worker = RecordingWorker(
        output_dir=str(output_dir),
        mic_device=mics[0][0],
        speaker_device=speakers[0][0] if speakers else None,
        filter_settings={
            'noise_gate_enabled': False,  # Disable filters for debugging
            'rnnoise_enabled': False,
            'use_enhanced_compressor': False
        }
    )

    # Result tracking
    result = {'success': False, 'error': None}

    def on_complete(path, duration):
        result['success'] = True
        print(f"\n{'='*70}")
        print(f"✅ SUCCESS! Recording saved: {path}")
        print(f"   Duration: {duration:.1f}s")
        print(f"{'='*70}")
        QTimer.singleShot(500, app.quit)

    def on_error(msg):
        result['error'] = msg
        print(f"\n{'='*70}")
        print(f"❌ FAILED!")
        print(f"   Error: {msg}")
        print(f"{'='*70}")
        QTimer.singleShot(500, app.quit)

    def on_level(mic, spk):
        # Show simple level indicator
        mic_bar = '█' * int(mic * 10)
        spk_bar = '█' * int(spk * 10)
        print(f"\r🎤 {mic_bar:<10} 🔊 {spk_bar:<10}", end='', flush=True)

    worker.recording_complete.connect(on_complete)
    worker.recording_error.connect(on_error)
    worker.audio_level.connect(on_level)

    # Start
    print(f"\n{'='*70}")
    print("🔴 RECORDING FOR 3 SECONDS...")
    print("Watch the logs above for detailed diagnostics!")
    print(f"{'='*70}\n")

    worker.start()

    # Stop after 3 seconds
    QTimer.singleShot(3000, worker.stop)

    # Safety timeout
    QTimer.singleShot(6000, app.quit)

    # Run
    app.exec()

    print()  # New line after level bars

    # Analysis
    if result['success']:
        print("\n✅ Recording worked! Check the file to verify audio quality.")
    else:
        print("\n❌ Recording failed!")
        print("\nLook at the logs above to see:")
        print("  - Did streams open? (Look for ✅ Mic stream opened)")
        print("  - How many callbacks fired? (Should be > 0)")
        print("  - How many chunks collected? (Should be > 0)")
        print("  - Any error messages or warnings?")
        print("\nCommon issues:")
        print("  - Callbacks fired: 0  →  Device not accessible or already in use")
        print("  - Chunks collected: 0  →  is_recording timing issue")
        print("  - Stream didn't open  →  Sample rate or permissions issue")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
