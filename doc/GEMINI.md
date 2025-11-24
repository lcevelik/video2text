# FonixFlow - Video Transcription GUI

FonixFlow is a modern, cross-platform video and audio transcription application featuring a polished Qt-based interface. It leverages OpenAI's Whisper model to provide high-accuracy, multi-language transcription with support for simultaneous system audio and microphone recording.

## Project Structure

*   **`app/`**: Contains the main entry point and core application logic.
    *   `fonixflow_qt.py`: Main launcher for the Qt application.
    *   `transcriber.py`: Handles the interaction with the Whisper model.
    *   `audio_extractor.py`: Utilities for audio extraction.
*   **`gui/`**: Implements the graphical user interface using PySide6.
    *   `main_window.py`: The main application window.
    *   `widgets.py`: Custom UI widgets.
    *   `workers.py`: Background workers for threading (transcription, recording).
    *   `dialogs.py`: Dialog windows (e.g., settings, recording setup).
*   **`i18n/`**: Localization files (`.ts` and `.qm`) for multi-language support.
*   **`scripts/`**: Utility scripts for building, translation management, and maintenance.
*   **`assets/`**: Icons, logos, and model files.
*   **`doc/`**: Documentation files.

## Key Features

*   **Transcription:** Uses OpenAI's Whisper model (local execution) for accurate speech-to-text.
*   **Multi-Language:** Supports transcribing and translating multiple languages.
*   **Recording:** Simultaneous capture of microphone and system audio (loopback).
*   **UI:** Ultra-minimal, theme-aware (Dark/Light/Auto) Qt interface.
*   **Cross-Platform:** Runs on Windows, macOS, and Linux.

## Setup & Building

### Dependencies

The project relies on Python and several key libraries:

*   `PySide6`: For the GUI.
*   `openai-whisper`: For transcription.
*   `torch`: Machine learning backend.
*   `ffmpeg-python`: Audio processing.
*   `sounddevice`: Audio recording.

Install dependencies via:
```bash
pip install -r requirements.txt
```

### Running the Application

To launch the Qt GUI:

```bash
python app/fonixflow_qt.py
```

### Build Commands

Platform-specific build scripts are provided in the root directory:

*   **macOS:** `./build_macos.sh`
*   **Windows:** `build_windows.bat`
*   **Standalone:** `./build_standalone.sh`

## Translation Workflow

The project uses Qt's translation system (`.ts` and `.qm` files).

1.  **Extract Strings:** Use `scripts/update_translations.py` to update `.ts` files from source.
2.  **Audit:** Run `scripts/audit_all_translations.py` to check for missing or obsolete strings.
3.  **Compile:** Use `scripts/compile_translations.py` (or `lrelease`) to generate `.qm` files for the app.

## Development

*   **Framework:** PySide6 (Qt for Python).
*   **Entry Point:** `app/fonixflow_qt.py`.
*   **Logging:** Configured in `app/fonixflow_qt.py` and other modules.
