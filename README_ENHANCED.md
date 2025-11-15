# Video/Audio to Text Transcription - Enhanced Version

## 🎯 Overview

This enhanced version provides a powerful, user-friendly application for transcribing video and audio files using OpenAI's Whisper model. It features dual modes, automatic model selection, multi-language support, and audio recording capabilities.

> **💡 Looking for the latest interface?** Check out the **Qt GUI** version (`README_QT.md`) which features a modern sidebar navigation, dark/light themes, and auto-transcription workflow. This Enhanced Tkinter version remains fully functional and offers all the same core features with a traditional interface.

## ✨ New Features

### 🎨 Dual Mode Interface

#### **Basic Mode** (Recommended for Most Users)
- 🖱️ Simple drag-and-drop interface
- 🤖 Automatic model selection
- ⚡ Starts with fastest model, upgrades if needed
- 📋 One-click transcription
- Perfect for quick, hassle-free transcriptions

#### **Advanced Mode** (For Power Users)
- ⚙️ Full control over all settings
- 🎙️ Built-in audio recording (microphone + system audio)
- 📊 Manual model selection
- 🌍 Multi-language detection
- 📝 Custom instructions/prompts
- 🎬 Multiple output formats (TXT, SRT, VTT)

### 🤖 Automatic Model Selection

The app intelligently selects the best model for your content:

1. **Starts with Tiny Model** - Fast initial processing
2. **Analyzes Quality** - Checks transcription confidence
3. **Upgrades if Needed** - Automatically tries better models
4. **Optimizes Speed vs Quality** - Balances performance

### 🎤 Audio Recording

Record audio directly in the app:
- **Microphone Recording** - Record your voice
- **System Audio Recording** - Capture desktop/speaker audio
- **Direct Transcription** - Recorded audio automatically loaded
- **Audio Device Settings** - View and configure devices

### 🌍 Multi-Language Support

- **User-Guided Multi-Language (Updated Nov 2025)** – In the Qt path a dialog allows explicit multi-language declaration + allowed-language selection (EN, CS, etc.). Enhanced transcriber now supports:  
   - Fast transcript-based heuristic segmentation (no initial sampling pass)  
   - Automatic fallback chunk-based reanalysis if heuristic collapses to single language  
   - Allowed-language enforcement to suppress spurious detections  
   - Cancellation and performance overlay (elapsed, ETA, RTF) integration.

### 📦 Standalone Distribution

- **No Installation Required** - Just extract and run
- **Bundled Runtime** - Includes Python and all dependencies
- **Offline Capable** - Tiny model can be bundled
- **Cross-Platform** - Windows, macOS, Linux

## 🚀 Quick Start

### Option 1: Run Enhanced Version (Requires Python)

```bash
# Windows
run_enhanced.bat

# Linux/macOS
chmod +x run_enhanced.sh
./run_enhanced.sh

# macOS (double-click)
chmod +x run_enhanced.command
# Then double-click run_enhanced.command in Finder
```

### Option 2: Build Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build without bundled model (smaller size, requires internet for first use)
python build_standalone.py

# Build with bundled tiny model (larger size, works offline)
python bundle_model.py
python build_standalone.py --include-model

# Build as single file (slower startup)
python build_standalone.py --onefile
```

The standalone executable will be in `dist/Video2Text/`

## 📋 Requirements

### For Running Enhanced Version

```
Python 3.8 or higher
openai-whisper>=20231117
torch>=2.0.0
torchaudio>=2.0.0
ffmpeg-python>=0.2.0
numpy>=1.24.0
tqdm>=4.65.0
sounddevice>=0.4.6    # For audio recording
scipy>=1.10.0         # For audio processing
Pillow>=10.0.0        # For image support
TkinterDnD2>=0.3.0    # For drag-and-drop (optional)
```

### External Dependencies

- **FFmpeg** - Required for audio/video processing
  - Windows: `choco install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

- **CUDA Toolkit** (Optional) - For GPU acceleration
  - Significantly speeds up transcription
  - Download from: https://developer.nvidia.com/cuda-downloads

## 📖 Usage Guide

### Basic Mode

