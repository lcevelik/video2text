# Comprehensive List of Translation Strings for FonixFlow

This document contains all English source strings found in `self.tr()` calls throughout the Python source code that should appear in `.ts` translation files.

## Summary
- **Total unique translated strings identified**: 115+
- **Source files analyzed**:
  - `/home/user/video2text/gui/main_window.py`
  - `/home/user/video2text/gui/dialogs.py`
  - `/home/user/video2text/gui/widgets.py`
  - `/home/user/video2text/gui/workers.py`

---

## 1. Main Window Strings (`main_window.py`)

### Window Title
- `"FonixFlow - Whisper Transcription"`

### Menu Items
- `"⚙️ Settings"`
- `"🎨 Theme"`
- `"🔄 Auto (System)"`
- `"☀️ Light"`
- `"🌙 Dark"`
- `"📁 Change Recording Directory"`
- `"🗂️ Open Recording Directory"`
- `"🔄 New Transcription"`

### Tab Labels
- `"Record"`
- `"Upload"`
- `"Transcript"`
- `"Settings"`

### Settings Section Headers
- `"⚙️ Recordings Settings"`
- `"Recordings save to:"`
- `"Quick Actions"`
- `"Settings Sections"`
- `"🎙️ Audio Processing"`
- `"📝 Transcription"`
- `"▼ ⚙️ Settings"` (expanded state)
- `"▶ ⚙️ Settings"` (collapsed state)
- `"  ▼ 🎙️ Audio Processing"` (expanded state, indented)
- `"  ▼ 📝 Transcription"` (expanded state, indented)

### Settings Options
- `"Enhance Audio"`
- `"Deep Scan"`

### Action Buttons
- `"New Transcription"`
- `"📂 Change Folder"`
- `"Change Folder"`
- `"🗂️ Open Folder"`
- `"Open Folder"`
- `"Start Recording"`
- `"🎤 Start Recording"`
- `"🔴 Start Recording"`
- `"Stop Recording"`
- `"⏹️ Stop Recording"`
- `"Transcribe Recording"`
- `"💾 Save Transcription"`
- `"✖ Cancel Transcription"`

### Status Messages
- `"Ready"`
- `"Ready to record"`
- `"Ready to transcribe"`
- `"Ready for new transcription"`
- `"Recording in progress..."`
- `"Processing recording..."`
- `"🔴 Recording from Microphone + Speaker..."`
- `"Starting…"`

### Recording-related
- `"00:00:00"`
- `"Microphone"`
- `"Speaker"`
- `"Recording will use the system's default microphone and audio output."`

### Upload/Transcription
- `"Drag and drop video/audio file"`
- `"Transcription text will appear here..."`

### Info Messages
- `"💡 Files automatically transcribe when dropped or selected"`
- `"💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click 'Transcribe Recording' to manually start transcription"`

### File Dialog Strings
- `"Select Video or Audio File"`
- `"Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)"`
- `"Select Recordings Folder"`
- `"Save Transcription"`
- `"Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)"`

### Message Box Titles and Content
- `"No Microphone Found"`
- `"No audio input device detected!"`
- `"Device Found"`
- `"No Recording"`
- `"No File"`
- `"No Transcription"`
- `"Settings Updated"`
- `"Could Not Open Folder"`
- `"Saved Successfully"`
- `"Save Error"`
- `"Transcription Error"`
- `"Unknown"` (used in status messages)

### Dynamic Strings (f-strings)
Note: These contain variables that will be replaced at runtime
- `f"🎙️ Audio Setup Guide for {platform_display}"`
- `f"Switched to {tab_names.get(index, self.tr('Unknown'))} tab"`

---

## 2. Dialog Strings (`dialogs.py`)

### Recording Dialog
- `"Audio Recording"`
- `"🎤 Audio Recording"`
- `"3a4 Audio Recording"` (appears to be a specific card title)
- `"What will be recorded:"`
- `"🎤 Microphone: Your voice and ambient sounds"`
- `"🔊 Speaker: System audio, music, video calls"`
- `"📝 Both sources mixed into one recording"`
- `"Ready to record"`
- `"Duration: 0:00"`
- `"🔴 Start Recording"`
- `"⏹️ Stop Recording"`
- `"Close"`
- `"💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured."`
- `"⏹️ Stopping recording..."`
- `"🎤 Microphone"`
- `"🔊 Speaker/System"`

