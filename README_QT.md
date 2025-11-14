# Video2Text - Modern Qt Interface

## 🎨 Ultra-Minimal, Professional GUI

This is the **modern Qt-based interface** for Video2Text, built with PySide6 for a polished, professional appearance across all platforms. Features **ultra-minimal design** with sidebar navigation and **auto theme detection**.

---

## ✨ Why Qt Version?

### **Ultra-Minimal Design**
- 🎯 **Clean Interface** - No unnecessary titles or descriptions
- ☰ **Hamburger Menu** - All settings in one organized menu
- 📱 **Sidebar Navigation** - Record, Upload, Transcript tabs
- 🌓 **Auto Theme** - Follows your system theme automatically
- 🎨 **Content-Focused** - Maximum screen space for what matters
- 🖱️ **Intuitive** - Simple, direct interactions

### **Fully Automatic**
- 🤖 **Zero Configuration** - No settings to adjust
- 🚀 **Optimal Models** - Automatically uses best models for accuracy
- 🌐 **Two-Pass Detection** - TRUE code-switching support (Czech ↔ English)
- ⚡ **Auto-Transcribe** - Drop files and start immediately
- 🔄 **Auto-Navigation** - Switches to results when done

### **Better Cross-Platform**
- ✅ **Native look** on Windows, macOS, and Linux
- ✅ **System theme detection** - Automatically matches your OS
- ✅ **Better DPI scaling** for high-resolution displays
- ✅ **Consistent behavior** across all platforms

---

## 🚀 Quick Start

### **Windows**
```bash
run_qt.bat
```

### **Linux/macOS**
```bash
chmod +x run_qt.sh
./run_qt.sh
```

### **Manual Launch**
```bash
# Install PySide6 first
pip install PySide6>=6.6.0

# Run the Qt GUI
python gui_qt.py
```

---

## 📦 Installation

### **Option 1: Install All Dependencies**
```bash
pip install -r requirements.txt
```

### **Option 2: Qt Only**
```bash
pip install PySide6>=6.6.0
```

Plus the core dependencies (whisper, torch, etc.)

---

## 🎯 Interface Overview

### **Layout**
```
                                              ☰ (Menu)
┌──────────┬────────────────────────────────────────┐
│ 🎙️ Record│                                       │
│ 📁 Upload │         Content Area                  │
│ 📄 Transcript│                                    │
└──────────┴────────────────────────────────────────┘
```

Clean, minimal, content-focused.

---

## 📋 Three Main Tabs

### **🎙️ Record Tab**

**What you see:**
- "Start Recording" button (centered)
- Progress bar
- Recording info tip

**What it does:**
1. Click "Start Recording"
2. Records microphone + system audio simultaneously
3. Button changes to "Stop Recording" (red)
4. Recording duration shown while active
5. Automatically transcribes when stopped

**Settings:**
- Change recording directory: Menu → Settings → Change Recording Directory

---

### **📁 Upload Tab**

**What you see:**
- Drag and drop zone
- Progress bar

**How it works:**
- **Fully automatic** - No settings to configure!
- Uses optimal configuration for multi-language transcription
- Two-pass detection: Fast language detection + Accurate transcription
- Perfect for code-switching (Czech ↔ English ↔ Czech)

**How to use:**
1. Drag and drop your video/audio file (or click to browse)
2. Transcription starts automatically with optimal settings
3. Progress updates in real-time
4. Auto-navigates to Transcript tab when done

---

### **📄 Transcript Tab**

**What you see:**
- Language info (appears after transcription)
- Transcription text area
- Save button

**What you get:**
- Full transcription with all languages properly transcribed
- Language info: "Languages detected: Czech, English | 45 segments"
- Language timeline (if multiple languages):
  ```
  ============================================================
  🌍 LANGUAGE TIMELINE:
  ============================================================

  [00:00:00 - 00:00:05] Language: Czech (CS)
  [00:00:05 - 00:00:10] Language: English (EN)
  [00:00:10 - 00:00:15] Language: Czech (CS)
  ```

**How to save:**
1. Choose format (TXT, SRT, VTT)
2. Click "💾 Save Transcription"

---

## ☰ Hamburger Menu

Click the **☰** button (top-right) to access all settings:

### **⚙️ Settings**

**🎨 Theme**
- 🔄 **Auto (System)** ← *default* - Follows your OS theme
- ☀️ **Light** - Always light mode
- 🌙 **Dark** - Always dark mode

**📁 Recording Directory**
- **Change Recording Directory** - Choose where recordings are saved
- **Open Recording Directory** - Open folder in file explorer

