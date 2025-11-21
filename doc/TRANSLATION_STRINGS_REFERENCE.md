# FonixFlow Translation Strings - Complete Reference

**Generated**: 2025-11-21
**Purpose**: Complete list of all English source strings that should appear in `.ts` translation files

---

## Summary

- **Total strings currently in .ts files**: ~105
- **Total strings found in source code**: ~130+
- **Missing strings identified**: ~25+
- **Source files analyzed**:
  - `gui/main_window.py` (FonixFlowQt class)
  - `gui/dialogs.py` (RecordingDialog, MultiLanguageChoiceDialog classes)
  - `gui/widgets.py` (DropZone class)
  - `gui/workers.py` (TranscriptionWorker class)

---

## Complete List of Source Strings (Alphabetical)

This is the definitive list of ALL strings that should appear in `.ts` translation files:

```
  ▼ 🎙️ Audio Processing
  ▼ 📝 Transcription
00:00:00
3a4 Audio Recording
Arabic
At least one language must be selected before confirming.
Audio Recording
Cancel to decide later.
Change Folder
Chinese
Close
Confirm Languages
Confirm Selection
Could Not Open Folder
Czech
Deep Scan
Device Found
Drag and drop video/audio file
Duration: 0:00
English
English (uses optimized .en model)
Enhance Audio
Extracting audio...
Finalizing transcription...
Finishing up...
FonixFlow - Whisper Transcription
French
German
Is your file multi-language?
Italian
Japanese
Korean
Language Mode
Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)
Microphone
Multi-Language
New Transcription
No File
No Language Type Selected
No Languages Selected
No Microphone Found
No Recording
No Transcription
No audio input device detected!
No recording available. Please record first.
Open Folder
Other language (uses multilingual model)
Please select a file first.
Please select either English or Other language.
Please transcribe a file first.
Polish
Processing recording...
Quick Actions
Ready
Ready for new transcription
Ready to record
Ready to transcribe
Record
Recording in progress...
Recording will use the system's default microphone and audio output.
Recordings save to:
Russian
Save Error
Save Transcription
Saved Successfully
Select Recordings Folder
Select Video or Audio File
Select at least one language to proceed.
Select language type:
Select languages present (check all that apply):
Select one language type before confirming.
Settings
Settings Sections
Settings Updated
Single-Language
Spanish
Speaker
Start Recording
Starting…
Stop Recording
Switched to {tab_names.get(index, self.tr('Unknown'))} tab
Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)
Transcribe Recording
Transcribing...
Transcript
Transcription Error
Transcription complete!
Transcription text will appear here...
Unknown
Upload
What will be recorded:
⏹️ Stop Recording
⏹️ Stopping recording...
▶ ⚙️ Settings
▼ ⚙️ Settings
☀️ Light
⚙️ Recordings Settings
⚙️ Settings
✖ Cancel Transcription
🌙 Dark
🎙️ Audio Processing
🎙️ Audio Setup Guide for {platform_display}
🎤 Audio Recording
🎤 Microphone
🎤 Microphone: Your voice and ambient sounds
🎤 Start Recording
🎨 Theme
💡 After stopping, the recording is saved but NOT automatically transcribed
💡 Click 'Transcribe Recording' to manually start transcription
💡 Files automatically transcribe when dropped or selected
💡 Perfect for video calls, meetings, or any scenario where you need both
your voice and system audio captured.
💾 Save Transcription
📁 Change Recording Directory
📂 Change Folder
📝 Both sources mixed into one recording
📝 Transcription
🔄 Auto
🔄 Auto (System)
🔄 New Transcription
🗂️ Open Folder
🗂️ Open Recording Directory
🔊 Speaker/System
🔊 Speaker: System audio, music, video calls
🔴 Recording from Microphone + Speaker...
🔴 Start Recording
```

**Total Count**: 130 unique strings

---

## Strings MISSING from Current .ts Files

These strings are used in the code with `self.tr()` but are **NOT** present in the current `.ts` translation files:

### From TranscriptionWorker (gui/workers.py)
```
❌ Extracting audio...
❌ Transcribing...
❌ Finishing up...
❌ Finalizing transcription...
❌ Transcription complete!
```

### Language Names (gui/dialogs.py)
```
❌ Czech
❌ German
❌ French
❌ Spanish
❌ Italian
❌ Polish
❌ Russian
❌ Chinese
❌ Japanese
❌ Korean
❌ Arabic
```

### UI Elements (gui/main_window.py)
```
❌ Settings
❌ Settings Sections
❌ Quick Actions
❌ 📝 Transcription
❌ 📂 Change Folder
❌ 🗂️ Open Folder
❌ 🗂️ Open Recording Directory
❌ Unknown
```

### Dialog Strings (gui/dialogs.py)
```
❌ 3a4 Audio Recording
```

**Total Missing**: 25 strings

---

## Organization by Context/Class

### Context: FonixFlowQt (main_window.py)
**Count**: ~80 strings

