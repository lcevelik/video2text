# Video2Text - Modern Qt Interface

## 🎨 Beautiful, User-Friendly GUI with Sidebar Navigation

This is the **modern Qt-based interface** for Video2Text, built with PySide6 for a polished, professional appearance across all platforms. Features a **sidebar navigation system** with organized tabs and **dark/light theme support**.

---

## ✨ Why Qt Version?

### **Modern Design**
- 🎯 **Sidebar Navigation** - Clean tabs for Upload, Record, and Transcript
- 🌓 **Dark/Light Mode** - Toggle themes for comfortable viewing in any lighting
- 🎨 **Card-based layout** - Clean, organized interface
- 🌈 **Professional styling** - Polished buttons, smooth transitions
- 📱 **Responsive design** - Adapts to different screen sizes
- 🖱️ **Intuitive interactions** - Hover effects, visual feedback

### **Better Cross-Platform**
- ✅ **Native look** on Windows, macOS, and Linux
- ✅ **Consistent behavior** across all platforms
- ✅ **Better DPI scaling** for high-resolution displays
- ✅ **Modern fonts** and icon support

### **Enhanced User Experience**
- 🎯 **Simpler interface** - Less technical, more approachable
- ⚡ **Auto-transcribe** - Drop files and transcription starts automatically (Basic Mode)
- 🔄 **Auto-navigation** - Automatically switches to Transcript tab when done
- 🚀 **Smoother animations** - Professional feel
- 💡 **Better visual hierarchy** - Easy to understand
- 🎭 **Persistent preferences** - Your theme and settings are saved

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

This installs both Tkinter version and Qt version dependencies.

### **Option 2: Qt Only**
```bash
pip install PySide6>=6.6.0
```

Plus the core dependencies (whisper, torch, etc.)

---

## 🎯 Features

### **Sidebar Navigation** (Both Modes)
Each mode features a clean sidebar with three organized tabs:

#### **Upload Tab**
- 📁 **Drag & Drop** - Visual drop zone for files
- 🎯 **Auto-Transcribe** - Drop file and transcription starts automatically (Basic Mode)
- 📊 **Progress Tracking** - Real-time progress updates
- ⚡ **Click to Browse** - Alternative to drag-and-drop

#### **Record Tab**
- 🎤 **Dual Recording** - Captures mic + speaker simultaneously
- 📁 **Directory Selection** - Choose where recordings are saved
- ⏺️ **One-Click Recording** - Start/stop with single button
- 🔄 **Auto-Load** - Recorded audio automatically loads for transcription

#### **Transcript Tab**
- 📝 **Results Display** - View transcription with formatting
- 💾 **Save Options** - Export as TXT, SRT, or VTT
- 🔄 **Auto-Navigation** - Automatically shown when transcription completes
- 📋 **Format Selection** - Choose output format before saving
- 🔄 **New Transcription** - Clear results and start fresh for next meeting

### **Basic Mode**
- ✨ **Simplified Interface** - Only essential controls
- 🤖 **Smart Model Selection** - Automatically chooses best model
- 🌐 **Automatic Multi-Language Detection** - Detects when speakers switch languages (no configuration needed)
- 🚀 **Automatic Workflow** - Drop file → transcribe → view results with language timeline
- 🎯 **Perfect for Beginners** - No configuration needed

### **Advanced Mode**
- ⚙️ **Full Control** - Manual model selection (tiny/base/small/medium/large)
- 🌍 **Language Options** - Choose from 99 supported languages
- 🌐 **Multi-Language Detection** - Track when speakers switch languages (perfect for multilingual meetings)
- 📝 **Multiple Formats** - TXT, SRT, VTT output
- 🎛️ **Fine-Tuning** - All advanced options available
- 💬 **Custom Instructions** - Add context for better accuracy

### **Theme System**
- 🌓 **Dark/Light Mode** - Toggle with one click
- 💾 **Persistent Preference** - Your choice is saved
- 🎨 **Complete Integration** - All UI elements themed
- 👁️ **Comfortable Viewing** - Optimized for any lighting condition

### **Modern UI Elements**
- 📂 **Sidebar Navigation** - Clean, organized tabs
- 💳 **Cards** - Organized content sections
- 🎨 **Styled Buttons** - Primary/secondary styling with hover effects
- 📊 **Smooth Progress** - Animated progress bars
- 🎬 **Drop Zone** - Visual file upload area with feedback
- 🔔 **Status Updates** - Clear feedback messages
- 🌈 **Theme-Aware Widgets** - All elements respond to theme changes

---

