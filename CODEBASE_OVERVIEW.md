# Video2Text Codebase Overview

## 1. PROJECT PURPOSE

**Video2Text** is a cross-platform desktop application that transcribes audio from video files or audio files directly using **OpenAI's Whisper** model running locally.

### Key Capabilities:
- Transcribes **multiple video formats** (MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V)
- Transcribes **multiple audio formats** (MP3, WAV, M4A, FLAC, OGG, WMA, AAC, OPUS, MP2)
- **GPU acceleration** with CUDA (falls back to CPU automatically)
- **Multi-language support** with code-switching detection (e.g., Czech ↔ English ↔ Czech)
- **Real-time progress tracking** with ETA and RTF (Real-Time Factor) metrics
- **Three GUI options** (Modern Qt, Enhanced Tkinter, Original Lightweight Tkinter)
- **Audio recording** from microphone + system audio
- **Multiple output formats** (TXT, SRT, VTT subtitles)
- **Performance optimized** - v3.2.0 provides 5-10x faster multi-language transcription

---

## 2. KEY FILES AND THEIR ROLES

### Core Transcription Engine
| File | Purpose |
|------|---------|
| `transcriber.py` | Base Whisper transcription module with device detection, model loading, and transcription with GPU/CPU support |
| `transcriber_enhanced.py` | Extended version with multi-language detection, segment analysis, language timeline generation |
| `audio_extractor.py` | Audio extraction from video files and conversion to Whisper-optimal format (16kHz mono WAV) using ffmpeg |

### GUI Applications (Choose One)
| File | Type | Features | Entry Point |
|------|------|----------|------------|
| `gui_qt.py` | **Qt (Recommended)** | Modern, minimal sidebar interface, auto-theme, drag-drop | `python gui_qt.py` |
| `gui_enhanced.py` | Tkinter Enhanced | Advanced features, dual-mode (Basic/Advanced), all controls | via `main_enhanced.py` |
| `gui.py` | Tkinter Original | Simple, lightweight, all core features | via `main.py` |

### Entry Points
| File | Type | Usage |
|------|------|-------|
| `main.py` | Original GUI entry | `python main.py` - Lightweight Tkinter GUI |
| `main_enhanced.py` | Enhanced entry | `./run_enhanced.sh` or `run_enhanced.bat` - Feature-rich Tkinter |
| `gui_qt.py` | Qt entry | `python gui_qt.py` - Modern Qt interface (recommended) |

### Utilities & Testing
| File | Purpose |
|------|---------|
| `test_whisper.py` | Installation verification - tests imports, GPU availability, model loading |
| `test_performance_optimizations.py` | Comprehensive performance testing of multi-language optimizations |
| `check_gpu.py` | GPU diagnostic tool - checks PyTorch, CUDA, nvidia-smi |
| `build_standalone.py` | PyInstaller wrapper for standalone executables |
| `bundle_model.py` | Offline model bundling for distribution |
| `transcriber_diagnostics_addon.py` | Diagnostic utilities (JSON export, detailed logging) |
| `test_progress_bar.py` | Progress bar UI testing |

### Configuration Files
| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies (Whisper, PyTorch, ffmpeg-python, PySide6, sounddevice, etc.) |
| `.gitignore` | Standard Python project gitignore (excludes __pycache__, venv, logs, .txt output files) |

### Documentation
| File | Content |
|------|---------|
| `README.md` | Main documentation - all three GUIs, installation, usage, troubleshooting |
| `README_QT.md` | Qt GUI specific documentation and features |
| `README_ENHANCED.md` | Enhanced GUI documentation |
| `WINDOWS_SETUP.md` | Detailed Windows installation instructions |
| `IMPLEMENTATION_SUMMARY.md` | Feature implementation details (dual-mode, auto-selection, multi-lang, etc.) |
| `CHANGELOG.md` | Version history, v3.2.0 performance optimizations, v3.1.0 multi-language features |

---

## 3. TRANSCRIPTION WORKFLOW

### Simplified Workflow
```
User Input (File/Recording)
    ↓
Audio Extraction (AudioExtractor)
    ↓
Load Whisper Model (Transcriber)
    ↓
Transcribe Audio (with/without multi-language)
    ↓
Format Output (TXT/SRT/VTT)
    ↓
Save to Disk
```

### Detailed Entry Points

#### **Qt GUI Workflow** (`gui_qt.py`)
1. **Record Tab**: Start → Record mic+speaker → Auto-transcribe
2. **Upload Tab**: Drag-drop file → Auto-load → Multi-language dialog → Transcribe
3. **Transcript Tab**: View results, language timeline, save output

