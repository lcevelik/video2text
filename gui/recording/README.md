# Recording Module Architecture

Modular, pluggable audio recording system with platform-specific backends.
**Now with improved modularity and auto-navigation!**

## Architecture Overview

```
gui/recording/
├── __init__.py                    # Public API exports
├── base.py                        # Abstract backend interface
├── audio_processor.py             # Audio utilities (resample, normalize, mix)
├── sounddevice_backend.py         # Cross-platform backend (BlackHole/WASAPI/PulseAudio)
└── screencapturekit_backend.py    # macOS native backend (12.3+)
```
Recent changes:
- Modular refactoring for maintainability
- Auto-jump to transcript tab after recording and transcription

## Backends

**Status**: ✅ Fully implemented and tested (auto-jump to transcript tab after recording)
**Status**: ✅ Fully implemented and tested

**Platform Support**:
- **macOS**: Uses BlackHole 2ch for system audio
- **Windows**: Uses WASAPI loopback
- **Linux**: Uses PulseAudio monitors

**Requirements**:
- `sounddevice` library
- macOS requires BlackHole: https://github.com/ExistentialAudio/BlackHole

### ScreenCaptureKitBackend (macOS Native)
**Status**: 🚧 Partial implementation

**Platform Support**:
- macOS 12.3+ (Monterey or later)

**Requirements**:
- PyObjC framework
- `pyobjc-framework-ScreenCaptureKit`
- `pyobjc-framework-AVFoundation`
- Screen recording permission

**Installation**:
```bash
pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation
```

**Current Limitations**:
- System audio capture not fully implemented (microphone only)
- Needs permission handling
- Needs SCStreamConfiguration setup

**TODO**:
1. Request screen recording permission
2. Configure SCStreamConfiguration for audio-only capture
3. Create SCStream with configuration and delegate
4. Implement proper audio buffer handling

## Usage

### Automatic Backend Selection
```python
from gui.workers import RecordingWorker

# Auto-selects best backend for platform
worker = RecordingWorker(
    output_dir="/path/to/output",
    mic_device=None,  # Auto-detect
    speaker_device=None  # Auto-detect
)
worker.start()
```

### Force Specific Backend
```python
# Force SoundDevice backend
worker = RecordingWorker(
    output_dir="/path/to/output",
    backend="sounddevice"
)

# Force ScreenCaptureKit (macOS 12.3+ only)
worker = RecordingWorker(
    output_dir="/path/to/output",
    backend="screencapturekit"
)
```

### Direct Backend Usage
```python
from gui.recording import SoundDeviceBackend, AudioProcessor

# Create backend
backend = SoundDeviceBackend(mic_device=0, speaker_device=1)

# Start recording
backend.start_recording()

# ... wait ...

# Stop and get results
result = backend.stop_recording()

# Process audio
final_audio = AudioProcessor.mix_audio(
    mic_data=result.mic_data,
    speaker_data=result.speaker_data,
    mic_rate=result.mic_sample_rate,
    speaker_rate=result.speaker_sample_rate,
    target_rate=16000
)

# Normalize
final_audio = AudioProcessor.normalize_audio(final_audio)

# Clean up
backend.cleanup()
```

## Audio Processing Pipeline

1. **Capture** (via backend)
   - Microphone audio (mono, native sample rate)
   - System audio (stereo→mono, native sample rate)

2. **Resampling** (AudioProcessor)
   - Both streams converted to target rate (16kHz default)
   - Uses scipy.signal.resample_poly or linear interpolation fallback

3. **Mixing** (AudioProcessor)
   - Length alignment (zero-padding shorter stream)
   - Average mixing: `(mic + speaker) / 2`

4. **Normalization** (AudioProcessor)
   - Target RMS: 0.12 (~-18.4dB)
   - Soft clipping via tanh
   - Max gain limit: 10x

5. **Safety Limiting** (AudioProcessor)
   - Peak limiting to 0.98 max amplitude

6. **Export** (RecordingWorker)
   - 320kbps MP3 or WAV fallback
   - 16kHz mono

## Benefits of Modular Architecture

### Before Refactoring
- **workers.py**: 689 lines, everything mixed together
- Hard to test individual components
- Difficult to add new backends
- Platform-specific code scattered throughout

### After Refactoring
- **workers.py**: 359 lines (48% reduction)
- **recording/** module: 1055 lines across 5 focused files
- Clear separation of concerns
- Easy to add new backends
- Testable components
- Reusable audio processing utilities

## Adding a New Backend

1. Create new file: `gui/recording/mybackend_backend.py`

2. Implement the `RecordingBackend` interface:
```python
from .base import RecordingBackend, RecordingResult

class MyBackend(RecordingBackend):
    def start_recording(self) -> None:
        # Start capturing audio
        pass

    def stop_recording(self) -> RecordingResult:
        # Stop and return audio data
        pass

    def get_backend_name(self) -> str:
        return "mybackend"
```

3. Export in `__init__.py`:
```python
from .mybackend_backend import MyBackend
__all__.append('MyBackend')
```

4. Add to `RecordingWorker._select_backend()` in `workers.py`

## Testing

Test individual components:
```bash
# Test audio processor
python3 -c "from gui.recording.audio_processor import AudioProcessor; print('OK')"

# Test backends
python3 -c "from gui.recording.sounddevice_backend import SoundDeviceBackend; print('OK')"

# Test full recording (requires actual devices)
python debug_recording.py
```

## Performance

- **Memory**: Streams audio in chunks (no full buffering)
- **CPU**: Efficient numpy operations
- **Latency**: ~100ms polling interval during recording

## Future Enhancements

1. **ScreenCaptureKit**: Complete implementation
2. **PipeWire backend**: Native Linux support
3. **JACK backend**: Pro audio on Linux
4. **Audio filters**: Pre-processing before save (noise reduction, EQ)
5. **Multi-track**: Save mic and speaker as separate tracks
6. **Format options**: FLAC, OGG, etc.
7. **Streaming**: Real-time transcription during recording

## License

Same as parent project.
