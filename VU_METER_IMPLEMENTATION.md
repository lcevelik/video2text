# VU Meter Implementation

## Overview
Implemented a real-time VU (Volume Unit) meter visualization for audio recording, similar to Zoom's audio level indicator. The VU meters display audio levels using vertical bars with a smooth green-to-red gradient.

## Visual Design
- **Style**: Horizontal bar meter with gradient
- **Colors**: Green → Yellow → Orange → Red (matches Zoom's design)
- **Features**:
  - Peak hold indicator (white line)
  - Scale marks at 10% intervals
  - Real-time updates (10 times per second)
  - Separate meters for microphone and speaker/system audio

## Implementation Details

### 1. VU Meter Widget (`gui/vu_meter.py`)
Already existed in the codebase with full implementation:
- `set_level(level)`: Updates the current level (0.0-1.0)
- Automatic peak detection and decay
- Smooth gradient rendering using Qt's QLinearGradient

### 2. Audio Level Calculation

#### Modified Files:
1. **`gui/recording/base.py`**
   - Added `mic_level` and `speaker_level` attributes to base backend class
   - Added `get_audio_levels()` method to retrieve current levels

2. **`gui/recording/sounddevice_backend.py`**
   - Mic callback (line 153-163): Calculate RMS of microphone input
   - Speaker callback (line 312-329): Calculate RMS of system audio
   - WASAPI callback (line 443-464): Calculate RMS for Windows loopback

3. **`gui/recording/screencapturekit_backend.py`**
   - Mic callback (line 344-354): Calculate RMS of microphone input
   - AudioCaptureDelegate (line 244-247): Calculate RMS of macOS system audio
   - Override `get_audio_levels()` to read from delegate (line 574-582)

4. **`gui/workers.py`**
   - Added `audio_level` signal (line 38)
   - Recording loop now polls backend for levels and emits signal (lines 128-133)

#### RMS Calculation
```python
# Calculate Root Mean Square (RMS) of audio chunk
rms = np.sqrt(np.mean(audio_data**2))

# Normalize to 0-1 range (assuming max RMS of ~0.3 for typical speech)
level = min(1.0, rms / 0.3)
```

### 3. Signal Flow
1. **Audio Backend** (10Hz callbacks) → Calculate RMS → Store in `mic_level`/`speaker_level`
2. **RecordingWorker** (10Hz polling) → Call `backend.get_audio_levels()` → Emit `audio_level` signal
3. **RecordingDialog** (Qt slot) → Receive signal → Call `vu_meter.set_level()`
4. **VU Meter Widget** → Render gradient bar

## Testing

### Visual Test
Run the test script to see the VU meter in action:
```bash
python test_vu_meter.py
```

This will open a window with two VU meters showing simulated audio levels with different patterns.

### Integration Test
1. Launch the application: `python gui_qt.py`
2. Click "🎤 Audio Recording"
3. Click "🔴 Start Recording"
4. The VU meters should appear and show real-time audio levels
5. Speak into the microphone - mic meter should respond
6. Play audio on your system - speaker meter should respond

## Color Ranges
- **Green** (0-60%): Safe audio level
- **Yellow** (60-85%): Moderate level
- **Orange** (85-95%): Approaching maximum
- **Red** (95-100%): Peak/clipping warning

## Performance
- **Update Rate**: 10 times per second (100ms interval)
- **CPU Impact**: Minimal (simple RMS calculation on already-captured audio chunks)
- **Memory**: Negligible (only stores two float values per backend)

## Future Enhancements
Possible improvements:
1. Add vertical bar style (like traditional VU meters)
2. Configurable color thresholds
3. dB scale instead of linear
4. Stereo visualization (separate left/right channels)
5. Frequency spectrum analyzer
