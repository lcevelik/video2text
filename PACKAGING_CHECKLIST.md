# FonixFlow Packaging & Build Checklist

This document lists all files, assets, dependencies, and steps required to package and build the FonixFlow app as a fully self-contained executable.

## 1. Required Python Files & Directories
- gui_qt.py
- audio_extractor.py
- transcriber.py
- gui/ (entire directory)
- transcription/ (entire directory)
- _internal/whisper/assets/mel_filters.npz
- requirements.txt

## 2. Required Assets
- ffmpeg.exe
- _internal/whisper/assets/mel_filters.npz
- venv/Lib/site-packages/whisper/assets/multilingual.tiktoken

## 3. Required Python Packages (add to requirements.txt)
- PySide6
- torch
- torchvision
- torchaudio
- pydub
- sounddevice
- openai-whisper
- comtypes
- scipy (recommended for resampling)

## 4. Packaging Steps
1. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install all dependencies:
   ```powershell
   pip install -r requirements.txt
   pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
   pip install openai-whisper
   pip install comtypes
   pip install scipy
   ```
3. Ensure all assets are present:
   - Place ffmpeg.exe in the project root.
   - Place mel_filters.npz in _internal/whisper/assets.
   - Place multilingual.tiktoken in _internal/whisper/assets (copy from venv/Lib/site-packages/whisper/assets if needed).
4. Run PyInstaller with all required options:
   ```powershell
   .\venv\Scripts\pyinstaller --onedir --name fonixflow --add-data "ffmpeg.exe;." --add-data "gui;gui" --add-data "transcription;transcription" --add-data "requirements.txt;." --add-data "_internal\whisper\assets\mel_filters.npz;_internal\whisper\assets" --add-data "_internal\whisper\assets\multilingual.tiktoken;_internal\whisper\assets" --add-data ".\venv\Lib\site-packages\PySide6\plugins;PySide6\plugins" --hidden-import PySide6 --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets --hidden-import PySide6.QtNetwork --hidden-import PySide6.QtMultimedia --hidden-import PySide6.QtMultimediaWidgets --hidden-import PySide6.QtPrintSupport --hidden-import PySide6.QtQml --hidden-import PySide6.QtQuick --hidden-import PySide6.QtQuickControls2 --hidden-import PySide6.QtSvg --hidden-import PySide6.QtSql --hidden-import PySide6.QtTest --hidden-import PySide6.QtWebEngineCore --hidden-import PySide6.QtWebEngineWidgets --hidden-import PySide6.QtWebChannel --hidden-import PySide6.QtWebSockets --hidden-import pydub --hidden-import whisper --hidden-import sounddevice --hidden-import comtypes gui_qt.py --noconfirm
   ```
5. After building, copy any missing assets (mel_filters.npz, multilingual.tiktoken) to the output directory if needed.

## 5. Notes
- If system audio capture is required, enable 'Stereo Mix' in Windows or install a virtual audio cable.
- Always verify all assets are present in the final dist directory before distribution.

---
This checklist should be kept up to date as dependencies or packaging requirements change.