# Video to Text Transcription Application

A desktop application that transcribes audio from video files or audio files directly using OpenAI's Whisper model running locally. Supports multiple video and audio formats and provides a user-friendly GUI for easy transcription.

## Features

- 🎥 **Multiple Video Formats**: Supports MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V
- 🎵 **Multiple Audio Formats**: Supports MP3, WAV, M4A, FLAC, OGG, WMA, AAC, OPUS, MP2
- 🎤 **Audio Processing**: Automatically extracts audio from video files or converts audio files to optimal format using ffmpeg
- 🤖 **Whisper Integration**: Uses OpenAI Whisper for high-quality transcription
- 🚀 **GPU Acceleration**: Automatically uses GPU (CUDA) if available, falls back to CPU
- 📊 **Progress Tracking**: Real-time progress updates during transcription
- 💾 **Multiple Output Formats**: Save as plain text (.txt), SRT subtitles (.srt), or VTT subtitles (.vtt)
- 🎛️ **Model Selection**: Choose from different Whisper model sizes (tiny, base, small, medium, large)
- 🎨 **Modern Qt GUI**: Professional sidebar navigation with tabbed interface and dark/light themes
- 🎙️ **Audio Recording**: Record from microphone and system audio simultaneously
- 🌍 **Multi-Language Support**: Auto-detect languages with 99 language support
- 🖥️ **Cross-Platform**: Works on Windows, macOS, and Linux

## GUI Versions

Video2Text offers **three GUI options** to suit your needs:

### 🎨 **Qt GUI** (Recommended - Modern & Professional)
The latest and most advanced interface with:
- ✨ **Sidebar Navigation**: Clean tabs for Upload, Record, and Transcript
- 🌓 **Dark/Light Mode**: Toggle themes for comfortable viewing
- 🎯 **Auto-Transcribe**: Drop files and transcription starts automatically
- 📱 **Basic & Advanced Modes**: Simple for beginners, powerful for experts
- 🎙️ **Integrated Recording**: Record mic + speaker with one click

**How to run:**
```bash
python gui_qt.py
```

**See:** `README_QT.md` for detailed Qt GUI documentation

### 📱 **Enhanced Tkinter GUI** (Feature-Rich)
Advanced features with traditional interface:
- Dual-mode interface (Basic/Advanced)
- Automatic model selection
- Audio recording support
- Multi-language detection

**How to run:**
```bash
./run_enhanced.sh    # Linux/macOS
run_enhanced.bat     # Windows
```

**See:** `README_ENHANCED.md` for detailed documentation

### 📋 **Original GUI** (Lightweight)
Simple, straightforward interface:
- Minimal dependencies (Tkinter built-in)
- All core transcription features
- Smallest footprint

**How to run:**
```bash
python main.py
```

## Requirements

### Core Requirements (All Versions)
- Python 3.8 or higher
- ffmpeg (for audio extraction)
- CUDA-capable GPU (optional, for faster transcription)

### GUI-Specific Requirements
- **Qt GUI**: PySide6 >= 6.6.0 (install via `pip install PySide6`)
- **Enhanced GUI**: sounddevice, scipy, Pillow (for recording features)
- **Original GUI**: Tkinter (usually built-in with Python)

## Installation

### Step 1: Install Python

If you don't have Python installed:

