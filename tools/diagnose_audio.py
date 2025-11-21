#!/usr/bin/env python3
"""
Comprehensive audio diagnostics for FonixFlow recording.
Run this script to debug recording issues and identify the right devices.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def main():
    print("=" * 70)
    print(" FONIXFLOW AUDIO DIAGNOSTICS")
    print("=" * 70)
    print()

    # Step 1: Check imports
    print("Step 1: Checking dependencies...")
    print("-" * 70)

    missing = []
    try:
        import sounddevice as sd
        print("sounddevice: OK")
    except Exception as e:
        print(f"sounddevice: FAILED - {e}")
        missing.append("sounddevice")

    try:
        import numpy as np
        print("numpy: OK")
    except Exception as e:
        print(f"numpy: FAILED - {e}")
        missing.append("numpy")

    try:
        import scipy
        print("scipy: OK")
    except Exception as e:
        print(f"scipy: FAILED - {e}")
        missing.append("scipy")

    try:
        from pydub import AudioSegment
        print("pydub: OK")
    except Exception as e:
        print(f"pydub: FAILED - {e}")
        missing.append("pydub")

    try:
        from PySide6.QtCore import QThread
        print("PySide6: OK")
    except Exception as e:
        print(f"PySide6: FAILED - {e}")
        missing.append("PySide6")

    if missing:
        print(f"\n Missing dependencies: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return

    print()

    # Step 2: Check PortAudio
    print("Step 2: Checking PortAudio library...")
    print("-" * 70)
    try:
        devices = sd.query_devices()
        print(f"PortAudio: OK ({len(devices)} devices found)")
    except OSError as e:
        print(f"PortAudio: NOT FOUND")
        print(f"   Error: {e}")
        print(f"   Install:")
        print(f"     - Windows: Comes with sounddevice")
        print(f"     - macOS: brew install portaudio")
        print(f"     - Linux: sudo apt-get install portaudio19-dev")
        return
    except Exception as e:
        print(f"PortAudio: ERROR - {e}")
        return

    print()

    # Step 3: List all devices
    print("Step 3: Enumerating all audio devices...")
    print("-" * 70)

    hostapis = sd.query_hostapis()
    print(f"Found {len(devices)} devices across {len(hostapis)} host APIs\n")

    for idx, device in enumerate(devices):
        name = device['name']
        input_ch = device['max_input_channels']
        output_ch = device['max_output_channels']
        sample_rate = device.get('default_samplerate', 'N/A')
        hostapi_idx = device.get('hostapi', -1)

        hostapi_name = "Unknown"
        if hostapi_idx >= 0 and hostapi_idx < len(hostapis):
            hostapi_name = hostapis[hostapi_idx]['name']

        device_type = []
        if input_ch > 0:
            device_type.append(f"INPUT ({input_ch}ch)")
        if output_ch > 0:
            device_type.append(f"OUTPUT ({output_ch}ch)")

        type_str = " + ".join(device_type) if device_type else "NO CHANNELS"

        print(f"[{idx:2d}] {name}")
        print(f"      {type_str}")
        print(f"      Host API: {hostapi_name}")
        print(f"      Sample Rate: {sample_rate} Hz")
        print()

    # Step 4: Use get_audio_devices
    print()
    print("Step 4: Using FonixFlow device categorization...")
    print("-" * 70)

    try:
        from gui.utils import get_audio_devices

        mics, speakers = get_audio_devices()

        print(f"\nMICROPHONES ({len(mics)}):")
        if mics:
            for idx, name in mics:
                print(f"  [{idx:2d}] {name}")
        else:
            print("  No microphones found!")
            print("     Make sure a microphone is connected and enabled")

        print(f"\nSYSTEM AUDIO DEVICES ({len(speakers)}):")
        print("   (These capture what you hear - for YouTube, meetings, etc.)")
        if speakers:
            for idx, name in speakers:
                print(f"  [{idx:2d}] {name}")
        else:
            print("  No system audio devices found!")
            print("     You need to enable a loopback device:")
            print("       Windows: Enable 'Stereo Mix' in Sound Settings")
            print("       macOS: Install BlackHole (brew install blackhole-2ch)")
            print("       Linux: Load loopback module (pactl load-module module-loopback)")

    except Exception as e:
        print(f"Error using get_audio_devices: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Step 5: Recommendations
    print()
    print("Step 5: Recommendations for recording...")
    print("-" * 70)

    if mics and speakers:
        print("READY TO RECORD!")
        print(f"\n   For MICROPHONE recording:")
        print(f"     • Use device: [{mics[0][0]}] {mics[0][1]}")
        print(f"\n   For SYSTEM AUDIO (YouTube/meetings):")
        print(f"     • Use device: [{speakers[0][0]}] {speakers[0][1]}")
        print(f"\n   For BOTH (mic + system audio):")
        print(f"     • Microphone: [{mics[0][0]}] {mics[0][1]}")
        print(f"     • System Audio: [{speakers[0][0]}] {speakers[0][1]}")
    elif mics:
        print(" PARTIAL SETUP")
        print(f"\n   Microphone available: [{mics[0][0]}] {mics[0][1]}")
        print(f"   No system audio device found")
        print(f"\n   To capture YouTube/meetings, you need a loopback device.")
        print(f"   See AUDIO_SETUP.md for instructions.")
    elif speakers:
        print(" PARTIAL SETUP")
        print(f"\n   No microphone found")
        print(f"   System audio available: [{speakers[0][0]}] {speakers[0][1]}")
        print(f"\n   Connect a microphone to record your voice.")
    else:
        print("NO DEVICES FOUND")
        print("\n   Please check:")
        print("     1. Audio devices are connected")
        print("     2. Drivers are installed")
        print("     3. Devices are enabled in system settings")
        print("     4. Permissions are granted for microphone access")

    print()
    print("=" * 70)
    print("For detailed setup instructions, see: AUDIO_SETUP.md")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
