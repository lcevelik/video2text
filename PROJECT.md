# Project: FonixFlow (video2text)

<!-- 
Project Tracker — keep these H2 headings exactly as-is.
The tracker parses them to populate Kanban columns.
Edit the tasks below. Use - [ ] for open, - [x] for done.
-->

## Goals

- [x] Video/audio-to-text transcription using OpenAI Whisper
- [x] Multi-language support with automatic language detection and code-switching
- [x] Cross-platform desktop app (macOS, Windows, Linux) with PySide6/Qt GUI
- [x] Web frontend (React) with FastAPI backend
- [x] Live audio recording (microphone + system audio capture)
- [x] Auto-update system with GCS-hosted manifests
- [x] License management (LemonSqueezy integration, offline validation)
- [x] i18n/translation system for UI localization
- [ ] Real-time streaming transcription (planned)
- [ ] Plugin/extension architecture for custom formatters

## In Progress

- [ ] Linux build parity testing and distribution
- [ ] Enhanced.py split (2143 lines, complex interdependencies) — needs dedicated PR
- [ ] Network blocking in dialogs.py (validate_and_save still sync) — needs async refactor

## To Do

- [ ] Add Whisper large-v3 and distilled models (distil-large-v3, distil-medium.en)
- [ ] Implement faster-whisper (CTranslate2) backend as alternative to openai-whisper (5-10x faster)
- [ ] Add WhisperX integration for word-level alignment and speaker diarization
- [ ] Write integration tests for multi-language detection paths
- [ ] Add CI/CD pipeline (GitHub Actions) for automated testing and releases
- [ ] Add batch transcription mode (process multiple files)
- [ ] Add export to more formats (JSON, TXT, ASS/SSA subtitles, PDF)
- [ ] Implement speaker diarization (who said what)
- [ ] Add audio waveform visualization in transcription view
- [ ] Add search within transcription results
- [ ] Add undo/redo for manual transcript editing
- [ ] Implement chunked upload for web API (large file support)
- [ ] Add Docker container for web backend deployment
- [ ] Add Vosk/Whisper.cpp as lightweight CPU-only alternatives
- [ ] Add progress estimation refinement based on actual GPU benchmarks
- [ ] Implement proper config file validation (JSON Schema)
- [ ] Add telemetry opt-in for usage analytics (anonymized)
- [ ] Add macOS menu bar integration (native menus)

## Done

- [x] Core Whisper transcription engine with GPU detection (CUDA, MPS, CPU)
- [x] Audio extraction from video files (ffmpeg integration, Opus/WAV output)
- [x] PySide6/Qt GUI with dark/light theme support
- [x] Multi-language transcription with two-pass segmentation pipeline
- [x] Language detection using stopword heuristics + diacritics + audio fallback
- [x] In-memory audio processing for faster chunk extraction
- [x] Parallel chunk processing with ThreadPoolExecutor
- [x] ScreenCaptureKit backend for native macOS system audio capture
- [x] WASAPI loopback backend for Windows system audio capture
- [x] SoundDevice backend for cross-platform recording
- [x] Audio filters (noise gate, compressor) for recording quality
- [x] Splash screen with progress bar during startup
- [x] Single-instance lock file mechanism
- [x] System tray integration for background operation
- [x] Auto-update system (GCS manifest, SHA256 verification, platform-specific install)
- [x] License key validation (local encoded file + LemonSqueezy API)
- [x] Free version with limitations dialog
- [x] Centralized logging with rotation (~/.fonixflow/logs/)
- [x] Centralized path management (~/.fonixflow/ directory structure)
- [x] Resource locator for bundled ffmpeg/ffprobe (PyInstaller compatible)
- [x] SRT and VTT subtitle export
- [x] Model caching (global cache prevents reloading)
- [x] MPS fallback to CPU on Apple Silicon compatibility issues
- [x] Background dependency preloading (torch/whisper loads after GUI renders)
- [x] i18n translation system with QTranslator
- [x] Build scripts for macOS (.app/.dmg), Windows (.exe), Linux (binary)
- [x] Code signing and notarization scripts for macOS
- [x] Web API (FastAPI) with file upload transcription endpoint
- [x] React frontend with recording, settings, and transcript views
- [x] License encoder/decoder tool for build-time obfuscation
- [x] v1.1.0 deep audit: 38 issues fixed, main_window.py split (-34%), async network calls, WASAPI disk-flush
- [x] Unit test framework (pytest) with 40 tests for transcriber, version, formatters, language_detection
- [x] pyproject.toml for pip-installability
- [x] Thread safety: shared bools → threading.Event, LRU model cache eviction
- [x] Code consolidation: LANGUAGE_NAMES (3→1), set_icon (2→1), LICENSE_XOR_KEY (4→1)
- [x] Controller pattern: main_window.py split into LicenseController, RecordingController, TranscriptionController
- [x] Async license validation and update checks (no more UI freeze on startup)

## Blocked

- [ ] Whisper large-v3 Turbo model support — blocked on openai-whisper adding turbo variant
- [ ] Native Windows installer (NSIS/InnoSetup) — waiting for Windows build stability

## Releases

- v1.1.0 — 2026-05 — Deep audit fixes (38 issues), main_window.py split, async network, WASAPI disk-flush, 40 tests
- v1.0.3 — 2025-11 — Mac build parity, no-console-window fixes, theme-aware update dialog
- v1.0.0 — 2025-10 — Initial public release with multi-language support

## Notes

