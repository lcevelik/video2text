# Video2Text Virtual Environment & Build Instructions

## 1. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2. Install All Dependencies
```powershell
pip install -r requirements.txt
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```

## 3. Ensure All Assets Are Present
- ffmpeg.exe in project root
- _internal/whisper/assets/mel_filters.npz
- _internal/whisper/assets/multilingual.tiktoken (copy from venv/Lib/site-packages/whisper/assets if needed)

## 4. Build with PyInstaller
```powershell
.\venv\Scripts\pyinstaller --onedir --name fonixflow --add-data "ffmpeg.exe;." --add-data "gui;gui" --add-data "transcription;transcription" --add-data "requirements.txt;." --add-data "_internal\whisper\assets\mel_filters.npz;_internal\whisper\assets" --add-data "_internal\whisper\assets\multilingual.tiktoken;_internal\whisper\assets" --add-data ".\venv\Lib\site-packages\PySide6\plugins;PySide6\plugins" --hidden-import PySide6 --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets --hidden-import PySide6.QtNetwork --hidden-import PySide6.QtMultimedia --hidden-import PySide6.QtMultimediaWidgets --hidden-import PySide6.QtPrintSupport --hidden-import PySide6.QtQml --hidden-import PySide6.QtQuick --hidden-import PySide6.QtQuickControls2 --hidden-import PySide6.QtSvg --hidden-import PySide6.QtSql --hidden-import PySide6.QtTest --hidden-import PySide6.QtWebEngineCore --hidden-import PySide6.QtWebEngineWidgets --hidden-import PySide6.QtWebChannel --hidden-import PySide6.QtWebSockets --hidden-import pydub --hidden-import whisper --hidden-import sounddevice --hidden-import comtypes gui_qt.py --noconfirm
```

## 5. Post-Build Steps
- Copy any missing assets (mel_filters.npz, multilingual.tiktoken) to the output directory if needed.
- Test the executable in `dist\gui_qt`.

---
Refer to PACKAGING_CHECKLIST.md for a full list of files and dependencies.