### Multi-Language Choice Dialog
- `"Language Mode"`
- `"Is your file multi-language?"`
- `"Select language type:"`
- `"English (uses optimized .en model)"`
- `"Other language (uses multilingual model)"`
- `"Select one language type before confirming."`
- `"Select languages present (check all that apply):"`
- `"At least one language must be selected before confirming."`
- `"Multi-Language"`
- `"Single-Language"`
- `"Confirm Languages"`
- `"Confirm Selection"`
- `"Cancel to decide later."`
- `"No Languages Selected"`
- `"No Language Type Selected"`
- `"Please select either English or Other language."`

### Language Names (for checkboxes)
- `"English"`
- `"Czech"`
- `"German"`
- `"French"`
- `"Spanish"`
- `"Italian"`
- `"Polish"`
- `"Russian"`
- `"Chinese"`
- `"Japanese"`
- `"Korean"`
- `"Arabic"`

---

## 3. Widgets Strings (`widgets.py`)

### DropZone Widget
- `"Drag and drop video/audio file"`

---

## 4. Workers Strings (`workers.py`)

### Transcription Progress Messages
- `"Extracting audio..."`
- `"Transcribing..."`
- `"Finishing up..."`
- `"Finalizing transcription..."`
- `"Transcription complete!"`

---

## 5. Strings Currently NOT Translated (Found in Code)

These strings appear in the UI but are **NOT** currently wrapped in `self.tr()` and should be considered for translation:

### From dialogs.py:
- `"🔴 Recording from Microphone + Speaker..."` (line 125 - hardcoded)
- `f"Duration: {mins}:{secs:02d}"` (line 166 - dynamic)
- `"Please:\n1. Connect a microphone\n2. Check your audio settings\n3. Make sure device is enabled\n\nClick 'Retry' to check again, or 'Cancel' to go back."` (lines 184-188)
- `"Device Found"` (line 201 - used in dialogs.py but not in main_window.py)
- `"✅ Audio input device detected!\n\nYou can now start recording."` (line 202)
- `f"✅ Recording complete ({duration:.1f}s)"` (line 213)
- `f"❌ Error: {error_message}"` (line 220)
- `"Select at least one language to proceed."` (line 357)

### From main_window.py:
- `"Please:\n1. Connect a microphone\n2. Check your audio settings\n3. Make sure device is enabled\n\nClick 'Retry' to check again, or 'Cancel' to go back."` (lines 1362-1366)
- `"✅ Audio input device detected!\n\nYou can now start recording."` (line 1380)
- `"No recording available. Please record first."` (line 1161)
- `"Please select a file first."` (line 1706)
- `"Please transcribe a file first."` (line 1831)
- Various dynamic status messages with formatting

---

## 6. Organization by Context

### Audio Recording Context
- Microphone/Speaker labels
- Recording status messages
- Duration displays
- VU meter labels

### Transcription Context
- Progress messages
- Model selection
- Language detection
- File format options

### UI Navigation
- Tab labels
- Menu items
- Button labels
- Settings sections

### Dialogs & Messages
- Error messages
- Confirmation dialogs
- Information messages
- Success messages

---

## Notes for Translation

1. **Emoji Handling**: Many strings contain emojis (🎙️, 📁, 🔄, etc.). Translators should preserve these emojis in their positions unless culturally inappropriate.

2. **Newline Characters**: Some strings contain `\n` for line breaks. These should be preserved in translations.

3. **Dynamic Content**: Strings with `{variable}` placeholders (f-strings) need special handling to ensure variables are properly placed in translated text.

4. **File Filters**: File filter strings like `"*.mp4 *.avi"` should generally not be translated, only the descriptive labels.

5. **Technical Terms**: Terms like "VU Meter", "Whisper", "ScreenCaptureKit" are proper nouns and should not be translated.

6. **Context Sensitivity**: Some strings like "Ready" appear in multiple contexts and may need different translations based on usage.

---

## Recommended Actions

1. **Add missing `self.tr()` calls** to the untranslated strings listed in Section 5
2. **Update all `.ts` translation files** with the complete list of source strings
3. **Review existing translations** to ensure they match the current source strings
4. **Test translations** in the UI to ensure proper text flow and layout
5. **Consider context comments** for ambiguous strings to help translators
