#!/usr/bin/env python3
"""Test script to list all available audio devices."""
import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sounddevice as sd

print("=== Available Audio Devices ===\n")

devices = sd.query_devices()
hostapis = sd.query_hostapis()

print(f"Total devices found: {len(devices)}\n")

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

    print(f"[{idx}] {name}")
    print(f"    Type: {type_str}")
    print(f"    Host API: {hostapi_name}")
    print(f"    Sample Rate: {sample_rate} Hz")
    print()

# Now use the get_audio_devices function
print("\n=== Using get_audio_devices() ===\n")
from gui.utils import get_audio_devices

mics, speakers = get_audio_devices()

print(f"\nMICROPHONES ({len(mics)}):")
for idx, name in mics:
    print(f"  [{idx}] {name}")

print(f"\nSYSTEM AUDIO / SPEAKERS ({len(speakers)}):")
for idx, name in speakers:
    print(f"  [{idx}] {name}")

print("\n=== Recommendations ===")
print("\nFor recording MICROPHONE:")
if mics:
    print(f"  Use device index: {mics[0][0]} ({mics[0][1]})")
else:
    print("  No microphone found!")

print("\nFor recording SYSTEM AUDIO (YouTube, meetings, etc.):")
if speakers:
    print(f"  Use device index: {speakers[0][0]} ({speakers[0][1]})")
    print("     This device can capture what you hear on your computer")
else:
    print("  No system audio device found!")
    print("     You may need to enable 'Stereo Mix' or install a virtual audio cable")