### **🔄 New Transcription**
- Clears current results
- Resets interface for next transcription
- Prompts for confirmation to avoid accidental clearing

---

## 🌐 Multi-Language Transcription

### **Two-Pass Detection (Always Enabled)**

**Automatic optimization for code-switching:**
1. **Pass 1 (Fast Detection):** Uses base model to quickly detect language boundaries
2. **Pass 2 (Accurate Transcription):** Uses large model to transcribe each segment precisely
3. Each segment detected in its correct language
4. All segments combined into one complete transcription

**Example:**
```
Input audio:
"Dobrý den, jak se máte?" (Czech)
"Hello, how are you?" (English)
"Můžeme si koupit kuře?" (Czech)

Output transcription:
Dobrý den, jak se máte? Hello, how are you? Můžeme si koupit kuře?

Language Timeline:
[00:00:00 - 00:00:05] Language: Czech (CS)
[00:00:05 - 00:00:10] Language: English (EN)
[00:00:10 - 00:00:15] Language: Czech (CS)
```

**Result:** Czech transcribed in Czech, English in English, perfectly combined.

**Supported Languages:**
English, Spanish, French, German, Polish, Czech, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, Hebrew, Thai, Vietnamese, Turkish, Romanian, Swedish, Danish, Norwegian, Finnish, Greek, Hindi, Indonesian, Ukrainian, and more.

**Performance:**
- ⚠️ Slower than single-pass transcription
- ✅ Much more accurate for mixed languages
- ✅ Essential for code-switching conversations

---

## 🤖 Automatic Optimization

**No configuration needed!** The app automatically uses:

- **Detection:** Base model (~74 MB) - Fast language boundary detection
- **Transcription:** Large model (~3 GB) - Best accuracy for multi-language
- **Mode:** Two-pass deep scanning - Perfect for code-switching

The system downloads models automatically on first use. Subsequent uses are instant.

---

## 🎬 Quick Workflows

### **Transcribe a File**
1. Open Qt GUI: `python gui_qt.py`
2. Go to **Upload** tab (or stay on default)
3. Drag and drop your file
4. Wait for transcription (auto-navigates to Transcript)
5. Click "💾 Save Transcription"

### **Record and Transcribe**
1. Go to **Record** tab
2. Click "Start Recording"
3. Speak/play audio
4. Click "Stop Recording"
5. Transcription starts automatically
6. View results in **Transcript** tab

### **Start Fresh**
1. Click **☰** (hamburger menu)
2. Select "🔄 New Transcription"
3. Confirm
4. Interface resets for next transcription

### **Change Theme**
1. Click **☰** (hamburger menu)
2. Settings → Theme
3. Choose Auto/Light/Dark

---

## 💡 Tips & Tricks

### **For Best Results:**
- Speak clearly with pauses between language switches
- Good audio quality = better detection
- Use high-quality source files when possible

### **For Long Recordings:**
- Transcription is fully automatic with optimal settings
- Progress updates every few seconds
- Don't close the application during transcription
- Large model may take several minutes

### **Theme Tips:**
- **Auto mode**: Automatically matches your system
  - Dark system → Dark app
  - Light system → Light app
- Changes apply immediately
- Preference is saved

---

## 🎨 UI Elements

### **Drag & Drop Zone**
- Clean border (no background color)
- Text: "Drag and drop video/audio file"
- Click anywhere to browse
- Shows "✓ filename" when file selected

### **Recording Button**
- **Before**: "Start Recording" (blue)
- **During**: "Stop Recording" (red)
- Changes color to indicate state

### **Save Button**
- Disabled until transcription completes
- Enabled after successful transcription
- Supports TXT, SRT, VTT formats

---

## 🐛 Troubleshooting

### **No Audio Devices Found**
- **Windows**: Check microphone permissions in Settings
- **macOS**: Grant microphone access in System Preferences → Security
- **Linux**: Ensure ALSA/PulseAudio is configured

### **Transcription is Slow**
- Two-pass transcription takes time (expected for accuracy)
- Large model ensures best multi-language results
- First transcription downloads models (~3.1 GB total)
- Check CPU/GPU usage

### **Wrong Language Detected**
- Automatic two-pass detection should handle most cases
- Check audio quality
- Verify speakers are clear
- Ensure clear pauses between language switches

### **Theme Not Changing**
- Check Menu → Settings → Theme selection
- Verify checkmark is on selected mode
- Restart application if needed

---

## 🎉 Enjoy Your Transcriptions!

The Qt interface provides a **professional, minimal experience** for all your transcription needs.

**Questions?** See main README.md or check the code!
