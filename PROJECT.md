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
- [ ] Performance optimization for long audio files (>1hr)

## To Do

- [ ] Add Whisper large-v3 and distilled models (distil-large-v3, distil-medium.en)
- [ ] Implement faster-whisper (CTranslate2) backend as alternative to openai-whisper (5-10x faster)
- [ ] Add WhisperX integration for word-level alignment and speaker diarization
- [ ] Write unit tests for core transcription pipeline (transcriber, audio_extractor, formatters)
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

## Blocked

- [ ] Whisper large-v3 Turbo model support — blocked on openai-whisper adding turbo variant
- [ ] Native Windows installer (NSIS/InnoSetup) — waiting for Windows build stability

## Releases

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

## Deep Code Analysis (2026-05-26)

### Architecture Overview

FonixFlow is a well-structured cross-platform video/audio transcription app built on OpenAI Whisper. The codebase has ~15,000 lines of Python across 50+ source files, with a React web frontend.

**Strengths:**
- Clean separation of concerns (app/gui/transcription/tools layers)
- Robust error handling with multiple fallback strategies (MPS->CPU, kv_cache retry, model reload)
- Smart performance optimizations (model caching, in-memory audio, parallel chunk processing)
- Cross-platform recording with proper backend abstraction (ScreenCaptureKit/WASAPI/SoundDevice)
- Professional release infrastructure (signing, notarization, DMG creation, GCS auto-update)

### Security Concerns

1. **CRITICAL: XOR-based license obfuscation is trivially reversible** (`main_window.py:224`, `dialogs.py:89`). The key `FonixFlow2024VideoTranscription` is hardcoded in source. Anyone with basic Python knowledge can decode licenses.dat. Consider asymmetric signing (RSA/Ed25519) or hardware-bound keys.

2. **Web API CORS allows all origins** (`web/backend/main.py:29`): `allow_origins=["*"]` — should be restricted in production.

3. **No file upload size limits** on the web API (`web/backend/main.py:62`). An attacker could upload massive files to exhaust disk/memory. Add `max_upload_size` middleware.

4. **Temp file cleanup race condition** — multiple temp files are created with `delete=False` and cleaned up manually. In error paths, some temp files may leak. Use `tempfile.TemporaryDirectory()` context managers.

5. **Debug file left in code** (`dialogs.py:267`): `with open("debug_dialog_button_click.txt", "a")` — writes debug info to current directory. Remove for production.

6. **License key logged in plaintext** (`main_window.py:101,237,336`): License keys appear in log files. Mask/redact them.

### Performance Optimizations

1. **Replace openai-whisper with faster-whisper (CTranslate2)**: The single biggest performance win. faster-whisper is 4-8x faster with same accuracy, uses less memory. Could be offered as a backend option alongside the existing one.

2. **Whisper.cpp via pywhispercpp**: For CPU-only users, whisper.cpp is significantly faster than PyTorch whisper on CPU. Good for the "free version" which may not have GPU.

3. **Audio extraction could use ffmpeg streaming** instead of writing entire file to disk first. For large files, pipe directly to Whisper.

4. **ThreadPoolExecutor in enhanced.py** uses default 4 workers. On high-core-count machines, this could be configurable and auto-scaled based on CPU count.

5. **Global model cache has no eviction** (`transcriber.py:76`): Models stay in memory forever. Add LRU eviction or explicit unload when switching models.

6. **Redundant "Transcription completed successfully" log** appears twice (`transcriber.py:529,540`).

### Missing Tests

- No unit tests for the core transcription pipeline (Transcriber, AudioExtractor)
- No unit tests for language detection heuristics
- No unit tests for SRT/VTT formatters
- No unit tests for settings manager serialization
- No unit tests for update manager (manifest parsing, version comparison)
- Existing tests in test/ are integration/manual tests (test_devices.py, test_recording_complete.py, test_languages.py, test_wasapi_standalone.py) — not automated
- No pytest configuration or test runner setup
- No mocking of Whisper/audio dependencies for fast test execution

### Missing Documentation

- No API documentation for the web backend (FastAPI auto-docs exist at /docs but no custom docs)
- No developer setup guide (virtual environment, ffmpeg installation, whisper model download)
- No architecture diagram
- No contribution guidelines (CONTRIBUTING.md)
- No CHANGELOG maintenance (existing changelogs are manually created, not automated)

### Code Quality Issues

1. **Duplicate code**: `STOPWORDS` and `DIACRITICS` dicts are defined in both `enhanced.py:_get_language_heuristics()` and `language_detection.py`. Single source of truth needed.

2. **Duplicate code**: `LANGUAGE_NAMES` dict defined in both `enhanced.py` and `language_detection.py`. Should be imported from one location.

3. **sys.stderr monkey-patching** (`transcriber.py:57-64`): Patching subprocess.Popen globally is fragile. Consider using Whisper's Python API directly or a proper progress callback.

4. **Import inside functions**: Many heavy imports happen inside methods (torch, librosa, soundfile). While this speeds up startup, it makes dependencies harder to track and can cause confusing errors.

5. **dialogs.py has two separate class definitions merged** — LicenseKeyDialog and the main dialogs module are in the same file without clear separation. Split into separate files.

6. **workers.py contains two separate worker classes plus a duplicate class definition** at the top that seems to be an old version left in.

7. **No type hints** in many public methods (main_window.py is 2550 lines with minimal type annotations).

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
