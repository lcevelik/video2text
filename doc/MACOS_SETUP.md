
# macOS Setup Guide - Native System Audio

This guide shows you how to set up **native system audio recording** on macOS using Apple's ScreenCaptureKit framework - **no third-party software required**!

## Quick Start

### Option 1: Native System Audio (Recommended - No BlackHole!)

Use Apple's built-in ScreenCaptureKit for native system audio capture.

**Requirements**:
- macOS 12.3+ (Monterey or later)
- Python 3.8+
- PyObjC framework

**Installation**:
```bash
# Install PyObjC frameworks for ScreenCaptureKit
pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation pyobjc-framework-Cocoa

# Run the application
python app/fonixflow_qt.py
## 🔑 License System

FonixFlow supports both offline and online license validation:

- Add your license key to `licenses.txt` for offline use
- If not found locally, the app checks LemonSqueezy API
```

**First-Time Setup**:
1. When you start recording for the first time, macOS will ask for **Screen Recording** permission
2. Click "Open System Settings"
3. Enable "Screen Recording" permission for your terminal or Python
4. Restart the application

That's it! The app will now capture:
- ✅ Microphone audio (your voice)
- ✅ System audio (all sounds from your Mac) - **natively, no BlackHole needed!**

### Option 2: BlackHole (Fallback)

If you can't install PyObjC or prefer not to grant screen recording permission, you can use BlackHole.

**Installation**:
```bash
# Install BlackHole
brew install blackhole-2ch

# Configure Multi-Output Device (one-time setup)
# 1. Open "Audio MIDI Setup" (in /Applications/Utilities/)
# 2. Click "+" → "Create Multi-Output Device"
# 3. Check both "Built-in Output" and "BlackHole 2ch"
# 4. Set as your default output in System Settings

# Run the application
python gui_qt.py
```

## Comparison

| Feature | ScreenCaptureKit (Native) | BlackHole |
|---------|---------------------------|-----------|
| System audio | ✅ Native | ✅ Via virtual device |
| Installation | `pip install` only | Requires BlackHole + setup |
| Permissions | Screen recording | Microphone only |
| System changes | None | Changes audio routing |
| Quality | Excellent (48kHz stereo) | Excellent (configurable) |
| Stability | Excellent | Excellent |
| macOS version | 12.3+ required | Works on older macOS |

## Permissions

### Screen Recording Permission (ScreenCaptureKit)

ScreenCaptureKit requires "Screen Recording" permission to capture system audio. This is an Apple security requirement.

**Why is this needed?**
- Apple considers system audio capture sensitive (like screen recording)
- This permission allows the app to capture all audio playing on your Mac
- The app **does not** capture video or screenshots

**To grant permission**:
1. System Settings → Privacy & Security → Screen Recording
2. Enable permission for Terminal (or your Python launcher)
3. Restart the application

**What gets captured?**:
- ✅ All system sounds (music, videos, notifications, etc.)
- ✅ Audio from other applications
- ❌ **Not** captured: Screen content, screenshots, or video

## Troubleshooting

### "ScreenCaptureKit not available"

**Cause**: PyObjC frameworks not installed

**Solution**:
```bash
pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation pyobjc-framework-Cocoa
```

### "Screen recording permission denied"

**Cause**: Permission not granted

**Solution**:
1. System Settings → Privacy & Security → Screen Recording
2. Enable for your terminal/Python
3. Restart the application

### "Only microphone is captured, no system audio"

**Possible causes**:
1. Permission not granted → Check Screen Recording permission
2. No audio playing → Try playing music during recording
3. Stream didn't start → Check logs for errors

**Debug**:
```bash
# Run with verbose logging
python gui_qt.py 2>&1 | grep -i "screencapturekit"
```

### "Application falls back to SoundDevice backend"

**Cause**: ScreenCaptureKit not available (PyObjC not installed or macOS < 12.3)

**Solutions**:
- **Preferred**: Install PyObjC (see "Option 1" above)
- **Alternative**: Install BlackHole (see "Option 2" above)
- **Mic-only**: Continue without system audio (mic will still work)

## Technical Details

### How ScreenCaptureKit Works

1. **Microphone**: Captured via `sounddevice` (standard audio input)
2. **System Audio**: Captured via Apple's ScreenCaptureKit framework
   - Creates an `SCStream` with audio-only configuration
   - Receives audio via `CMSampleBuffer` callbacks
   - Processes Float32 PCM audio at 48kHz
3. **Mixing**: Both streams are synchronized and mixed in real-time

### Audio Processing Pipeline

```
Microphone (sounddevice)  ─┐
                           ├─→ Resample → Mix → Normalize → Export MP3
System Audio (SCKit)      ─┘
```

### Architecture

```
RecordingWorker
├── Auto-selects: ScreenCaptureKitBackend (macOS 12.3+)
│   ├── Microphone: sounddevice
│   └── System audio: ScreenCaptureKit (native!)
│
└── Fallback: SoundDeviceBackend (macOS < 12.3 or PyObjC not installed)
    ├── Microphone: sounddevice
    └── System audio: BlackHole (requires installation)
```

## Verifying Installation

Check if ScreenCaptureKit is available:

```bash
python3 -c "
try:
    import ScreenCaptureKit
    print('✅ ScreenCaptureKit available')
except ImportError:
    print('❌ ScreenCaptureKit NOT available')
    print('   Install with: pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation pyobjc-framework-Cocoa')
"
```

Check macOS version:
```bash
sw_vers
# You need macOS 12.3 (Monterey) or later
```

## Benefits of ScreenCaptureKit

✅ **No third-party software** - Uses Apple's built-in framework
✅ **No audio routing changes** - Your system audio setup remains unchanged
✅ **High quality** - Native 48kHz stereo capture
✅ **Reliable** - Official Apple API
✅ **Easy uninstall** - Just remove PyObjC packages
✅ **Secure** - Controlled by macOS permissions system

## Support

- **macOS 12.3+**: ScreenCaptureKit (recommended)
- **macOS < 12.3**: BlackHole (fallback)
- **Windows**: WASAPI loopback (built-in)
- **Linux**: PulseAudio monitors (built-in)

## FAQ

**Q: Do I need to install BlackHole?**
A: No! With PyObjC and macOS 12.3+, ScreenCaptureKit provides native system audio.

**Q: Will this work on macOS 11 (Big Sur)?**
A: No, ScreenCaptureKit requires macOS 12.3+. Use BlackHole for older versions.

**Q: Why does it need screen recording permission?**
A: This is an Apple requirement for capturing system audio. The app does NOT record your screen.

**Q: Can I use this without screen recording permission?**
A: Yes, but you'll only get microphone audio. Install BlackHole for system audio without permission.

**Q: Is my screen content being recorded?**
A: No! The app only captures audio, not video or screenshots.

**Q: How do I uninstall?**
A: Simply remove PyObjC packages:
```bash
pip uninstall pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation pyobjc-framework-Cocoa
```

---

**Recommendation**: Use ScreenCaptureKit (Option 1) for the best experience! It's the cleanest, most reliable solution for macOS users.
**Latest update:**
- Rebranded to FonixFlow
- UI improvements: logo in top bar, auto-jump to transcript tab