- **Architecture**: Monorepo with app/ (core logic), gui/ (PySide6 GUI), transcription/ (language detection & segmentation), tools/ (utilities), web/ (FastAPI + React), scripts/ (build/release)
- **Key dependencies**: openai-whisper, torch, PySide6, sounddevice, librosa, soundfile, pydub, FastAPI
- **License model**: Freemium (FonixFlow Free with limitations, paid license via LemonSqueezy)
- **Model strategy**: Uses openai-whisper (tiny/base/small/medium/large), models cached globally
- **Performance notes**: Two-pass segmentation (base model detection + main model transcription) is the key multi-language optimization. In-memory audio + parallel chunks reduced 33-min processing from ~44min to ~4-7min.
- **Platform backends**: macOS=ScreenCaptureKit, Windows=WASAPI loopback, Linux=SoundDevice+PulseAudio monitor
- **Deep code analysis completed**: 2026-05-26 — see analysis below

---

## Deep Code Analysis (2026-05-26, updated 2026-05-31 for v1.1.0)

### Architecture Overview

FonixFlow is a well-structured cross-platform video/audio transcription app built on OpenAI Whisper. The codebase has ~15,000 lines of Python across 50+ source files, with a React web frontend.

**Strengths:**
- Clean separation of concerns (app/gui/transcription/tools layers)
- Robust error handling with multiple fallback strategies (MPS->CPU, kv_cache retry, model reload)
- Smart performance optimizations (model caching, in-memory audio, parallel chunk processing)
- Cross-platform recording with proper backend abstraction (ScreenCaptureKit/WASAPI/SoundDevice)
- Professional release infrastructure (signing, notarization, DMG creation, GCS auto-update)

### v1.1.0 Fixes Applied (2026-05-31)

**Critical bugs fixed:**
- stderr FD leak in transcriber.py (devnull handle now properly closed)
- QThread.terminate() → cancel()+wait() for transcription worker
- Debug file write removed from dialogs.py
- Wrong widget update (record_progress_label → upload_progress_label)
- Theme mode setting respected (was hardcoded to dark)

**Thread safety:**
- Shared bools (is_running, is_recording, cancel_requested) → threading.Event
- LRU model cache eviction (max 2 models, prevents 9GB+ memory)
- try/except for IndexError on chunk access (race condition)

**Resource leaks:**
- 3x sf.read() → sf.info() (no more loading entire files into memory)
- WASAPI disk-flush (flushes chunks to temp file every 1000, prevents unbounded memory)

**Error handling:**
- 6 bare except: → except Exception:
- All subprocess.run in enhanced.py wrapped with CREATE_NO_WINDOW + 120s timeout
- License key logging masked (first 8 chars only)

**Code health:**
- LANGUAGE_NAMES consolidated (3→1), set_icon (2→1), LICENSE_XOR_KEY (4→1)
- Unused imports removed from dialogs.py
- pyproject.toml added for pip-installability

**Architecture:**
- main_window.py split into 3 controller mixins (-34%, 2558→1689 lines)
- License API validation → async QThread (no UI freeze on startup)
- Update check → async QThread (no UI freeze)

**Tests:**
- pytest framework with 40 unit tests (all passing)
- Tests for transcriber, version, formatters, language_detection, theme_manager

### Remaining Issues (deferred to v1.2.0)

1. **XOR-based license obfuscation is trivially reversible** — consider asymmetric signing
2. **Web API CORS allows all origins** — restrict in production
3. **enhanced.py is 2143 lines** — needs split (complex interdependencies)
4. **dialogs.py validate_and_save still sync** — needs async refactor
5. **No CI/CD pipeline** — add GitHub Actions for automated testing
6. **Duplicate code** — STOPWORDS/DIACRITICS dicts in enhanced.py and language_detection.py

### Recommended New Features

1. **Batch processing**: Process entire folders of video/audio files with a single command
2. **Speaker diarization**: Add pyannote.audio or WhisperX for speaker identification
3. **Live transcription**: Real-time streaming transcription using Whisper's streaming API or faster-whisper's segment callback
4. **Custom vocabulary / prompt templates**: Allow users to specify domain-specific terms that improve accuracy
5. **Transcript editing**: Allow manual correction of transcription with auto-save
6. **Cloud transcription**: Offload to OpenAI Whisper API or Azure Speech for users without GPU
7. **Format export expansion**: JSON (with timestamps + confidence), ASS/SSA subtitles, PDF with formatting
8. **Drag-and-drop from URL**: Transcribe directly from YouTube/URL by downloading first (yt-dlp integration)
9. **Keyboard shortcuts**: Common actions (start/stop recording, export, model selection)
10. **Transcript comparison**: Side-by-side view of two transcription runs with different models

### Model Options & Alternatives

| Model | Speed | Accuracy | Size | Notes |
|-------|-------|----------|------|-------|
| openai-whisper (current) | Baseline | Good | 39MB-3GB | PyTorch, GPU recommended |
| faster-whisper (CTranslate2) | 4-8x faster | Same | Similar | Best drop-in replacement |
| whisper.cpp (pywhispercpp) | 2-4x faster CPU | Same | Similar | Best for CPU-only |
| WhisperX | Similar | Better (with alignment) | Larger | Word-level timestamps + diarization |
| Distil-Whisper | 6x faster | 90% of full | 75% smaller | English-only, good for Free version |
| Vosk | 10x faster | Lower | 50MB | Offline, lightweight, streaming |
| NVIDIA NeMo | 3-5x faster | Comparable | Similar | Best for NVIDIA GPUs |
| OpenAI Whisper API | Network dependent | Best | N/A | Cloud option, costs per minute |
