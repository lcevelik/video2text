# Video2Text - Quick Reference Guide

## File Structure at a Glance

```
video2text/
├── Core Engine
│   ├── transcriber.py              # Whisper wrapper (load model, transcribe)
│   ├── transcriber_enhanced.py     # Multi-language detection & segmentation
│   └── audio_extractor.py          # ffmpeg integration (extract audio)
│
├── GUI (Choose One)
│   ├── gui_qt.py                   # Modern Qt interface (RECOMMENDED)
│   ├── gui_enhanced.py             # Feature-rich Tkinter
│   └── gui.py                      # Lightweight Tkinter
│
├── Entry Points
│   ├── main.py                     # Launch lightweight GUI
│   └── main_enhanced.py            # Launch enhanced GUI
│
├── Testing & Utilities
│   ├── test_whisper.py             # Installation verification
│   ├── test_performance_optimizations.py  # v3.2.0 optimization tests
│   ├── check_gpu.py                # GPU diagnostics
│   ├── build_standalone.py         # PyInstaller wrapper
│   └── bundle_model.py             # Offline model bundling
│
├── Configuration
│   ├── requirements.txt            # Python dependencies
│   └── .gitignore                  # Git ignore patterns
│
└── Documentation
    ├── README.md                   # Main docs (all features)
    ├── README_QT.md               # Qt GUI docs
    ├── README_ENHANCED.md         # Enhanced GUI docs
    ├── WINDOWS_SETUP.md           # Windows installation
    ├── CHANGELOG.md               # Version history
    └── IMPLEMENTATION_SUMMARY.md  # Feature details
```

## Quick Command Reference

### Installation
```bash
pip install -r requirements.txt
```

### Run Application
```bash
# Qt GUI (Recommended)
python gui_qt.py

# Enhanced GUI
python main_enhanced.py

# Lightweight GUI
python main.py
```

### Test Installation
```bash
python test_whisper.py
python check_gpu.py
python test_performance_optimizations.py
```

## Main Classes & Methods

### Transcriber (transcriber.py)
```python
transcriber = Transcriber(model_size='base')
transcriber.load_model()
result = transcriber.transcribe(
    audio_path='audio.wav',
    language='en',  # or None for auto-detect
    progress_callback=update_progress_func
)
# result keys: 'text', 'segments', 'language'
```

### EnhancedTranscriber (transcriber_enhanced.py)
```python
transcriber = EnhancedTranscriber(model_size='large')
result = transcriber.transcribe_multilang(
    audio_path='audio.wav',
    detect_language_changes=True,
    allowed_languages=['en', 'cs']
)
# Additional keys: 'language_segments', 'language_timeline', 'classification'
```

### AudioExtractor (audio_extractor.py)
```python
extractor = AudioExtractor()
audio_path = extractor.extract_audio(
    media_path='video.mp4',
    progress_callback=update_progress_func
)
duration = extractor.get_media_duration('file.mp4')
```

## Key Workflows

### Transcription Pipeline
1. **User loads file** → GUI event handler
2. **Extract audio** → AudioExtractor (ffmpeg)
3. **Load model** → Transcriber.load_model()
4. **Transcribe** → Transcriber.transcribe() or EnhancedTranscriber.transcribe_multilang()
5. **Format & save** → Write TXT/SRT/VTT file

### Multi-Language Detection (v3.2.0 Optimized)
1. **Single transcription pass** with word timestamps
2. **Text-based heuristic** (diacritics + stopwords) - NO re-transcription!
3. **Fallback chunk analysis** (if only 1 language detected)
4. **Segment merging** & timeline generation
5. **Return** with language_timeline & classification

## Model Selection

| Use Case | Model | Speed | Accuracy |
|----------|-------|-------|----------|
| Quick test | `tiny` | 100x (GPU) | Basic |
| English only | `base.en` | 67x (GPU) | Good |
| **Default** | `base` | 67x (GPU) | Good |
| Better accuracy | `small` | 33x (GPU) | Better |
| High quality | `medium` | 11x (GPU) | High |
| Maximum accuracy | `large` | 5.5x (GPU) | Best |

## Configuration Files

### requirements.txt
Lists all Python dependencies (Whisper, PyTorch, PySide6, sounddevice, etc.)

### Logging
- Default: `transcription.log` in project root
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Level: INFO

## Threading Architecture (Qt GUI)

```python
Main Thread (GUI)
    ↓
    ├─→ TranscriptionWorker (QThread)
    │   ├─→ Audio extraction
    │   ├─→ Model loading
    │   └─→ Transcription
    │
    └─→ RecordingWorker (QThread)
        ├─→ Microphone capture
        └─→ System audio capture
```

**Signal-based communication** ensures UI remains responsive.

## Performance Metrics (v3.2.0)

### Speed (Real-Time Factor)
- tiny: 100x (1 min audio = 0.6s)
- base: 67x (1 min audio = 0.9s)
- large: 5.5x (1 min audio = 11s)

### Multi-Language Performance
- 5-minute audio: ~45 seconds (GPU)
- Breakdown:
  - Extraction: 10s
  - Main transcription: 35s
  - Language analysis: <1s

## Supported Formats

### Video (8 formats)
MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V

### Audio (9 formats)
MP3, WAV, M4A, FLAC, OGG, WMA, AAC, OPUS, MP2

### Output (3 formats)
TXT (plain text), SRT (subtitles), VTT (subtitles)

## Language Support
99 languages including:
- English, Spanish, French, German, Italian
- Chinese, Japanese, Korean, Russian, Arabic
- Czech, Polish, Romanian, Greek, Thai, Vietnamese
- And 84 more!

## Error Handling

### Common Issues
| Issue | Solution |
|-------|----------|
| FFmpeg not found | Install ffmpeg (`winget install ffmpeg` or `brew install ffmpeg`) |
| GPU out of memory | Use smaller model (tiny/base) |
| Model download slow | Check internet connection |
| Transcription slow | Enable GPU (`check_gpu.py`), use smaller model |
| Audio quality issues | Check input file format, volume levels |

## Testing Checklist

```
[ ] Run test_whisper.py           # Verify installation
[ ] Run check_gpu.py              # Check GPU availability
[ ] Run test_performance_optimizations.py  # Verify optimizations
[ ] Test GUI startup              # python gui_qt.py
[ ] Test single-language transcription
[ ] Test multi-language transcription
[ ] Test audio recording
[ ] Test output formats (TXT, SRT, VTT)
```

## Version Info

**Current Version**: v3.2.0 (2025-11-15)

**Major Features**:
- Multi-language support (99 languages)
- GPU acceleration with auto-fallback
- Three GUI options (Qt recommended)
- Audio recording (mic + system)
- Performance optimized (5-10x faster multi-lang)
- Real-time progress with ETA

## Quick Links

- **Main docs**: README.md
- **Qt GUI docs**: README_QT.md
- **Enhanced GUI docs**: README_ENHANCED.md
- **Implementation details**: IMPLEMENTATION_SUMMARY.md
- **Full codebase overview**: CODEBASE_OVERVIEW.md

