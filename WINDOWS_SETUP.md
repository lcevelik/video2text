# Windows Setup Guide

## Quick Installation Steps for Windows

### Step 1: Install Python

**Option 1: Using winget (Recommended - Fastest)**
```powershell
winget install Python.Python.3.11
```

**Option 2: Using Microsoft Store**
1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Click "Install"

**Option 3: Manual Download**
1. Go to https://www.python.org/downloads/
2. Download the latest Python 3.11 or 3.12 (Windows installer)
3. **IMPORTANT**: During installation, check the box "Add Python to PATH"
4. Click "Install Now"

**Verify Python Installation:**
Close and reopen PowerShell, then run:
```powershell
python --version
```

If you see an error, try:
```powershell
py --version
```

### Step 2: Install ffmpeg

**Option 1: Using winget (Recommended)**
```powershell
winget install ffmpeg
```

**Option 2: Using Chocolatey**
```powershell
choco install ffmpeg
```

**Option 3: Manual Installation**
1. Download from https://www.gyan.dev/ffmpeg/builds/
2. Extract the zip file to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add `C:\ffmpeg\bin`
   - Click "OK" on all dialogs
4. Close and reopen PowerShell

**Verify ffmpeg Installation:**
```powershell
ffmpeg -version
```

### Step 3: Install Python Dependencies

Navigate to the project folder in PowerShell:
```powershell
cd C:\Users\YourUsername\Desktop\video2text
```

**Choose which GUI you want to use:**

**Option 1: Qt GUI (Recommended - Modern Interface)**
Installs all dependencies including PySide6 for the modern Qt interface:
```powershell
python -m pip install -r requirements.txt
```

**Option 2: Enhanced Tkinter GUI**
Same command, includes all dependencies:
```powershell
python -m pip install -r requirements.txt
```

**Option 3: Original GUI (Minimal)**
Install only core dependencies:
```powershell
python -m pip install openai-whisper torch torchaudio ffmpeg-python
```

**If only `py` works instead of `python`:**
```powershell
py -m pip install -r requirements.txt
```

**If you get permission errors, use:**
```powershell
python -m pip install --user -r requirements.txt
```

**For Qt GUI specifically (if installing separately):**
```powershell
python -m pip install PySide6>=6.6.0
```

### Step 4: Verify Installation

Test if everything is working:
```powershell
python test_whisper.py
```

Or if using `py`:
```powershell
py test_whisper.py
```

### Step 5: Run the Application

**Qt GUI (Recommended - Modern Interface):**
```powershell
python gui_qt.py
```

On first run of a multi-language file you will see a dialog:
1. Choose Single vs Multi-language.  
2. (If Multi) Tick expected languages (e.g. English + Czech).  
3. Transcription begins with fast heuristic segmentation; fallback chunk pass runs only if needed.

Performance overlay displays progress, elapsed time, ETA, and final RTF (real-time factor). Use the Cancel button to abort long runs (partial result preserved).

**Enhanced Tkinter GUI:**
```powershell
run_enhanced.bat
```
Or manually:
```powershell
python main_enhanced.py
```

**Original GUI:**
```powershell
python main.py
```

**If `python` doesn't work, use `py` instead:**
```powershell
py gui_qt.py
# or
py main_enhanced.py
# or
py main.py
```

## Troubleshooting

### "python is not recognized"

**Solution 1:** Reinstall Python and make sure to check "Add Python to PATH"

**Solution 2:** Use the Python launcher:
```powershell
py -m pip install -r requirements.txt
```

**Solution 3:** Find Python manually:
1. Python is usually installed at: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3XX\`
2. Add this folder to your PATH (see ffmpeg instructions above)

### "pip is not recognized"

Use Python's module syntax instead:
```powershell
python -m pip install -r requirements.txt
```

### "ffmpeg is not recognized"

1. Make sure ffmpeg is installed
2. Add ffmpeg to your PATH (see Step 2, Option 3)
3. Close and reopen PowerShell
4. Verify with: `ffmpeg -version`

### Still having issues?

1. Make sure you've closed and reopened PowerShell after installing Python/ffmpeg
2. Try restarting your computer
3. Check that both Python and ffmpeg are in your PATH:
   ```powershell
   $env:Path -split ';' | Select-String -Pattern 'python|ffmpeg'
   ```

### Multi-Language Troubleshooting (Qt)

| Issue | Possible Cause | Fix |
|-------|----------------|-----|
| Only one language detected | Heuristic collapsed; fallback not triggered | Re-run ensuring Multi-language selected; verify allow-list includes both languages |
| English segments missing | Allow-list excludes 'en' | Re-open file; choose Multi-language and tick English |
| Slow transcription | Large model + fallback chunk pass | Accept trade-off or switch to Single mode if file is monolingual |
| Cancel not working | Transcription near completion | Wait for finalization or force close (log still preserved) |

