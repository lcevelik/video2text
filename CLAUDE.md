# FonixFlow — Claude Code Guidelines

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
- Version: `app/version.py`
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

## Windows-specific Notes

- Always use `creationflags=subprocess.CREATE_NO_WINDOW` (or `_NO_WIN` dict) for all subprocess calls — ffmpeg must not spawn visible console windows.
- `subprocess.Popen.__init__` is globally monkey-patched in `app/transcriber.py` at import time to enforce this for Whisper's internal calls.
- Python: `py -3.11` (Python 3.11 at `C:\Users\f\AppData\Local\Programs\Python\Python311\`)
