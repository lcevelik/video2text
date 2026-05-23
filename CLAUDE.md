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
| Recording | `gui/recording/wasapi_loopback.py` | WASAPI loopback speaker audio capture |

## User Data Directory

All user data lives in `~/.fonixflow/` managed by `gui/managers/path_manager.py`:

| Path | Purpose |
|---|---|
| `~/.fonixflow/config.json` | App settings |
| `~/.fonixflow/logs/` | Log files |
| `~/.fonixflow/recordings/` | Default recording output |
| `~/.fonixflow/updates/` | Update cache / downloaded new exe |
| `~/.fonixflow/licenses.dat` | License key file (encoded) |

## License Validation

License key validation happens in **two places** — both must point to `~/.fonixflow/`:

1. `gui/dialogs.py` — `validate_and_save()` — called when user enters key in dialog
2. `gui/main_window.py` — `validate_license_key()` — called on every startup

Both check in this order:
1. `~/.fonixflow/licenses.dat` (XOR+base64 encoded)
2. `~/.fonixflow/licenses.txt` (plaintext fallback)
3. Remote LemonSqueezy API

Encoding key: `FonixFlow2024VideoTranscription`. Use `tools/license_encoder.py` to encode/decode.

Word limit (500 words) is enforced in `gui/main_window.py:2243` based on `self.license_valid`.

## WASAPI Loopback Capture

Speaker audio capture uses Windows Audio Session API (WASAPI) loopback mode via `gui/recording/wasapi_loopback.py`. Key implementation details:

- **COM threading:** `comtypes.CoInitialize()` must be called in `_capture_loop` thread itself (not in `start()`), with matching `CoUninitialize()` in the `finally` block.
- **Silent packets:** WASAPI returns packets with `AUDCLNT_BUFFERFLAGS_SILENT = 0x00000002` set — reading `data_pointer` on these crashes. Always check `if num_frames > 0 and not (flags & AUDCLNT_BUFFERFLAGS_SILENT)` before accessing the buffer.
- **Format:** Typically 32-bit float at system sample rate; 16-bit int also handled (converted to float32).

## Windows-specific Notes

- Always use `creationflags=subprocess.CREATE_NO_WINDOW` (or `_NO_WIN` dict) for all subprocess calls — ffmpeg must not spawn visible console windows.
- `subprocess.Popen.__init__` is globally monkey-patched in `app/transcriber.py` at import time to enforce this for Whisper's internal calls.
- Python: `py -3.11` — Python 3.11 at `C:\Users\f\AppData\Local\Programs\Python\Python311\` has all required packages: torch+CUDA 12.8, whisper, librosa, PySide6, scipy, sounddevice, etc.

## Windows Build

```bash
py -3.11 -m PyInstaller fonixflow_qt_windows.spec
```

Output: `dist/FonixFlow_<version>.exe` (~2.9 GB with torch+CUDA+whisper)

The spec reads version dynamically from `app/version.py` and names the exe `FonixFlow_<version>.exe`.

**Zipping for upload:** PowerShell `Compress-Archive` has a 2GB limit — use Python's zipfile instead:
```python
import zipfile
with zipfile.ZipFile('dist/FonixFlow_1.0.x_windows.zip', 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
    zf.write('dist/FonixFlow_1.0.x.exe', 'FonixFlow_1.0.x.exe')
```

## Release to Google Cloud Storage

GCS bucket: `gs://fonixflow-files/updates/windows/`
Windows manifest URL (what the app fetches): `https://storage.googleapis.com/fonixflow-files/updates/windows/manifest.json`

**gsutil path:** `"/c/Users/f/AppData/Local/Google/Cloud SDK/google-cloud-sdk/bin/gsutil.cmd"`  
Auth check: `gcloud auth list` — if no credentialed accounts, run `gcloud auth login`

**Release steps:**
1. Bump `__version__` and `__build__` in `app/version.py`
2. Build: `py -3.11 -m PyInstaller fonixflow_qt_windows.spec`
3. Zip with Python zipfile (allowZip64=True)
4. Compute SHA256 hash with Python hashlib
5. Upload zip to `gs://fonixflow-files/updates/windows/FonixFlow_<version>_windows.zip`
6. Upload manifest as both `manifest.json` AND `manifest_windows.json`

**Manifest format:**
```json
{
  "latest_version": "1.0.x",
  "platform": "windows",
  "platform_name": "Windows",
  "download_url": "https://storage.googleapis.com/fonixflow-files/updates/windows/FonixFlow_<version>_windows.zip",
  "release_notes": "...",
  "force_update": false,
  "file_hash": "<SHA256 UPPERCASE>",
  "minimum_version": "1.0.0",
  "release_date": "YYYY-MM-DD",
  "file_size_mb": <int>
}
```

**Update check throttle:** stored in `~/.fonixflow/update_config.json`. Reset with `echo '{}' > ~/.fonixflow/update_config.json` to force an immediate check on next launch.

## macOS Build & Release

**Build:**
```bash
./build_macos.sh
```
Output: `dist/FonixFlow.app` and `dist/FonixFlow_<version>_macOS.dmg`

**macOS spec:** `fonixflow_qt.spec` — reads version dynamically from `app/version.py`.

**GCS paths (two separate manifests — app auto-detects arch):**
- Apple Silicon: `gs://fonixflow-files/updates/macos-arm/`
- Intel Mac: `gs://fonixflow-files/updates/macos-intel/`

**Release steps:**
1. Bump `__version__` and `__build__` in `app/version.py`
2. Build: `./build_macos.sh`
3. Create zip: `zip -r dist/FonixFlow_<version>_macos.zip dist/FonixFlow.app`
4. Compute SHA256: `shasum -a 256 dist/FonixFlow_<version>_macos.zip`
5. Upload zip to both `gs://fonixflow-files/updates/macos-arm/` and `gs://fonixflow-files/updates/macos-intel/`
6. Upload manifest to both paths as `manifest.json`

**Manifest format (same as Windows, change `platform` field):**
```json
{
  "latest_version": "1.0.x",
  "platform": "macos-arm",
  "platform_name": "macOS (Apple Silicon)",
  "download_url": "https://storage.googleapis.com/fonixflow-files/updates/macos-arm/FonixFlow_<version>_macos.zip",
  "release_notes": "...",
  "force_update": false,
  "file_hash": "<SHA256 lowercase>",
  "minimum_version": "1.0.0",
  "release_date": "YYYY-MM-DD",
  "file_size_mb": <int>
}
```

**Mac update install:** replaces `/Applications/FonixFlow.app` in-place. User must quit and reopen manually after update.
