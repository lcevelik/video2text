# 🎙️ Recording Fix & Diagnostic Guide

## Summary

I've debugged your recording system and found/fixed several issues:

### 🐛 Bugs Fixed

1. **Critical Bug in `gui/workers.py` (line 740)**
   - **Issue**: Speaker audio filters were applied at the wrong sample rate
   - **Problem**: Filters were using `speaker_capture_rate` instead of `sample_rate_final` after resampling
   - **Impact**: This could cause audio glitches or filter failures
   - **Status**: ✅ **FIXED**

### 📦 Tools Created

I've created 3 diagnostic/test scripts to help you:

#### 1. `diagnose_audio.py` - Audio System Diagnostics
**Purpose**: Check if your audio system is properly configured

**Run this first:**
```bash
python diagnose_audio.py
```

**What it does:**
- ✅ Checks all dependencies (sounddevice, numpy, scipy, pydub, PySide6)
- ✅ Verifies PortAudio library is installed
- ✅ Lists ALL audio devices on your system
- ✅ Categorizes devices into Microphones vs System Audio
- ✅ Recommends which devices to use for recording
- ✅ Provides setup instructions if devices are missing

#### 2. `test_devices.py` - Simple Device Listing
**Purpose**: Quick view of available devices

```bash
python test_devices.py
```

**What it shows:**
- Raw list of all audio devices
- Device capabilities (input/output channels, sample rates)
- Categorized microphones and system audio devices

#### 3. `test_recording_complete.py` - Full Recording Test Suite
**Purpose**: Test actual recording functionality

```bash
python test_recording_complete.py
```

**What it tests:**
- 🎤 Microphone-only recording (5 seconds)
- 🔊 System audio-only recording (5 seconds)
- 🎙️+🔊 Combined mic + system audio (5 seconds)

**Features:**
- Real-time audio level meters
- Automatic file saving
- Quality verification
- Detailed test reports

---

## 🔍 Understanding System Audio Devices

### What is "System Audio"?

System audio = capturing what you HEAR (for recording YouTube, meetings, music, etc.)

### How to Identify System Audio Devices:

#### **Windows**
Look for these in the device list:
- ✅ **"Stereo Mix"** - Built-in loopback (must be enabled)
- ✅ Devices with **"[Output Loopback]"** tag
- ✅ Any **WASAPI** output device (speakers/headphones)

**How to Enable Stereo Mix:**
1. Right-click speaker icon → Sound Settings
2. Go to "Recording" tab
3. Right-click empty space → "Show Disabled Devices"
4. Right-click "Stereo Mix" → Enable

#### **macOS**
Look for these:
- ✅ **"BlackHole"** (install with: `brew install blackhole-2ch`)
- ✅ **"Soundflower"**
- ✅ **"Aggregate Device"** or **"Multi-Output Device"**

**macOS requires a virtual audio device** - system audio capture isn't built-in.

#### **Linux**
Look for these:
- ✅ Devices with **"monitor"** or **".monitor"** in name
- ✅ **"Monitor of [Device Name]"**
- ✅ **"Loopback"** devices

**Enable PulseAudio loopback:**
```bash
pactl load-module module-loopback
```

---

## 🚀 Quick Start - Diagnose & Fix

### Step 1: Run Diagnostics
```bash
cd /path/to/video2text
python diagnose_audio.py
```

**Expected output:**
```
✅ sounddevice: OK
✅ numpy: OK
✅ PortAudio: OK (X devices found)

📱 MICROPHONES (3):
  [0] Default Microphone — follows system
  [2] USB Microphone — System Output
  [5] Headset Mic — System Output

🔊 SYSTEM AUDIO DEVICES (2):
  [3] Stereo Mix — System Output
  [4] Speakers (Realtek) — System Output

✅ READY TO RECORD!
```

**If you see issues:**
- ❌ Missing dependencies → `pip install -r requirements.txt`
- ❌ PortAudio not found → Install system library (see below)
- ❌ No microphone → Check connections & permissions
- ❌ No system audio → Enable loopback device (see platform guides)

### Step 2: Test Recording
```bash
python test_recording_complete.py
```

Follow the prompts to test:
1. Microphone (speak into mic)
2. System audio (play YouTube/music)
3. Both together (speak while playing audio)

### Step 3: Use the Main App
```bash
python gui_qt.py
```

In the app:
1. Go to **"Record"** tab
2. Select your devices from dropdowns:
   - 🎤 **Microphone**: Pick your mic (or "Default Microphone")
   - 🔊 **Speaker/System**: Pick system audio device (Stereo Mix, BlackHole, etc.)
3. Click **"Start Recording"**