Main application window strings including:
- Window title
- Menu items (Settings, Theme, etc.)
- Tab labels (Record, Upload, Transcript, Settings)
- Status messages
- Button labels
- File dialog filters
- Message box content

### Context: RecordingDialog (dialogs.py)
**Count**: ~20 strings

Recording dialog strings including:
- Dialog title
- Recording status messages
- Button labels
- Information messages
- VU meter labels

### Context: MultiLanguageChoiceDialog (dialogs.py)
**Count**: ~30 strings

Multi-language selection dialog including:
- Language names (12 languages)
- Dialog prompts
- Button labels
- Validation messages
- Helper text

### Context: DropZone (widgets.py)
**Count**: 1 string

- "Drag and drop video/audio file"

### Context: TranscriptionWorker (workers.py) ⚠️ MISSING
**Count**: 5 strings

Progress update messages:
- "Extracting audio..."
- "Transcribing..."
- "Finishing up..."
- "Finalizing transcription..."
- "Transcription complete!"

---

## Strings by Category

### Window/App Level
- FonixFlow - Whisper Transcription

### Navigation (Tabs)
- Record
- Upload
- Transcript
- Settings

### Menus
- ⚙️ Settings
- 🎨 Theme
- 🔄 Auto (System)
- ☀️ Light
- 🌙 Dark
- 📁 Change Recording Directory
- 🗂️ Open Recording Directory
- 🔄 New Transcription

### Settings Sections
- ⚙️ Recordings Settings
- 🎙️ Audio Processing
- 📝 Transcription
- Settings Sections
- Quick Actions
- Recordings save to:
- Enhance Audio
- Deep Scan

### Buttons - Primary Actions
- Start Recording
- 🎤 Start Recording
- 🔴 Start Recording
- Stop Recording
- ⏹️ Stop Recording
- Transcribe Recording
- 💾 Save Transcription
- ✖ Cancel Transcription
- 🔄 New Transcription

### Buttons - File Operations
- Change Folder
- 📂 Change Folder
- Open Folder
- 🗂️ Open Folder
- 🗂️ Open Recording Directory

### Buttons - Dialogs
- Close
- Confirm Languages
- Confirm Selection
- Multi-Language
- Single-Language

### Status Messages
- Ready
- Ready to record
- Ready to transcribe
- Ready for new transcription
- Recording in progress...
- Processing recording...
- ⏹️ Stopping recording...
- 🔴 Recording from Microphone + Speaker...
- Starting…

### Progress Messages (Transcription)
- Extracting audio...
- Transcribing...
- Finishing up...
- Finalizing transcription...
- Transcription complete!

### Audio/Recording Related
- Microphone
- Speaker
- 🎤 Microphone
- 🔊 Speaker/System
- Duration: 0:00
- 00:00:00
- Audio Recording
- 🎤 Audio Recording
- 3a4 Audio Recording
- Recording will use the system's default microphone and audio output.

### Recording Dialog - Info Messages
- What will be recorded:
- 🎤 Microphone: Your voice and ambient sounds
- 🔊 Speaker: System audio, music, video calls
- 📝 Both sources mixed into one recording

### UI Placeholders & Drop Zones
- Drag and drop video/audio file
- Transcription text will appear here...

### Language Selection
- Language Mode
- Is your file multi-language?
- Select language type:
- Select languages present (check all that apply):
- English (uses optimized .en model)
- Other language (uses multilingual model)
- At least one language must be selected before confirming.
- Select one language type before confirming.
- Cancel to decide later.

### Language Names
- English
- Czech
- German
- French
- Spanish
- Italian
- Polish
- Russian
- Chinese
- Japanese
- Korean
- Arabic

### File Dialogs
- Select Video or Audio File
- Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)
- Select Recordings Folder
- Save Transcription
- Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)

### Message Boxes - Titles
- No Microphone Found
- No Recording
- No File
- No Transcription
- No Languages Selected
- No Language Type Selected
- Device Found
- Settings Updated
- Could Not Open Folder
- Saved Successfully
- Save Error
- Transcription Error

### Message Boxes - Content
- No audio input device detected!
- No recording available. Please record first.
- Please select a file first.
- Please transcribe a file first.
- Select at least one language to proceed.
- Please select either English or Other language.

### Info/Help Messages
- 💡 Files automatically transcribe when dropped or selected
- 💡 After stopping, the recording is saved but NOT automatically transcribed
- 💡 Click 'Transcribe Recording' to manually start transcription
- 💡 Perfect for video calls, meetings, or any scenario where you need both
your voice and system audio captured.

### Collapsible Sections
- ▼ ⚙️ Settings (expanded)
- ▶ ⚙️ Settings (collapsed)
- ▼ 🎙️ Audio Processing (expanded)
- ▼ 📝 Transcription (expanded)

### Dynamic Strings (with variables)
- 🎙️ Audio Setup Guide for {platform_display}
- Switched to {tab_names.get(index, self.tr('Unknown'))} tab
- Unknown (fallback text)

