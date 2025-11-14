# Video2Text - Modern Qt Interface

## 🎨 Beautiful, User-Friendly GUI

This is the **modern Qt-based interface** for Video2Text, built with PySide6 for a polished, professional appearance across all platforms.

---

## ✨ Why Qt Version?

### **Modern Design**
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
- 🚀 **Smoother animations** - Professional feel
- 💡 **Better visual hierarchy** - Easy to understand
- 🎭 **Dark/Light themes** - Comfortable for any lighting

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

### **Basic Mode**
- 📁 **Drag & Drop** - Visual drop zone for files
- 🎤 **One-Click Recording** - Record mic + speaker
- ✨ **Auto Transcribe** - Single button to start
- 🤖 **Smart Model Selection** - Automatically chooses best model

### **Advanced Mode**
- ⚙️ **Full Control** - Manual model selection
- 🌍 **Language Options** - Choose specific language
- 📝 **Multiple Formats** - TXT, SRT, VTT output
- 🎛️ **Fine-Tuning** - All advanced options available

### **Modern UI Elements**
- 💳 **Cards** - Organized content sections
- 🎨 **Styled Buttons** - Primary/secondary styling
- 📊 **Smooth Progress** - Animated progress bars
- 🎬 **Drop Zone** - Visual file upload area
- 🔔 **Status Updates** - Clear feedback messages

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

## 📸 UI Components

### **1. Header**
```
🎬 Video2Text
AI-Powered Transcription with Whisper
```
Clean, professional branding

### **2. Mode Switcher**
```
[📱 Basic Mode] [⚙️ Advanced Mode]
```
Toggle between simple and advanced interfaces

### **3. Drop Zone (Basic Mode)**
```
┌────────────────────────────┐
│          🎬                │
│  Drag & Drop File Here     │
│    or click Browse         │
└────────────────────────────┘
```
Visual file upload area

### **4. Cards (Advanced Mode)**
```
┌─ Media File ───────────────┐
│  📁 No file selected       │
│  [Browse...]              │
└───────────────────────────┘

┌─ Whisper Model ────────────┐
│  ○ 🤖 Auto-select (✓)     │
│  ○ Manual selection        │
│  [tiny ▼]                  │
└───────────────────────────┘
```
Organized, easy-to-understand sections

### **5. Progress**
```
┌─ Progress ─────────────────┐
│  Transcribing audio...     │
│  ████████░░░░░ 75%        │
└───────────────────────────┘
```
Clear visual feedback

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
├── Header (title, subtitle)
├── Mode Switcher (basic/advanced)
├── Stacked Widget
│   ├── Basic Mode (DropZone, buttons)
│   └── Advanced Mode (Cards, controls)
├── Progress Section (label, bar)
├── Result Section (text edit, save)
└── Status Bar
```

### **Custom Widgets**
- `ModernButton` - Styled buttons with hover effects
- `Card` - Container with shadow and rounded corners
- `DropZone` - Drag-and-drop file upload area
- `RecordingDialog` - Modern recording interface

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

## 🔮 Future Enhancements

### **Planned Features**
- 🌓 **Dark Mode** - Toggle dark/light themes
- 🎨 **Custom Themes** - User-selectable color schemes
- 📊 **Real-time Waveform** - Visual audio feedback during recording
- 🎬 **Video Preview** - Thumbnail preview of video files
- 📈 **Statistics Dashboard** - Usage metrics and history
- 🔔 **Desktop Notifications** - Completion alerts
- 🌐 **Multi-language UI** - Interface in multiple languages
- 💾 **Settings Panel** - Persistent user preferences

### **Technical Improvements**
- ⚡ **Async Operations** - Non-blocking transcription
- 🔄 **Auto-updates** - Update checker
- 📦 **Smaller Packaging** - Optimized builds
- 🎯 **Accessibility** - Screen reader support

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