1. **Launch the Application**
   ```bash
   # Windows
   run_enhanced.bat

   # Linux/macOS
   ./run_enhanced.sh
   ```

2. **Select Basic Mode** (default)
   - Click "📱 Basic Mode" button if not already selected

3. **Add Your File**
   - **Drag & Drop**: Drag video/audio file to the drop zone
   - **Browse**: Click the drop zone to browse for a file
   - **Record**: Click "🎤 Record Audio" to record directly

4. **Transcribe**
   - Click "✨ Transcribe Now"
   - Wait for automatic processing
   - Model will auto-upgrade if quality is insufficient

5. **Save Results**
   - Click "💾 Save Transcription"
   - Choose location and format

### Advanced Mode

1. **Switch to Advanced Mode**
   - Click "⚙️ Advanced Mode" button

2. **Configure Settings**

   **Audio Source:**
   - Browse for file, or
   - Click "🎤 Start Recording" to record audio
     - Choose microphone or system audio
     - Click "Start Recording"
     - Click "Stop Recording" when done

   **Model Selection:**
   - Keep "Auto-select" enabled (recommended), or
   - Uncheck and manually select model size
   - Click "?" for model information

   **Language:**
   - Keep "Auto-detect" (recommended), or
   - Select specific language
   - Check "Detect multiple languages" for mixed content

   **Output Format:**
   - Plain Text (.txt) - Simple transcription
   - SRT Subtitles (.srt) - With timestamps for video
   - VTT Subtitles (.vtt) - Web-compatible format

   **Instructions** (Optional):
   - Add context for better accuracy
   - Example: "Meeting between John (CEO) and Sarah (CTO)"
   - Helps with speaker recognition

3. **Start Transcription**
   - Click "Start Transcription"
   - Monitor progress bar
   - View real-time status updates

4. **Save Results**
   - Click "💾 Save Transcription"
   - Choose format and location

## 🎨 Model Selection Guide

| Model  | Size   | Speed (GPU) | Speed (CPU) | Best For                          |
|--------|--------|-------------|-------------|-----------------------------------|
| tiny   | ~75MB  | 100x RT     | 10x RT      | Quick tests, simple speech        |
| base   | ~142MB | 67x RT      | 6.7x RT     | Most common use cases             |
| small  | ~466MB | 33x RT      | 3.3x RT     | Better accuracy, accents          |
| medium | ~1.5GB | 11x RT      | 1.7x RT     | High accuracy, complex audio      |
| large  | ~2.9GB | 5.5x RT     | 0.8x RT     | Maximum accuracy, professional    |

*RT = Real-time (e.g., 10x RT means 1 minute of audio takes ~6 seconds to transcribe)*

### Auto-Selection Strategy

The auto-selection feature:
1. Starts with **tiny** (fastest)
2. Checks confidence score
3. If score < 70%, tries **base**
4. If score < 80%, tries **small**
5. Uses best quality result

## 🛠️ Troubleshooting

### Application Won't Start

```bash
# Check Python version (must be 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check FFmpeg
ffmpeg -version
```

### No Audio Devices Found

```bash
# Linux: Install ALSA
sudo apt install libasound2-dev

# Check devices in Advanced Mode
Click "⚙️ Audio Settings" button
```

### GPU Not Detected

```bash
# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"

# If False, reinstall PyTorch with CUDA:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Transcription Quality Issues

**Try:**
- Switch to Advanced Mode
- Use larger model (base → small → medium)
- Add context in Instructions field
- Ensure audio quality is good
- Check correct language is selected

### Memory Errors

**Solutions:**
- Use smaller model (medium → small → base)
- Close other applications
- Ensure at least 8GB RAM for large model
- Use CPU instead of GPU if GPU memory is limited

## 📦 Building Standalone Version

### Step 1: Prepare Environment

```bash
# Install build dependencies
pip install pyinstaller

# Optional: Bundle tiny model for offline use
python bundle_model.py
```

### Step 2: Build Executable

```bash
# Standard build (directory-based, faster startup)
python build_standalone.py --include-model