---

## Translation Guidelines

### 1. Emoji Preservation
- **Keep emojis in the same position** unless culturally inappropriate
- Examples: 🎙️, 📁, 🔄, ⚙️, 💡, etc.

### 2. Newline Characters
- Preserve `\n` characters for line breaks
- Example: `"💡 After stopping...\n💡 Click 'Transcribe Recording'..."`

### 3. File Filters
- **Do NOT translate** file extensions: `*.mp4`, `*.wav`, etc.
- **DO translate** descriptive labels: `"Media Files"` → `"Fichiers Médias"`
- Example: `"Media Files (*.mp4 *.avi)"` → `"Fichiers Médias (*.mp4 *.avi)"`

### 4. Dynamic Placeholders
- Keep placeholder syntax intact: `{variable_name}`
- Example: `"Guide for {platform_display}"` → `"Guide pour {platform_display}"`

### 5. Button States
- Some buttons have multiple states with different icons:
  - Start: `"Start Recording"`, `"🎤 Start Recording"`, `"🔴 Start Recording"`
  - Stop: `"Stop Recording"`, `"⏹️ Stop Recording"`
- Translate the text part, keep the emoji

### 6. Technical Terms
- **Do NOT translate**: Whisper, FonixFlow, VU Meter, ScreenCaptureKit
- **DO translate**: Transcription, Recording, Settings, etc.

### 7. Ellipsis Usage
- `"..."` indicates ongoing action: `"Recording..."`, `"Processing..."`
- `"…"` (single character) also used: `"Starting…"`
- Preserve the style used in the source

### 8. Arrow Characters
- `▼` = expanded/open state
- `▶` = collapsed/closed state
- These are UI indicators, keep them in position

### 9. Indentation Spaces
- Some strings have leading spaces for visual hierarchy:
  - `"  ▼ 🎙️ Audio Processing"` (2 spaces = nested item)
- Preserve leading spaces

### 10. Context Sensitivity
Some strings appear in multiple contexts:
- `"Ready"` - general status
- `"Ready to record"` - specific recording context
- `"Ready to transcribe"` - specific transcription context

Translate appropriately for each context.

---

## Verification Checklist

When updating `.ts` files, ensure:

- [ ] All 130 source strings are present
- [ ] All 5 TranscriptionWorker strings are added
- [ ] All 12 language names are added
- [ ] Settings-related strings are complete
- [ ] File dialog strings include proper filters
- [ ] Emoji positions are preserved
- [ ] Newline characters (`\n`) are intact
- [ ] Dynamic placeholders (`{variable}`) are preserved
- [ ] File extensions are not translated
- [ ] Leading spaces for indentation are preserved
- [ ] Both expanded (▼) and collapsed (▶) states exist

---

## Files to Update

All `.ts` files in the `i18n/` directory should be updated:

- `i18n/fonixflow_cs.ts` (Czech)
- `i18n/fonixflow_ar.ts` (Arabic)
- `i18n/fonixflow_es.ts` (Spanish)
- `i18n/fonixflow_de.ts` (German)
- `i18n/fonixflow_it.ts` (Italian)
- `i18n/fonixflow_fr.ts` (French)
- `i18n/fonixflow_ko.ts` (Korean)
- `i18n/fonixflow_pl.ts` (Polish)
- `i18n/fonixflow_ja.ts` (Japanese)
- `i18n/fonixflow_zh_CN.ts` (Chinese Simplified)
- `i18n/fonixflow_ru.ts` (Russian)
- `i18n/fonixflow_pt_BR.ts` (Portuguese Brazilian)

---

## Next Steps

1. **Update translation template**: Run `pylupdate6` or `create_translation_templates.py` to regenerate `.ts` files with all source strings
2. **Add missing contexts**: Ensure TranscriptionWorker context is included
3. **Translate missing strings**: Focus on the 25 identified missing strings
4. **Verify consistency**: Check that all `.ts` files have the same source strings
5. **Compile translations**: Run `lrelease` or `compile_translations.py` to generate `.qm` files
6. **Test in application**: Verify translations display correctly in all contexts

---

## Source File Locations

**Main Window**: `/home/user/video2text/gui/main_window.py`
- Class: `FonixFlowQt`
- Context name in .ts: `FonixFlowQt`

**Dialogs**: `/home/user/video2text/gui/dialogs.py`
- Class: `RecordingDialog` → Context: `RecordingDialog`
- Class: `MultiLanguageChoiceDialog` → Context: `MultiLanguageChoiceDialog`

**Widgets**: `/home/user/video2text/gui/widgets.py`
- Class: `DropZone` → Context: `DropZone`

**Workers**: `/home/user/video2text/gui/workers.py`
- Class: `TranscriptionWorker` → Context: `TranscriptionWorker` (⚠️ currently missing from .ts files)

---

*End of Reference Document*