---

## 🔧 Installing System Dependencies

### PortAudio (if missing)

**Windows:**
- Should work automatically with sounddevice
- If not: Download from http://www.portaudio.com/

**macOS:**
```bash
brew install portaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev  # Debian/Ubuntu
sudo yum install portaudio-devel      # RedHat/CentOS
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install sounddevice numpy scipy pydub PySide6
```

---

## 📝 Common Issues & Solutions

### Issue 1: "No microphone found"
**Solutions:**
1. Connect a microphone
2. Check system permissions:
   - Windows: Settings → Privacy → Microphone
   - macOS: System Settings → Privacy → Microphone
   - Linux: Check PulseAudio/PipeWire settings
3. Run `python diagnose_audio.py` to verify detection

### Issue 2: "No system audio device found"
**Cause:** Your system doesn't have a loopback device enabled

**Solutions by platform:**

**Windows:**
1. Enable "Stereo Mix" (see guide above)
2. Or install VB-Audio Virtual Cable: https://vb-audio.com/Cable/

**macOS:**
1. Install BlackHole: `brew install blackhole-2ch`
2. Restart the app
3. Select "BlackHole 2ch" as Speaker/System device

**Linux:**
```bash
pactl load-module module-loopback
```

### Issue 3: "Recording is silent"
**Check:**
1. Verify audio is being captured:
   - Wrong device selected
   - Device is muted
   - Nothing is playing (for system audio)
2. Is audio actually playing through speakers?
3. Try different system audio device from dropdown

### Issue 4: "System audio recording is empty"
**Likely cause:** Wrong device selected

**Solution:**
1. Run `python diagnose_audio.py`
2. Look at the "SYSTEM AUDIO DEVICES" section
3. Try each device listed (top one is usually best)
4. Play YouTube/music and test recording to verify correct device

### Issue 5: "Audio quality is poor"
**Solutions:**
1. Check your Windows sound format:
   - Right-click speaker icon → Sound Settings → Device Properties → Advanced
   - Try 48000 Hz or 44100 Hz
2. Reduce background noise:
   - Get closer to microphone
   - Use noise gate (enabled by default)
3. Enable AI noise reduction:
   - `pip install rnnoise`
   - Restart app

---

## 🎯 Which Device for YouTube/Meetings?

### For Recording YouTube Videos:
Use **System Audio Only**:
- 🎤 Microphone: None (or leave unchecked)
- 🔊 Speaker/System: Select loopback device (Stereo Mix, BlackHole, etc.)

### For Recording Meetings (Zoom, Teams, etc.):
Use **Both Devices**:
- 🎤 Microphone: Your microphone
- 🔊 Speaker/System: Loopback device
- Result: Records your voice + others' voices

### For Recording Voice Memos:
Use **Microphone Only**:
- 🎤 Microphone: Your microphone
- 🔊 Speaker/System: None (or leave unchecked)

---

## 🧪 Verification Checklist

Run through this checklist:

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] System libraries installed (PortAudio)
- [ ] `python diagnose_audio.py` shows devices
- [ ] At least 1 microphone detected
- [ ] At least 1 system audio device detected (for YouTube/meetings)
- [ ] `python test_recording_complete.py` completes successfully
- [ ] Recorded files have audible audio

---

## 📚 Additional Resources

- **Full Audio Setup Guide**: `AUDIO_SETUP.md`
- **Performance Optimization**: `PERFORMANCE_OPTIMIZATION_GUIDE.md`
- **GPU Acceleration**: `GPU_OPTIMIZATION.md`

---

## 💡 Pro Tips

1. **Test before important recordings**: Run `test_recording_complete.py` to verify everything works

2. **Try multiple system audio devices**: The "best" device varies by system
   - App tries to pick the best one
   - If first doesn't work, try others from dropdown

3. **Recording folder**: Default is `~/Video2Text/Recordings/`
   - Change in app: Menu (☰) → Settings → Change Recording Directory

4. **Sample rate issues**: If you get "Could not open microphone" errors
   - Go to Windows Sound Settings → Device Properties → Advanced
   - Change format to 48000 Hz or 44100 Hz

---

## 🆘 Still Having Issues?

If you've tried everything above:

1. Run full diagnostics:
```bash
python diagnose_audio.py > audio_diag.txt 2>&1
python test_devices.py > devices.txt 2>&1
```

2. Check the output files: `audio_diag.txt` and `devices.txt`

3. Look for error messages

4. Check if the "right" device is listed but just not being selected

5. Try manually specifying device index in `quick_record_test2.py`

---

**Last Updated**: 2025-11-17
**Bug Fix Version**: 1.0
