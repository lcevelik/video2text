# FonixFlow - Modern Qt Interface
![FonixFlow Logo](assets/fonixflow_logo.png)

## 🎨 Ultra-Minimal, Professional GUI

This is the **modern Qt-based interface** for FonixFlow, built with PySide6 for a polished, professional appearance across all platforms. Features **ultra-minimal design** with sidebar navigation, auto theme detection, and a branded top bar with the FonixFlow logo.
Auto-Navigation - Switches to transcript tab automatically after transcription completes

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
- 🌐 **Smart Language Detection** - TRUE code-switching support (Czech ↔ English)
- ⚡ **5-10x Faster** - v3.2.0 optimizations for blazing-fast multi-language transcription
- 🎯 **Auto-Transcribe** - Drop files and start immediately
- 🔄 **Auto-Navigation** - Switches to results when done

### **Better Cross-Platform**
- ✅ **Native look** on Windows, macOS, and Linux
- ✅ **System theme detection** - Automatically matches your OS
- ✅ **Better DPI scaling** for high-resolution displays
- ✅ **Consistent behavior** across all platforms

---

## 🔑 License Requirements

FonixFlow uses a license key system for premium features:

- **Free Features (No License Required):** Audio recording, file upload, settings, UI navigation, transcription (limited to 500 words)
- **Premium Features (License Required):** Unlimited transcription, full multi-language support

**Free Version Limits:**
- Transcription is available but limited to **500 words** per transcription
- If your transcription exceeds 500 words, it will be truncated with a notification

**To Activate:**
1. Go to Settings tab
2. Click "Activate" button
3. Enter your license key
4. Unlimited transcription unlocks immediately

For detailed information, see [LICENSE_AND_FEATURES.md](LICENSE_AND_FEATURES.md)

---

## 🚀 Quick Start

### **New Features**
- FonixFlow logo in top bar
- Auto-jump to transcript tab after transcription
- Improved modularity and refactoring for maintainability
- License activation system for premium features

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
# Install dependencies
pip install -r requirements.txt

# Run the Qt GUI
python app/fonixflow_qt.py
```

---

## 📦 Installation


### **Option 1: Install All Dependencies**
```bash
pip install -r requirements.txt
```

Note (Python 3.13): Python 3.13 removed the stdlib module `audioop` used by some audio libraries. We include `pyaudioop` in `requirements.txt` to restore compatibility for recording/export. If you upgraded Python and recording fails, run:

```bash
pip install pyaudioop
```

---

## 🔑 License System

FonixFlow now supports both online and offline license validation:

- **Local License File**: Add your license key to `licenses.txt` in the app folder for offline validation.
- **LemonSqueezy API**: If the key is not found locally, the app will check the LemonSqueezy license API.

This allows you to run the app even if the LemonSqueezy store is offline or unavailable.

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

### **🧪 Deep Scan (Toggle)**
Menu item: **Enable Deep Scan** (checkbox)

Default: OFF (fast heuristic-only segmentation)

When OFF (Heuristic Mode):
- Single full transcription pass (large model)
- Transcript-only segmentation (stopword + diacritic scoring windows)
- Limited fallback chunk re-analysis only if multi-mode collapses to one language

When ON (Deep Scan Mode):
- Performs secondary chunk re-transcription on mixed / uncertain windows
- Refines short interwoven phrases and rapid switches
- Slower (≈ +25–40% runtime impact)

Use Deep Scan only if the heuristic timeline appears merged or misses very short alternations.

---

## 🌐 Multi-Language Transcription

### **⚡ Performance Optimized Workflow (v3.2.0 - Nov 2025)**

**5-10x faster multi-language transcription!** Language detection now uses intelligent text-based analysis instead of re-transcribing audio chunks.

When you drop a file or finish recording a **Language Mode Dialog** appears:

1. Choose Single vs Multi-language.
2. If Multi-language: tick allowed languages. By default, English and Spanish are preselected for clarity (you can change this to match your content).
3. App uses minimal sampling (3 strategic points) for classification.

Processing steps (Multi-language) - **OPTIMIZED**:
1. **Single transcription pass** with word-level timestamps (no redundancy).
2. **Instant text-based language detection** using linguistic heuristics:
   - Diacritic patterns (č, ř, š for Czech; é, à for French, etc.)
   - Language-specific stopwords and common words
   - Character set analysis
3. Allowed-language list constrains classification (suppresses outliers).
4. Segments merged → timeline + combined text.

**Performance gains:**
- ✅ No chunk re-transcription (eliminated 75+ subprocess calls)
- ✅ Text analysis completes in <1 second (was 180+ seconds)
- ✅ Audio sampling: 3 samples (was up to 25)
- ✅ Total speedup: **5.2x faster** on typical 5-minute multi-language files

Deep re-transcription of audio chunks (legacy "two-pass") has been **eliminated** - text-based analysis is proven accurate for languages with distinctive features.

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

**Performance (v3.2.0 Optimized):**
- **Single-pass transcription**: One transcription with word timestamps (no redundant passes)
- **Text-based language detection**: <1 second analysis (was 180+ seconds of re-transcription)
- **Minimal sampling**: 3 strategic samples (was 3-25)
- **Zero chunk overhead**: Eliminated 75+ ffmpeg subprocess calls
- **5.2x faster**: 5-minute multi-language file now processes in ~45 seconds (was ~235 seconds)
- **Large model accuracy retained**: Same quality, dramatically faster processing
- **Allowed-language filtering**: Improves precision and consistency

**Cancellation:** Mid-process cancel keeps processed segments and any partial language timeline.

**Overlay Metrics:** Status bar shows `% | Elapsed | ETA` continuously; final line includes Real-Time Factor (RTF).

**Heuristic Logic:** English scored via expanded stopword list; Czech via diacritic + common word density; fallback inherits previous language to avoid excessive 'unknown'.

**Upgrade Summary:**
- Removed redundant sampling pass when user confirms multi-language.
- Added transcript-only segmentation `_detect_language_from_transcript`.
- Added automatic deep chunk fallback when heuristic collapses.
- Added language allow‑list selection dialog.
- Added cancellation and performance overlay.

---

## 🤖 Automatic Optimization & Model Defaults

**No configuration needed!** The app chooses sensible defaults based on the mode you select in the Language Mode dialog:

- **Single-language:** Uses the `base` model by default (balanced speed & accuracy). If you explicitly select English-only content you can choose `base.en`, `small.en`, or `medium.en` for an English‑optimized variant (slightly smaller download / memory footprint and focused language vocabulary).
- **Multi-language:** Uses the `large` model for maximum cross‑language accuracy and cleaner boundaries between languages.
- **Detection / Segmentation:** Text heuristic pass (single transcription) + automatic fallback deep chunk pass only if declared multi-language collapses to one language.
- **Deep Scan Toggle:** When enabled, forces full chunk re-analysis for highly interwoven code-switching; leave OFF for fastest processing.

### English‑Only Variants (.en)
Available models now include: `tiny.en`, `base.en`, `small.en`, `medium.en` (Whisper does not provide `large.en`). These are trained for English only and can reduce minor false positives and slightly improve speed on English content. For mixed languages, always use the non-`.en` variant.

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