Key classes:
- `TranscriptionWorker` (QThread) - Background transcription
- `RecordingWorker` (QThread) - Background recording
- `TranscriptionAppQt` (QMainWindow) - Main UI

#### **Transcriber.transcribe()** - Core Method
**Location**: `transcriber.py`, line 113

```python
def transcribe(self, audio_path, language=None, initial_prompt=None, 
               progress_callback=None, word_timestamps=False)
```

**Steps**:
1. Validate audio file exists
2. Load model if not already loaded (first time only)
3. Call `whisper.model.transcribe()` with parameters:
   - `language`: ISO 639-1 code (auto-detect if None)
   - `verbose`: False (suppress output)
   - `fp16`: True on GPU (faster)
   - `word_timestamps`: Include word-level timing
   - `initial_prompt`: Optional context/speaker names
4. Return result dict with: `text`, `segments`, `language`

**Performance Tracking**:
- `SPEED_FACTORS`: RTF (real-time factors) for each model/device combo
- `estimate_transcription_time()`: Predicts duration before transcription
- Model load time estimates included

#### **EnhancedTranscriber.transcribe_multilang()** - Multi-Language Version
**Location**: `transcriber_enhanced.py`, line 69

**v3.2.0 Optimized Pipeline** (5-10x faster):
1. **Initial Transcription** - Single pass with word timestamps
2. **Heuristic Language Detection** - Text-based segmentation (NO re-transcription)
   - Uses diacritics + stopword scoring in 4s windows
   - No extra audio passes
3. **Fallback Chunk Analysis** (if heuristic collapses to single language)
   - Re-transcribes 4-second chunks only
   - Detects late-arriving languages
   - Respects allowed-language list
4. **Segment Merging** - Consolidates consecutive same-language segments
5. **Language Timeline** - Generates `[00:00:00 - 00:00:05] Language: Czech`
6. **Cancellation** - Partial results preserved if user aborts

#### **AudioExtractor.extract_audio()** - Audio Processing
**Location**: `audio_extractor.py`, line 146

**Key Operations**:
1. Check file format (video or audio)
2. Generate temp output path if not specified
3. Run ffmpeg command:
   ```bash
   ffmpeg -i input -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav
   ```
4. Parameters explained:
   - `-vn`: No video (strip video from video files)
   - `-acodec pcm_s16le`: PCM 16-bit little-endian (optimal for Whisper)
   - `-ar 16000`: 16 kHz sample rate (Whisper standard)
   - `-ac 1`: Mono (single channel)
   - `-y`: Overwrite if exists
5. Return path to processed audio

**Progress Callbacks**:
- 5% - Starting extraction
- 15% - Processing
- 25% - Finalizing
- 30% - Complete

---

## 4. CONFIGURATION FILES & MODELS

### Python Dependencies (`requirements.txt`)
```
openai-whisper>=20231117    # Core transcription engine
torch>=2.0.0                # Deep learning framework
torchaudio>=2.0.0           # Audio processing for PyTorch
ffmpeg-python>=0.2.0        # FFmpeg wrapper (optional - subprocess used)
numpy>=1.24.0               # Numerical computing
tqdm>=4.65.0                # Progress bars
sounddevice>=0.4.6          # Recording: microphone input
scipy>=1.10.0               # Recording: audio processing
pydub>=0.25.1               # Recording: audio manipulation
Pillow>=10.0.0              # Image processing (UI)
TkinterDnD2>=0.3.0          # Drag-drop support for Enhanced/Original GUI
PySide6>=6.6.0              # Qt framework for modern GUI
```

### Whisper Models

**Model Selection Default (v3.2.0)**:
- **Single-language** (English-only): `base` or `base.en`
- **Multi-language**: `large` (best cross-language accuracy)
- **Custom**: User can select tiny, base, small, medium, large

**Model Comparison**:
| Model | Size | Speed (CPU) | Speed (GPU) | Accuracy | Use Case |
|-------|------|------------|-----------|----------|----------|
| tiny | ~39 MB | 10x | 100x | Basic | Quick tests |
| tiny.en | ~39 MB | 10x | 100x | Basic (EN) | English quick |
| base | ~74 MB | 6.7x | 67x | Good | **Default single-lang** |
| base.en | ~74 MB | 6.7x | 67x | Good (EN) | English balanced |
| small | ~244 MB | 3.3x | 33x | Better | Better accuracy |
| small.en | ~244 MB | 3.3x | 33x | Better (EN) | English improved |
| medium | ~769 MB | 1.7x | 11x | High | High accuracy |
| medium.en | ~769 MB | 1.7x | 11x | High (EN) | English high |
| large | ~3 GB | 0.8x | 5.5x | Best | **Multi-language max** |

