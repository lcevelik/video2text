# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Karpathy Principles (always apply these)

### 1. Think Before Coding
State assumptions explicitly before writing code. When a request is ambiguous, present interpretations and ask — do not guess and run with it.

### 2. Simplicity First
Write the minimum code that solves exactly the stated problem. No speculative features, no unnecessary abstractions, no unrequested configurability, no error handling for scenarios that cannot happen.

### 3. Surgical Changes
Edit only what the request requires. Preserve existing style, formatting, and comments. Never delete pre-existing code unless explicitly asked — only remove code that YOUR changes made obsolete.

### 4. Goal-Driven Execution
Define success criteria before starting. Convert vague tasks into testable goals (e.g. "add validation" → "write tests for invalid inputs, then make them pass"). Verify completion against those criteria.

---

## Project Overview

**FonixFlow** — a desktop transcription app (PySide6/Qt) that extracts audio from video/audio files and transcribes them using OpenAI Whisper.

- Entry point: `app/fonixflow_qt.py`
- Version: `app/version.py` — bump both `__version__` and `__build__` for every release
- Run (Windows): `py -3.11 -m app.fonixflow_qt`

## Key Architecture

| Layer | Path | Purpose |
|---|---|---|
| GUI | `gui/main_window.py` | Main Qt window |
| Managers | `gui/managers/` | log, path, settings, file, theme |
| Workers | `gui/workers.py` | Background transcription threads |
| Audio | `app/audio_extractor.py` | ffmpeg audio extraction/conversion |
| Transcription | `app/transcriber.py` | Whisper model wrapper |
| Processing | `transcription/audio_processing.py` | Chunking, language sampling |
| Enhanced | `transcription/enhanced.py` | Multi-language transcription |
| Tools | `tools/resource_locator.py` | ffmpeg/ffprobe path resolution |

## User Data Directory

All user data lives in `~/.fonixflow/` managed by `gui/managers/path_manager.py`:

| Path | Purpose |
|---|---|
| `~/.fonixflow/config.json` | App settings |
| `~/.fonixflow/logs/` | Log files |
| `~/.fonixflow/recordings/` | Default recording output |
| `~/.fonixflow/updates/` | Update cache |
| `~/.fonixflow/licenses.dat` | License key file (encoded) |

## License Validation

`gui/dialogs.py` validates license keys in this order:
1. `~/.fonixflow/licenses.dat` (encoded, user-installed)
2. `~/.fonixflow/licenses.txt` (plaintext fallback)
3. Bundled file inside the exe (via `sys._MEIPASS` for frozen builds)
4. Remote API call

Encoding uses XOR + base64 with key `FonixFlow2024VideoTranscription`. Use `tools/license_encoder.py` to encode/decode.

## Windows Build

```bash
py -3.11 -m PyInstaller fonixflow_qt_windows.spec
```

Output: `dist/FonixFlow.exe` (single-file, no console window, ffmpeg bundled)

The spec (`fonixflow_qt_windows.spec`) auto-detects ffmpeg from PATH or common install locations and bundles it. It also bundles `licenses.txt` from the project root for offline key validation.

## Release to Google Cloud Storage

GCS bucket: `gs://fonixflow-files/updates`  
Windows manifest URL: `https://storage.googleapis.com/fonixflow-files/updates/windows/manifest.json`

Release steps (Windows):
1. Bump version in `app/version.py`
2. Build exe: `py -3.11 -m PyInstaller fonixflow_qt_windows.spec`
3. Zip: `dist/FonixFlow_<version>_windows.zip` containing `FonixFlow.exe`
4. Upload zip + manifest to `gs://fonixflow-files/updates/windows/`

Use `scripts/release_to_gcs_multiplatform.sh 1.0.2 windows` (requires `gsutil` from Google Cloud SDK).

## Windows-specific Notes

- Always use `creationflags=subprocess.CREATE_NO_WINDOW` (or `_NO_WIN` dict) for all subprocess calls — ffmpeg must not spawn visible console windows.
- `subprocess.Popen.__init__` is globally monkey-patched in `app/transcriber.py` at import time to enforce this for Whisper's internal calls.
- Python: `py -3.11` (Python 3.11 at `C:\Users\f\AppData\Local\Programs\Python\Python311\`)