## 🎨 Interface Comparison

### **Old Tkinter GUI**
- ❌ Basic, technical appearance
- ❌ Inconsistent cross-platform look
- ❌ Limited styling options
- ❌ No animations or transitions

### **New Qt GUI**
- ✅ Modern, polished appearance
- ✅ Native look on all platforms
- ✅ Professional styling
- ✅ Smooth animations

---

## 📘 How to Use the Qt GUI

### **Basic Workflow**

1. **Launch the Application**
   ```bash
   python gui_qt.py
   ```

2. **Choose Your Mode**
   - Click **"📱 Basic Mode"** for simplified interface (recommended for beginners)
   - Click **"⚙️ Advanced Mode"** for full control

3. **Use the Sidebar Tabs**

   **Upload Tab** (Start here):
   - Drag and drop your video/audio file
   - Or click the drop zone to browse
   - In Basic Mode, transcription starts automatically!

   **Record Tab** (Optional):
   - Click "Start Recording" to record audio
   - Records both microphone and system audio
   - Configure recording directory in settings
   - Recorded audio loads automatically

   **Transcript Tab** (Results):
   - View your transcription results
   - Choose output format (TXT, SRT, VTT)
   - Click "Save Transcription" to export
   - Automatically shown when transcription completes

4. **Toggle Theme** (Optional)
   - Click the 🌙/☀️ button in the header
   - Switch between dark and light modes
   - Your preference is saved automatically

### **Basic Mode Step-by-Step**

1. Make sure **Basic Mode** is selected
2. Go to **Upload Tab** (sidebar)
3. **Drop your file** into the drop zone (or click to browse)
4. **Wait** - transcription starts automatically with multi-language detection enabled
5. **View results** - automatically navigate to Transcript tab
   - Includes full transcription in all languages
   - Language timeline appended showing when each language was spoken
6. **Save** - choose format and click "Save Transcription"
7. **Start fresh** - click "🔄 New Transcription" to clear and process another meeting

**Note:** Basic Mode automatically detects language changes - perfect for multilingual meetings without any configuration!

### **Advanced Mode Step-by-Step**

1. Select **Advanced Mode**
2. **Upload Tab**:
   - Drop or browse for your file
   - Choose model size (or use Auto-select)
   - Select language (or use Auto-detect)
   - **For multilingual meetings**: Check "🌍 Detect language changes"
   - Add custom instructions (optional)
   - Click "Start Transcription"
3. **Transcript Tab**:
   - Wait for transcription to complete
   - Review results (includes language timeline if multi-language detection was enabled)
   - Select output format
   - Click "Save Transcription"

### **Multi-Language Detection (For Multilingual Meetings)**

Perfect for international meetings, conferences, or recordings with multiple languages:

**In Basic Mode** (Automatic):
- Multi-language detection is **always enabled** - no configuration needed!
- Just drop your file and transcribe
- Results automatically include language timeline
- Uses fast detection (Whisper's primary language + character analysis)

**In Advanced Mode** (Manual Control):
1. Go to Upload Tab
2. Check the box: **"🌍 Detect language changes (for multilingual meetings)"**
3. **For TRUE code-switching** (people switching languages mid-conversation):
   - Check **"🔬 Deep multi-language scanning (SLOW but accurate)"**
   - Example: Czech → English → Czech in same meeting
   - ⚠️ **Much slower** but handles language mixing correctly
4. Start transcription as normal

**What You Get:**
- Full transcription with all languages properly transcribed
- **Language Timeline** showing when each language was spoken
- Example timeline format:
  ```
  [00:00:15 - 00:02:30] Language: English (EN)
  [00:02:30 - 00:05:45] Language: Spanish (ES)
  [00:05:45 - 00:08:00] Language: English (EN)
  ```
- Automatic detection of: English, Spanish, French, German, Polish, Czech, Chinese, Japanese, Korean, Arabic, Russian, Hebrew, Thai, and more

**Detection Modes:**

1. **Fast Detection** (Default):
   - Uses Whisper's detected language + character-based script analysis
   - Good for meetings where one language dominates
   - Very fast

2. **Deep Scanning** (Advanced Mode option):
   - Re-transcribes each segment individually
   - Each segment gets its own language detection
   - Perfect for **code-switching** (Czech ↔ English ↔ Czech)
   - Slower but highly accurate for mixed languages

**Use Cases:**
- International business meetings with language switching
- Multilingual conferences
- Code-switching conversations (bilingual speakers)
- Customer support calls in multiple languages
- Educational content with multiple languages
- Any recording where speakers switch between languages mid-conversation

## 📸 UI Components

### **1. Header**
```
🎬 Video2Text                          🌙 Dark Mode
AI-Powered Transcription with Whisper
```
Clean, professional branding with theme toggle

### **2. Mode Switcher**
```
[📱 Basic Mode] [⚙️ Advanced Mode]
```
Toggle between simple and advanced interfaces

### **3. Sidebar Navigation**
```
┌─────────────┐
│ 📤 Upload   │ ← Currently selected (highlighted)
│ 🎤 Record   │
│ 📝 Transcript│
└─────────────┘
```
Three main sections organized as tabs

### **4. Upload Tab**
```
┌────────────────────────────┐
│          🎬                │
│  Drag & Drop File Here     │
│    or click to browse      │
└────────────────────────────┘

Progress: ████████░░░░░ 75%
Transcribing audio...
```
Visual file upload with progress tracking

### **5. Record Tab**
```
┌─ Recording Settings ───────┐
│  Directory: ~/Recordings   │
│  [Change Directory]        │
└───────────────────────────┘

[🎤 Start Recording]

Recording: 00:23 ⏺️
```
Recording controls and settings

### **6. Transcript Tab**
```
┌─ Results ──────────────────┐
│  Your transcription text   │
│  appears here with proper  │
│  formatting...             │
└───────────────────────────┘

Format: [TXT ▼]  [💾 Save Transcription]
```
Results display with save options

---

## 🔧 Technical Details

### **Framework**
- **PySide6** (Qt for Python) - Official Qt bindings
- **License**: LGPL (more permissive than PyQt)
- **Version**: 6.6.0+

### **Advantages**
1. **Modern Qt6** - Latest features and improvements
2. **Cross-platform** - Windows, macOS, Linux
3. **Python-friendly** - Pythonic API
4. **Well-documented** - Extensive Qt documentation
5. **Active development** - Regular updates

### **Architecture**
```python
Video2TextQt (QMainWindow)
├── Header (title, subtitle, theme toggle button)
├── Mode Switcher (basic/advanced)
├── Stacked Widget (Mode Container)
│   ├── Basic Mode
│   │   ├── Sidebar (QListWidget) - Tab navigation
│   │   └── Tab Stack (QStackedWidget)
│   │       ├── Upload Tab (drop zone, progress)
│   │       ├── Record Tab (recording controls, settings)
│   │       └── Transcript Tab (results, save options)
│   └── Advanced Mode
│       ├── Sidebar (QListWidget) - Tab navigation
│       └── Tab Stack (QStackedWidget)
│           ├── Upload Tab (drop zone, file info, progress)
│           ├── Record Tab (recording controls, directory settings)
│           └── Transcript Tab (results, format selection, save)
├── Status Bar (current operation feedback)
└── Theme System (Light/Dark color palettes)
```

### **Custom Widgets**
- `ModernButton` - Styled buttons with hover effects and theme support
- `Card` - Container with shadow, rounded corners, and theme-aware colors
- `DropZone` - Drag-and-drop file upload area with theme-aware styling
- `RecordingDialog` - Modern recording interface with dual-stream capture
- `RecordingWorker` - QThread for background audio recording
- `TranscriptionWorker` - QThread for background transcription
- `Theme` - Color palette manager for dark/light modes

### **Threading Architecture**
The Qt GUI uses proper QThread workers for all background tasks:
- **RecordingWorker**: Handles audio recording in background thread
- **TranscriptionWorker**: Handles transcription in background thread
- **Signal/Slot Communication**: Thread-safe updates to GUI
- **No Blocking**: Main UI thread remains responsive during long operations

---

## 🎭 Styling

### **Color Palette**
```
Primary:   #2196F3 (Blue)
Success:   #4CAF50 (Green)
Warning:   #FF9800 (Orange)
Error:     #F44336 (Red)
Text:      #333333
Light:     #F5F5F5
Border:    #E0E0E0
```

### **Typography**
- **Headers**: 20-24px, bold
- **Body**: 14px, regular
- **Small**: 11-12px, light
- **Monospace**: Consolas, Monaco (for transcription)

### **Spacing**
- **Cards**: 20px padding
- **Sections**: 20px spacing
- **Elements**: 10-15px gaps
- **Window**: 20px margins

---

## 🆚 Version Comparison

| Feature | Tkinter (Enhanced) | Qt (Modern) |
|---------|-------------------|-------------|
| **Appearance** | Basic | Modern ⭐ |
| **Cross-platform** | Good | Excellent ⭐ |
| **Customization** | Limited | Extensive ⭐ |
| **Animations** | None | Smooth ⭐ |
| **Learning Curve** | Easy | Moderate |
| **Performance** | Good | Good |
| **File Size** | Smaller | Larger |
| **Dependencies** | Built-in | External |

---

## ✅ Recently Implemented Features

### **Latest Updates**
- ✅ **Dark/Light Mode** - Complete theme system with toggle button
- ✅ **Sidebar Navigation** - Clean tab-based interface
- ✅ **Auto-Navigation** - Automatically switch to Transcript tab when done
- ✅ **Auto-Transcribe** - Drop files and start transcription automatically (Basic Mode)
- ✅ **Persistent Settings** - Your preferences are saved (theme, recording directory)
- ✅ **Theme-Aware Widgets** - All UI elements adapt to selected theme
- ✅ **Proper Threading** - QThread workers for responsive UI

## 🔮 Future Enhancements

### **Planned Features**
- 🎨 **Custom Themes** - User-selectable color schemes beyond dark/light
- 📊 **Real-time Waveform** - Visual audio feedback during recording
- 🎬 **Video Preview** - Thumbnail preview of video files
- 📈 **Statistics Dashboard** - Usage metrics and history
- 🔔 **Desktop Notifications** - Completion alerts
- 🌐 **Multi-language UI** - Interface in multiple languages
- 📝 **Recent Files** - Quick access to recently transcribed files
- 🔍 **Search Transcripts** - Search through saved transcriptions

### **Technical Improvements**
- 🔄 **Auto-updates** - Update checker
- 📦 **Smaller Packaging** - Optimized builds
- 🎯 **Accessibility** - Screen reader support
- 🎤 **Real-time Transcription** - Live transcription as you speak

---

## 🤝 Which Version to Use?

### **Use Tkinter Version If:**
- ✅ You want smallest file size
- ✅ You prefer simpler dependencies
- ✅ You're familiar with Tkinter
- ✅ Basic appearance is fine

### **Use Qt Version If:**
- ✅ You want modern, polished UI ⭐
- ✅ Professional appearance matters
- ✅ Better cross-platform consistency needed
- ✅ You want future enhancements

---

## 📝 Migration Guide

### **From Tkinter to Qt**

**Same Features:**
- ✅ Basic/Advanced modes
- ✅ Auto model selection
- ✅ Recording (mic + speaker)
- ✅ Multi-language support
- ✅ All output formats

**Key Differences:**
1. **Launch script**: Use `run_qt.sh/bat` instead of `run_enhanced.sh/bat`
2. **Dependency**: Requires `PySide6` package
3. **Look**: Modern, card-based design
4. **Feel**: Smoother animations, better feedback

**Data Compatibility:**
- ✅ Same config file (`app_config.json`)
- ✅ Same log files
- ✅ Same model cache
- ✅ Same output formats

---

## 🐛 Troubleshooting

### **Qt Won't Start**
```bash
# Install PySide6
pip install PySide6>=6.6.0

# Check installation
python -c "import PySide6; print(PySide6.__version__)"
```

### **Missing Icons/Fonts**
Qt should handle this automatically. If issues persist:
```bash
# Reinstall PySide6
pip uninstall PySide6
pip install PySide6>=6.6.0
```

### **High DPI Issues**
Qt 6 handles high DPI automatically. If scaling is wrong:
```python
# Add to environment before starting
export QT_AUTO_SCREEN_SCALE_FACTOR=1  # Linux/Mac
set QT_AUTO_SCREEN_SCALE_FACTOR=1     # Windows
```

### **Performance**
Qt GUI may use slightly more memory than Tkinter:
- **Tkinter**: ~200MB
- **Qt**: ~250MB

This is normal and provides better features.

---

## 💡 Tips

1. **Drag & Drop**: Works in both Basic and Advanced modes
2. **Keyboard Shortcuts**: Enter to transcribe, Esc to cancel dialogs
3. **Window Resizing**: Minimum 1000x700, but resizable
4. **Cards Expand**: Content adjusts to window size
5. **Status Bar**: Always shows current operation

---

## 📚 Documentation

- **Qt Documentation**: https://doc.qt.io/qtforpython/
- **PySide6 Examples**: https://doc.qt.io/qtforpython/examples/index.html
- **Video2Text Docs**: See README_ENHANCED.md

---

## 🎉 Enjoy the Modern Interface!

The Qt version provides a professional, polished experience while maintaining all the powerful features of Video2Text.

**Questions?** Check the logs or open an issue!

---

*Made with ❤️ using PySide6 (Qt for Python)*