# Single-file build (portable, slower startup)
python build_standalone.py --include-model --onefile
```

### Step 3: Test Build

```bash
# Test the executable
cd dist/Video2Text
./Video2Text  # or Video2Text.exe on Windows
```

### Step 4: Distribute

Package the `dist/Video2Text/` folder with:
- All files in the folder
- FFmpeg installation instructions
- README_ENHANCED.md (this file)

## 🔍 Advanced Features

### Command-Line Arguments

The enhanced version can be run with command-line arguments:

```bash
python main_enhanced.py --help
```

### Batch Processing

For batch processing, use the original `main.py` with a script:

```python
from transcriber import Transcriber
from audio_extractor import AudioExtractor

extractor = AudioExtractor()
transcriber = Transcriber(model_size='base')
transcriber.load_model()

files = ['file1.mp4', 'file2.mp3', 'file3.wav']

for file in files:
    audio = extractor.extract_audio(file)
    result = transcriber.transcribe(audio)

    with open(f'{file}.txt', 'w') as f:
        f.write(result['text'])
```

### Multi-Language Analysis

```python
from transcriber_enhanced import EnhancedTranscriber

transcriber = EnhancedTranscriber(model_size='small')
transcriber.load_model()

result = transcriber.transcribe_multilang(
    'mixed_language_audio.mp3',
   detect_language_changes=True,
   skip_sampling=True,                # Skip legacy sampling when user knows it's multi-language
   fast_text_language=True,           # Enable fast transcript heuristic segmentation
   allowed_languages=['en','cs']      # Restrict detection to expected languages
)

# View language timeline
print(result['language_timeline'])

# Get detailed report
report = transcriber.format_multilang_report(result)
print(report)
```

## 📊 Performance Benchmarks

Tested on: Intel i7-12700K, RTX 4080, 32GB RAM

| File       | Duration | Model  | Device | Time   | Speed    |
|------------|----------|--------|--------|--------|----------|
| sample.mp4 | 5 min    | tiny   | GPU    | 3s     | 100x RT  |
| sample.mp4 | 5 min    | base   | GPU    | 4.5s   | 67x RT   |
| sample.mp4 | 5 min    | small  | GPU    | 9s     | 33x RT   |
| sample.mp4 | 5 min    | medium | GPU    | 27s    | 11x RT   |
| podcast.mp3| 32 min   | base   | GPU    | 29s    | 66x RT   |
| podcast.mp3| 32 min   | small  | GPU    | 58s    | 33x RT   |
| mixed_cs_en.wav | 12 min | large | GPU | 140s | 5.1x RT (heuristic+fallback) |
| mixed_cs_en.wav | 12 min | large | GPU | 118s | 6.0x RT (heuristic only) |

Note: Multi-language heuristic path removes initial sampling pass; fallback chunk analysis only triggers when heuristic yields a single language despite multi-language selection.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Better drag-and-drop support across platforms
- Additional output formats
- Real-time transcription
- Speaker diarization
- Translation features
- Dark mode theme
- Plugin system

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **OpenAI Whisper** - Amazing transcription model
- **PyTorch** - Deep learning framework
- **FFmpeg** - Media processing
- **Tkinter** - GUI framework

## 📞 Support

For issues, questions, or suggestions:

1. Check the Troubleshooting section
2. Review logs in `logs/transcription.log`
3. Open an issue on GitHub
4. Consult the original Whisper documentation

## 🗺️ Roadmap

**v2.0** (Current - Enhanced Tkinter)
- ✅ Dual-mode interface
- ✅ Auto model selection
- ✅ Audio recording
- ✅ Multi-language support
- ✅ Standalone packaging

**v3.0** (Current - Qt GUI)
- ✅ Modern sidebar navigation
- ✅ Dark/light mode themes
- ✅ Auto-transcription workflow
- ✅ Auto-navigation between tabs
- ✅ Proper threading (QThread)

**v2.1/v3.1** (Planned)
- ⏳ Real-time transcription
- ⏳ GPU memory optimization
- ⏳ Better progress estimation
- ⏳ Desktop notifications

**v2.2/v3.2** (Future)
- ⏳ Speaker diarization
- ⏳ Translation support
- ⏳ Cloud backup
- ⏳ Batch processing

---

**Made with ❤️ by the Video2Text Team**

For the original version, see: README.md