- **Windows**: 
  - **Recommended**: `winget install Python.Python.3.11` (in PowerShell)
  - **Alternative**: Download from [python.org](https://www.python.org/downloads/)
  - **IMPORTANT**: During installation, check "Add Python to PATH"
  - See `WINDOWS_SETUP.md` for detailed Windows instructions
- **macOS**: Download from [python.org](https://www.python.org/downloads/) or use Homebrew: `brew install python3`
- **Linux**: Usually pre-installed. If not: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

Verify installation:
```bash
python --version
# or (on Windows, if python doesn't work)
py --version
# or (on Mac/Linux)
python3 --version
```

**Windows Note**: If `python` doesn't work, try `py` (Python launcher) or `python3`. You can also use `python -m pip` instead of just `pip`.

### Step 2: Install ffmpeg

ffmpeg is required for extracting audio from video files.

#### Windows

**Option 1: Using winget (recommended)**
```bash
winget install ffmpeg
```

**Option 2: Manual Installation**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the zip file
3. Add the `bin` folder to your system PATH
4. Verify: Open Command Prompt and run `ffmpeg -version`

**Option 3: Using Chocolatey**
```bash
choco install ffmpeg
```

#### macOS

**Using Homebrew (recommended)**
```bash
brew install ffmpeg
```

**Using MacPorts**
```bash
sudo port install ffmpeg
```

#### Linux

**Ubuntu/Debian**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Fedora**
```bash
sudo dnf install ffmpeg
```

**Arch Linux**
```bash
sudo pacman -S ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### Step 3: Install Python Dependencies

1. Navigate to the project directory:
```bash
cd video2text
```

2. Install Python packages:

**For Qt GUI (Recommended):**
```bash
# Install all dependencies including PySide6
pip install -r requirements.txt

# Or install PySide6 separately
pip install PySide6>=6.6.0
```

**For Enhanced Tkinter GUI:**
```bash
pip install -r requirements.txt
```

**For Original GUI (Minimal):**
```bash
# Install only core dependencies
pip install openai-whisper torch torchaudio ffmpeg-python
```

**Platform-specific commands:**

**Windows:**
```powershell
python -m pip install -r requirements.txt
# or if python doesn't work:
py -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

**Note for GPU users**: If you have a CUDA-capable GPU and want to use it for faster transcription, you may need to install PyTorch with CUDA support separately:

```bash
# For CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

The application will automatically detect and use GPU if available.

### Step 4: Verify Installation

Test if Whisper is properly installed:

```bash
python test_whisper.py
```

This script will:
- Check if all dependencies are installed
- Verify GPU availability (if applicable)
- Test loading a Whisper model
- Confirm everything is working

## Usage

### Starting the Application

Choose your preferred GUI:

**Qt GUI (Recommended):**
```bash
python gui_qt.py
```

**Enhanced Tkinter GUI:**
```bash
./run_enhanced.sh    # Linux/macOS
run_enhanced.bat     # Windows
```

**Original GUI:**
```bash
python main.py
```

### Using the Qt GUI (Recommended)

The modern Qt interface features a **sidebar with three main tabs**:

#### Basic Mode:
1. **Upload Tab**:
   - Drag & drop your video/audio file (or click to browse)
   - Transcription starts automatically
   - Progress updates in real-time

2. **Record Tab**:
   - Click "Start Recording" to record audio
   - Records both microphone and system audio
   - Configure recording directory in settings
   - Recording automatically loads for transcription

3. **Transcript Tab**:
   - View transcription results
   - Choose output format (TXT, SRT, VTT)
   - Click "Save Transcription" to export
   - Auto-navigates here when transcription completes

#### Advanced Mode:
Same three tabs with additional controls:
- Manual model selection (tiny, base, small, medium, large)
- Language selection (99 languages supported)
- Custom instructions for better accuracy

#### Dark/Light Mode:
- Click the theme toggle button (🌙/☀️) in the header
- Preference is saved automatically

### Using the Enhanced GUI

1. **Select Mode**: Choose Basic Mode (simple) or Advanced Mode (full control)
2. **Select Media File**: Browse or drag-and-drop a video/audio file
3. **Choose Settings** (Advanced Mode):
   - Model size (or use Auto-select)
   - Language (or use Auto-detect)
   - Output format (TXT, SRT, VTT)
4. **Start Transcription**: Click "Transcribe Now" or "Start Transcription"
5. **Review Results**: Transcription appears in the text area
6. **Save**: Click "Save Transcription"

### Using the Original GUI

1. **Select Media File**: Click "Browse..." to select a video or audio file
2. **Choose Model Size**: Select a Whisper model from the dropdown
3. **Select Output Format**: Choose between plain text (.txt) or SRT subtitles (.srt)
4. **Start Transcription**: Click "Start Transcription"
5. **Wait for Completion**: The progress bar will show the current status
6. **Review Results**: The transcription will appear in the text area
7. **Save Transcription**: Click "Save Transcription" to export to a file

### First Run

The first time you use a Whisper model, it will be automatically downloaded. This may take several minutes depending on:
- Your internet connection speed
- The model size you selected (larger models take longer to download)
- Model sizes range from ~39 MB (tiny) to ~3 GB (large)

Models are cached after the first download, so subsequent uses will be faster.

## Project Structure

```
VideoToText/
├── main.py                 # Application entry point
├── gui.py                  # GUI module (Tkinter interface)
├── audio_extractor.py      # Audio extraction module (ffmpeg)
├── transcriber.py          # Whisper transcription module
├── test_whisper.py        # Installation test script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── transcription.log      # Application log file (created at runtime)
```

## Model Sizes Comparison

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | ~39 MB | Very Fast | Basic | Quick tests, low accuracy needs |
| base | ~74 MB | Fast | Good | **Recommended for most users** |
| small | ~244 MB | Medium | Better | Better accuracy needed |
| medium | ~769 MB | Slow | High | High accuracy needed |
| large | ~3 GB | Very Slow | Best | Maximum accuracy, requires 10GB+ RAM |

## Troubleshooting

### "ffmpeg is not installed or not in PATH"

- **Windows**: Make sure ffmpeg is added to your system PATH. Restart your terminal/IDE after installation.
- **macOS/Linux**: Verify installation with `ffmpeg -version`. If not found, check your PATH.

### "Failed to load Whisper model"

- Check your internet connection (first-time model download requires internet)
- Ensure you have enough disk space (models can be large)
- Try a smaller model size first (e.g., 'tiny' or 'base')

### "CUDA out of memory" or GPU errors

- The application will automatically fall back to CPU if GPU fails
- Try using a smaller model size
- Close other GPU-intensive applications

### Slow transcription

- Use a smaller model size (tiny or base)
- Ensure GPU is being used (check the log file)
- Close other resource-intensive applications
- For very long videos, consider splitting them into smaller segments

### Application crashes or freezes

- Check `transcription.log` for error messages
- Ensure you have enough RAM (especially for large models)
- Try restarting the application

## Performance Tips

1. **Use GPU when available**: GPU can be 10-50x faster than CPU
2. **Choose appropriate model size**: Base model is usually the best balance
3. **Close other applications**: Free up system resources
4. **For long videos**: Consider splitting into smaller segments
5. **First run**: Be patient during model download

## Output Formats

### Plain Text (.txt)
Simple text file with the transcribed content. No timestamps.

### SRT Subtitles (.srt)
Standard subtitle format with timestamps. Can be used with video players or video editing software.

Example SRT format:
```
1
00:00:00,000 --> 00:00:05,000
Hello, this is the first subtitle.

2
00:00:05,000 --> 00:00:10,000
And this is the second one.
```

## Logging

The application creates a `transcription.log` file in the project directory. This file contains:
- Application startup information
- Transcription progress
- Error messages
- Debug information

Check this file if you encounter any issues.

## System Requirements

### Minimum Requirements
- **CPU**: Any modern processor (2+ cores recommended)
- **RAM**: 4 GB (8 GB recommended)
- **Storage**: 5 GB free space (for models and temporary files)
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- **CPU**: Multi-core processor (4+ cores)
- **RAM**: 8 GB (16 GB for large model)
- **GPU**: CUDA-capable GPU with 4+ GB VRAM (optional but recommended)
- **Storage**: 10 GB free space

## License

This project uses OpenAI Whisper, which is licensed under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the `transcription.log` file for error details
3. Ensure all dependencies are properly installed
4. Try running `test_whisper.py` to verify installation

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [ffmpeg](https://ffmpeg.org/) - Multimedia framework for audio extraction