RTF (Real-Time Factor) = seconds per 1 second of audio
- 100x = 1 minute audio → 0.6 seconds to transcribe

### Application Configuration

**Qt GUI** (`gui_qt.py`):
- Theme: Auto-detect system (Light/Dark/Manual override in ☰ menu)
- Recording directory: Configurable via menu
- Multi-language mode: User dialog (single vs multi, language selection)
- Performance overlay: Shows % | Elapsed | ETA

**Enhanced GUI** (`gui_enhanced.py`):
- Mode persistence: Saves Basic/Advanced choice to `app_config.json`
- Model selection: Auto or manual
- Language: Auto-detect or specific code
- Output format: TXT, SRT, or VTT

**Logging**:
- Default: `transcription.log` in project root
- Enhanced: Optionally in `logs/` directory
- Level: INFO (captures model loads, transcription progress, errors)

---

## 5. DEPENDENCIES & EXTERNAL TOOLS

### Python Packages
- **Core ML**: whisper, torch, torchaudio (required)
- **Audio Processing**: pydub, scipy, sounddevice (recording)
- **GUI**: PySide6 (Qt) or TkinterDnD2 (Tkinter enhanced)
- **Utilities**: numpy, tqdm

### System Requirements
- **ffmpeg** (external binary) - Required for audio extraction/conversion
- **NVIDIA GPU** (optional) - CUDA-capable GPU for 10-100x speedup
- **Python 3.8+** - Language runtime

### GPU Setup
1. Check GPU with `check_gpu.py`
2. If using CPU: No setup needed (slower but works)
3. If CUDA available but not detected:
   ```bash
   # For CUDA 11.8
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # For CUDA 12.1
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

---

## 6. HOW TO RUN THE APPLICATION

### Quick Start (Recommended - Qt GUI)
```bash
# Install dependencies
pip install -r requirements.txt

