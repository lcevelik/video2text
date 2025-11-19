# Audio Setup Guide - Cross-Platform

This guide helps you set up audio recording for FonixFlow on macOS, Windows, and Linux.

## Quick Start

FonixFlow can record:
- **🎤 Microphone** - Your voice
- **🔊 System Audio** - YouTube videos, music, video calls, etc.

Both sources are captured simultaneously and mixed together for optimal transcription.

---

## macOS Setup

### Microphone Setup

**Grant Microphone Permissions:**
1. Open **System Settings** (or **System Preferences** on older macOS)
2. Go to **Privacy & Security** → **Microphone**
3. Enable permission for FonixFlow or your Terminal app
4. Restart the app and click "🔄 Refresh Devices"

### System Audio Capture (YouTube, Music, etc.)

macOS doesn't have built-in system audio capture. You need to install a virtual audio device:

#### Option 1: BlackHole (Recommended - Free & Open Source)

**Install via Homebrew:**
```bash
brew install blackhole-2ch
```

**Manual Download:**
1. Visit: https://github.com/ExistentialAudio/BlackHole
2. Download and install BlackHole 2ch
3. Restart FonixFlow
4. Click "🔄 Refresh Devices"
5. Select "BlackHole 2ch" as Speaker/System device

#### Option 2: Soundflower (Alternative)

1. Visit: https://github.com/mattingalls/Soundflower
2. Download and install Soundflower
3. Restart FonixFlow
4. Select "Soundflower (2ch)" as Speaker/System device

---

## Windows Setup

### Microphone Setup

**Grant Microphone Permissions:**
1. Open **Settings** → **Privacy** → **Microphone**
2. Enable "Allow apps to access your microphone"
3. Enable permission for FonixFlow
4. Click "🔄 Refresh Devices" in the app

### System Audio Capture (YouTube, Music, etc.)

#### Method 1: Enable Stereo Mix (Built-in on most systems)

1. Right-click the **speaker icon** in system tray
2. Select **"Sounds"** or **"Sound Settings"**
3. Go to the **"Recording"** tab
4. Right-click in empty space
5. Check **"Show Disabled Devices"**
6. Right-click **"Stereo Mix"** and select **"Enable"**
7. Click "🔄 Refresh Devices" in FonixFlow
8. Select "Stereo Mix" as Speaker/System device

#### Method 2: Virtual Audio Cable (if Stereo Mix unavailable)

1. Download **VB-Audio Virtual Cable**: https://vb-audio.com/Cable/
2. Install the software
3. Restart FonixFlow
4. Click "🔄 Refresh Devices"
5. Select "CABLE Output" as Speaker/System device

---

## Linux Setup

### Microphone Setup

**Check Audio System:**
1. Verify your microphone is not muted in system settings
2. Check available devices:
   ```bash
   arecord -l
   ```
3. Click "🔄 Refresh Devices" in the app

### System Audio Capture (YouTube, Music, etc.)

Linux audio varies by system (PulseAudio, PipeWire, ALSA). Here are the common setups:

#### PulseAudio (Ubuntu, Debian, Fedora)

**Load Loopback Module:**
```bash
pactl load-module module-loopback
```

**Make it Permanent:**
Add to `/etc/pulse/default.pa`:
```
load-module module-loopback
```

**Monitor Devices:**
PulseAudio automatically creates monitor devices for each output. Look for devices ending in `.monitor` in the Speaker/System dropdown.

#### PipeWire (Modern Distributions)

PipeWire usually works out of the box with virtual devices. Monitor devices are automatically available for capturing application audio.

#### ALSA Loopback

**Load ALSA Loopback Module:**
```bash
sudo modprobe snd-aloop
```

**Make it Permanent:**
Add to `/etc/modules`:
```
snd-aloop
```

---

## Troubleshooting

### No Microphone Detected

**macOS:**
- Check System Settings → Privacy & Security → Microphone
- Ensure permission is granted for FonixFlow or Terminal
- Try unplugging/replugging USB microphones

**Windows:**
- Check Settings → Privacy → Microphone
- Ensure "Allow apps to access your microphone" is enabled
- Check Device Manager for driver issues

**Linux:**
- Run `arecord -l` to list recording devices
- Check if microphone is muted in system settings
- Verify PulseAudio/PipeWire is running: `pactl info`

### No System Audio Device

**macOS:**
- BlackHole or Soundflower **must** be installed
- System audio capture is not built-in on macOS
- After installing, restart the app

**Windows:**
- Stereo Mix might be disabled - follow Method 1 above
- Some systems lack Stereo Mix - use Virtual Audio Cable (Method 2)

**Linux:**
- Load loopback module for PulseAudio: `pactl load-module module-loopback`
- Check for monitor devices: `pactl list sources | grep monitor`

### VU Meters Not Moving

1. Click **"🔍 Test Audio Levels"**
2. Speak into microphone - mic meter should bounce
3. Play YouTube video - speaker meter should bounce
4. If neither moves:
   - Check device selection in dropdowns
   - Verify devices in system sound settings
   - Click "🔄 Refresh Devices"

### Recording Works But No System Audio

**macOS:**
- Ensure BlackHole/Soundflower is selected as Speaker/System device
- Configure macOS to send audio to BlackHole:
  - Open Audio MIDI Setup
  - Create Multi-Output Device with BlackHole + Built-in Output

**Windows:**
- Verify Stereo Mix or Virtual Cable is enabled
- Set it as default recording device temporarily
- Ensure it's selected in FonixFlow dropdowns

**Linux:**
- Ensure monitor device is selected (ends with `.monitor`)
- Check PulseAudio/PipeWire mixer settings

---

## Features

### Audio Level Testing
- Click **"🔍 Test Audio Levels"** before recording
- VU meters show real-time audio from both sources
- Green → Yellow → Orange → Red colors indicate level
- Speak and play audio to verify capture

### Device Selection
- Choose specific microphone from dropdown
- Choose specific system audio device from dropdown
- Devices show index numbers for advanced troubleshooting

### Automatic Gain Control (AGC)
- Automatically adjusts audio levels
- Quiet voices: boosted up to 20dB
- Loud sources: reduced to prevent distortion
- 3:1 dynamic range compression
- Optimal levels for Whisper AI transcription

### Platform Detection
- App automatically detects your OS
- Shows platform-specific setup instructions
- Click **"❓ Setup Guide"** for full help

---

## Support

**App Issues:**
- Check logs for detailed device information
- Click "🔄 Refresh Devices" after connecting new devices
- Grant permissions when prompted

**Audio Quality:**
- Test levels before recording important content
- Ensure VU meters show green/yellow during test
- Red indicates too loud (will be compressed)
- Barely moving indicates too quiet (will be boosted)

**YouTube/System Audio Not Working:**
- Most common issue: loopback device not installed/enabled
- Follow platform-specific instructions above
- Click "❓ Setup Guide" in the app for detailed steps

---

## Technical Details

- **Sample Rate:** 16 kHz (optimal for Whisper)
- **Channels:** Mono (1 channel)
- **Format:** MP3 @ 320 kbps
- **Mix Ratio:** 60% mic + 40% speaker
- **Normalization:** RMS-based with soft clipping
- **Compression:** 3:1 ratio above threshold
- **AGC:** Up to 10x gain boost for quiet audio

---

For more help, click the **"❓ Setup Guide"** button in the app for platform-specific instructions.