# Run Qt GUI
python gui_qt.py
```

### All Launchers

**Qt GUI (Modern, Recommended)**:
- Windows: `run_qt.bat`
- Linux/macOS: `./run_qt.sh`
- Direct: `python gui_qt.py`

**Enhanced Tkinter (Feature-Rich)**:
- Windows: `run_enhanced.bat`
- Linux/macOS: `./run_enhanced.sh`
- Direct: `python main_enhanced.py`

**Original Tkinter (Lightweight)**:
- Direct: `python main.py`

### Installation Steps
1. **Install Python 3.8+** (check: `python --version`)
2. **Install FFmpeg**:
   - Windows: `winget install ffmpeg` or download from ffmpeg.org
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. **Install Python packages**: `pip install -r requirements.txt`
4. **Verify**: `python test_whisper.py`
5. **Run**: Choose GUI version above

### First Run
- First use downloads Whisper model (39 MB to 3 GB)
- Subsequent runs cached
- Large model may take 5-10 minutes to download

---

## 7. TESTING & VERIFICATION

### Test Scripts

**`test_whisper.py`** - Installation Check
```bash
python test_whisper.py
```
Verifies:
- Whisper installed
- PyTorch imported
- GPU availability
- Model loading works

**`test_performance_optimizations.py`** - v3.2.0 Optimization Tests
```bash
python test_performance_optimizations.py
```
Tests:
- Module imports
- Text-based language detection
- Segment merging logic
- Performance time predictions

**`test_progress_bar.py`** - UI Component Testing
Tests progress bar display and updates

**`check_gpu.py`** - GPU Diagnostics
```bash
python check_gpu.py
```
Checks:
- PyTorch CUDA support
- NVIDIA GPU detection
- nvidia-smi availability
- GPU memory

### Testing Approach

The codebase uses **static testing** and **unit tests** for verification:

1. **Offline Static Tests** (no Whisper needed):
   - Module import verification
   - Language detection algorithm validation
   - Segment merging logic
   - Performance time calculations

2. **Runtime Tests** (require Whisper):
   - Actual transcription flow
   - Multi-language detection accuracy
   - Performance metrics validation

3. **Integration Points**:
   - GUI startup checks dependencies
   - Test scripts verify each component independently
   - No mocking framework (direct Whisper testing)

### CI/CD Integration
- Could add `pytest` for formal test suite
- Performance benchmark tracking recommended
- Integration tests for GUI interactions

---

## 8. CODEBASE STATISTICS

### File Structure
- **Python Modules**: 15 files (transcriber, audio_extractor, GUIs, utils)
- **Tests**: 4 test scripts
- **Documentation**: 6 markdown files
- **Configuration**: requirements.txt, .gitignore
- **Diagnostics**: 1 directory with JSON exports

### Code Size
- `gui_qt.py`: ~2000 lines (modern Qt interface)
- `gui_enhanced.py`: ~1500 lines (Tkinter advanced)
- `transcriber_enhanced.py`: ~1500 lines (multi-language engine)
- `audio_extractor.py`: ~280 lines (ffmpeg wrapper)
- `transcriber.py`: ~370 lines (core Whisper wrapper)
- Supporting files: ~500 lines total

### Key Metrics (v3.2.0)
- **Performance**: 5-10x faster multi-language transcription
- **Languages**: 99 languages supported
- **Models**: 9 Whisper model variants (tiny → large)
- **Formats**: 8 video + 9 audio formats
- **Output**: 3 output formats (TXT, SRT, VTT)
- **Platforms**: Windows, macOS, Linux

---

## 9. ARCHITECTURE OVERVIEW

### Layer Model
```
┌─────────────────────────────────────────┐
│        GUI Layer (3 Options)            │
│   (Qt / Enhanced Tkinter / Tkinter)     │
├─────────────────────────────────────────┤
│       Application Logic Layer           │
│  (Recording, File I/O, Threading)       │
├─────────────────────────────────────────┤
│    Audio Processing Layer               │
│  (AudioExtractor - ffmpeg wrapper)      │
├─────────────────────────────────────────┤
│   Transcription Layer                   │
│  (Transcriber / EnhancedTranscriber)    │
├─────────────────────────────────────────┤
│    External Dependencies                │
│  (Whisper ML / PyTorch / ffmpeg)        │
└─────────────────────────────────────────┘
```

### Threading Model
- **Qt GUI**: Uses QThread workers for transcription & recording (non-blocking)
- **Enhanced GUI**: Threading for background operations
- **Main Thread**: GUI event loop
- **Worker Threads**: Audio extraction, transcription, recording

### Signal Flow (Qt)
```
User Action (Upload/Record)
    ↓
GUI captures event
    ↓
Create TranscriptionWorker (QThread)
    ↓
Worker: Extract audio + Transcribe
    ↓
Emit signals: progress_update, transcription_complete, error
    ↓
Main thread: Update UI (progress bar, results)
```

---

## 10. RECENT IMPROVEMENTS (v3.2.0 - Nov 2025)

### Performance Optimizations
- **Eliminated redundant chunk re-transcription** (10-20x speedup)
- **Single-pass transcription** with text-based language analysis
- **Reduced sampling** from 3-25 to 3 strategic samples
- **Optimized string processing** (frozensets, set intersections)

### Before/After
```
5-minute multi-language audio:
  v3.1.0: 235 seconds (4 min)
  v3.2.0: 45 seconds (75-80% faster!)

Breakdown:
- Extraction: 10s (same)
- Sampling: 15s → <1s ✓
- Main transcription: 30s → 35s (includes word timestamps)
- Chunk re-transcription: 180s → 0s ✓ ELIMINATED
- Language analysis: <1s ✓
```

### Model Selection Changes
- **Single-language English**: `tiny` → **`base`** (better accuracy)
- **Single-language mixed**: **`base`** (recommended default)
- **Multi-language**: **`large`** (best cross-language accuracy)

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **Purpose** | Transcribe audio/video to text using local Whisper |
| **Main Entry Points** | `gui_qt.py`, `main_enhanced.py`, `main.py` |
| **Core Engine** | `transcriber.py` (Whisper wrapper) + `transcriber_enhanced.py` (multi-lang) |
| **Audio Processing** | `audio_extractor.py` (ffmpeg wrapper) |
| **Key Performance** | 5-10x faster multi-language (v3.2.0) |
| **Supported Formats** | 8 video + 9 audio formats |
| **Languages** | 99 supported languages |
| **Output Formats** | TXT, SRT, VTT |
| **GPU Support** | CUDA (auto-fallback to CPU) |
| **Platforms** | Windows, macOS, Linux |
| **Testing** | Installation, performance optimization, GPU diagnostics tests |
| **Latest Version** | v3.2.0 (2025-11-15) |

