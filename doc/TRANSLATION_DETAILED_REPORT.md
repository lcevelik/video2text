# FonixFlow Application - Translation Analysis Report

## Executive Summary

**Framework:** Qt (PySide6)
**Application Name:** FonixFlow - Whisper Transcription
**Main GUI File:** `/home/user/video2text/gui/main_window.py`
**Total User-Facing Text Strings:** 100+ unique strings requiring translation
**Language Support:** Currently English only
**Architecture:** Modern Qt-based GUI with modular components

---

## Application Architecture

### Technology Stack
- **GUI Framework:** PySide6/Qt6
- **Primary Language:** Python 3.7+
- **Main Components:**
  - Main Window (`gui/main_window.py`)
  - Dialogs (`gui/dialogs.py`)
  - Custom Widgets (`gui/widgets.py`)
  - Workers/Threading (`gui/workers.py`)
  - Utilities (`gui/utils.py`)
  - Theme System (`gui/theme.py`)

### Application Structure

**Three Main Tabs:**
1. **Record Tab** (🎙️) - Record audio from microphone and system
2. **Upload Tab** (📁) - Drag & drop files for transcription
3. **Transcript Tab** (📄) - View and save transcription results

**Sidebars:**
- Left Collapsible Sidebar: Navigation actions
- Right Settings Sidebar: Theme and settings
- Top Bar: FonixFlow logo

---

## Complete User-Facing Text String List

### Main Window Titles and Labels

| String | Location | Context |
|--------|----------|---------|
| FonixFlow - Whisper Transcription | main_window.py:38 | Application window title |
| Ready | main_window.py:428, 1824 | Initial status bar message |
| Ready to transcribe | main_window.py:882 | Upload tab progress label |
| Ready to record | main_window.py:954 | Record tab progress label |
| Recordings save to: | main_window.py:532 | Settings card label |

### Tab Names and Buttons

| String | Location | Context |
|--------|----------|---------|
| Record | main_window.py:626, 855, 1867 | Tab button/label |
| Upload | main_window.py:627, 856, 1867 | Tab button/label |
| Transcript | main_window.py:628, 857, 1867 | Tab button/label |
| Start Recording | main_window.py:933 | Record button initial text |
| Stop Recording | main_window.py:1208 | Record button during recording |
| 🎤 Start Recording | main_window.py:1350 | Record button after error |
| Transcribe Recording | main_window.py:970 | Button to start manual transcription |
| 💾 Save Transcription | main_window.py:1019 | Save results button |
| ✖ Cancel Transcription | main_window.py:1025 | Cancel button during transcription |
| 📂 Change Folder | main_window.py:555 | Change recordings directory button |
| 🗂️ Open Folder | main_window.py:560 | Open recordings directory button |
| Close | main_window.py:1133, dialogs.py:89 | Close dialog button |

### Menu Items (Hamburger Menu)

| String | Location | Context |
|--------|----------|---------|
| ⚙️ Settings | main_window.py:465 | Main menu |
| 🎨 Theme | main_window.py:468 | Submenu under Settings |
| 🔄 Auto (System) | main_window.py:471 | Theme option |
| ☀️ Light | main_window.py:476 | Theme option |
| 🌙 Dark | main_window.py:481 | Theme option |
| 🔍 Enable Deep Scan (Slower) | main_window.py:488 | Settings toggle for deep language detection |
| 📁 Change Recording Directory | main_window.py:501 | Settings action |
| 🗂️ Open Recording Directory | main_window.py:504 | Settings action |
| 🔄 New Transcription | main_window.py:509 | Main menu action |

### Sidebar Actions (Collapsible Sidebar)

| String | Location | Context |
|--------|----------|---------|
| 🔄 New Transcription | main_window.py:587 | Sidebar action |
| 📂 Change Recordings Folder | main_window.py:589 | Sidebar action |
| 🗂️ Open Recordings Folder | main_window.py:590 | Sidebar action |

### Settings Section (Right Sidebar)

| String | Location | Context |
|--------|----------|---------|
| ▼ ⚙️ Settings | main_window.py:801 | Settings section header (expanded) |
| ▶ ⚙️ Settings | main_window.py:804 | Settings section header (collapsed) |
| ▼ 🎨 Theme | main_window.py:814 | Theme subsection header (expanded) |
| ▶ 🎨 Theme | main_window.py:817 | Theme subsection header (collapsed) |
| 🔄 Auto | main_window.py:759 | Theme option in sidebar |
| ☀️ Light | main_window.py:760 | Theme option in sidebar |
| 🌙 Dark | main_window.py:761 | Theme option in sidebar |

### Informational Text and Tips

| String | Location | Context |
|--------|----------|---------|
| Recording will use the system's default microphone and audio output. | main_window.py:909 | Info label on Record tab |
| 💡 Files automatically transcribe when dropped or selected | main_window.py:892 | Tip on Upload tab |
| 💡 After stopping, the recording is saved but NOT automatically transcribed\n💡 Click 'Transcribe Recording' to manually start transcription | main_window.py:964 | Tip on Record tab |
| Transcription text will appear here... | main_window.py:1003 | Placeholder text in results area |
| Duration: 0:00 | main_window.py:943, dialogs.py:79 | Recording duration display |

### VU Meter Labels

| String | Location | Context |
|--------|----------|---------|
| Microphone | main_window.py:920, dialogs.py:67 | Mic level meter label |
| Speaker | main_window.py:921, dialogs.py:68 | Speaker level meter label |

### Recording Status Messages

| String | Location | Context |
|--------|----------|---------|
| 🔴 Recording from Microphone + Speaker... | main_window.py:1232 | Status during active recording |
| Recording in progress... | main_window.py:1233 | Progress label during recording |
| Processing recording... | main_window.py:1279 | Status after stopping recording |
| ✅ Recording complete ({duration:.1f}s). File saved. | main_window.py:1322 | Status after successful recording |
| Recording complete ({duration:.1f}s). Ready for manual transcription. | main_window.py:1328 | Progress label after recording ends |

### Transcription Progress and Status

| String | Location | Context |
|--------|----------|---------|
| Starting… | main_window.py:1437 | Status when transcription begins |
| Loading Whisper model ({model_size})... | workers.py:340 | Model loading progress |
| Extracting audio... | workers.py:310 | Audio extraction progress |
| Transcribing... | workers.py:383 | Active transcription progress |
| Finishing up... | workers.py:460 | Finalization stage |
| Finalizing transcription... | workers.py:462 | Final stage |
| Transcription complete! | workers.py:466 | Completion message |
| ✅ Complete! {lang_info} | main_window.py:1746, 1750 | Progress labels after transcription |
| {current_pct}% \| Elapsed {elapsed_str} \| ETA {eta_str} | main_window.py:1610 | Performance overlay display |
| Finished in {total:.2f}s (RTF {rtf:.2f}) | main_window.py:1730 | Final performance stats |
| Model: {model_size} | main_window.py:1487 | Display current model in use |

### Transcription Results Labels

| String | Location | Context |
|--------|----------|---------|
| Language: {lang_name} \| {segment_count} segments | main_window.py:1736 | Single-language result summary |
| {lang_info} \| {segment_count} segments | main_window.py:1734 | Multi-language result summary |
| Languages detected: {langs} | main_window.py:1687 | Multi-language info |

### Dialog Windows

#### Recording Dialog
| String | Location | Context |
|--------|----------|---------|
| Audio Recording | dialogs.py:29 | Dialog window title |
| 🎤 Audio Recording | dialogs.py:43 | Dialog title label |
| What will be recorded: | dialogs.py:50 | Info section header |
| 🎤 Microphone: Your voice and ambient sounds | dialogs.py:51 | Description |
| 🔊 Speaker: System audio, music, video calls | dialogs.py:52 | Description |
| 📝 Both sources mixed into one recording | dialogs.py:53 | Description |
| 🔴 Start Recording | dialogs.py:86 | Start button |
| ⏹️ Stop Recording | dialogs.py:87 | Stop button |
| 💡 Perfect for video calls, meetings, or any scenario where you need both\nyour voice and system audio captured. | dialogs.py:101 | Dialog tip text |
| ⏹️ Stopping recording... | dialogs.py:152 | Status during stop |
| ✅ Recording complete ({duration:.1f}s) | dialogs.py:213 | Success status |

#### Language Mode Dialog
| String | Location | Context |
|--------|----------|---------|
| Language Mode | dialogs.py:232 | Dialog window title |
| Is your file multi-language? | dialogs.py:240 | Main question |
| Select language type: | dialogs.py:248 | Single-language section header |
| English (uses optimized .en model) | dialogs.py:253 | Checkbox label |
| Other language (uses multilingual model) | dialogs.py:258 | Checkbox label |
| Select one language type before confirming. | dialogs.py:265 | Hint text |
| Select languages present (check all that apply): | dialogs.py:274 | Multi-language section header |
| At least one language must be selected before confirming. | dialogs.py:292 | Hint text |
| English | dialogs.py:279 | Language option |
| Czech | dialogs.py:279 | Language option |
| German | dialogs.py:279 | Language option |
| French | dialogs.py:279 | Language option |
| Spanish | dialogs.py:279 | Language option |
| Italian | dialogs.py:279 | Language option |
| Polish | dialogs.py:279 | Language option |
| Russian | dialogs.py:279 | Language option |
| Chinese | dialogs.py:279 | Language option |
| Japanese | dialogs.py:279 | Language option |
| Korean | dialogs.py:279 | Language option |
| Arabic | dialogs.py:279 | Language option |
| Multi-Language | dialogs.py:298 | Button text (initial) |
| Confirm Languages | dialogs.py:352 | Button text (after selection) |
| Single-Language | dialogs.py:299 | Button text (initial) |
| Confirm Selection | dialogs.py:368 | Button text (after selection) |
| Cancel to decide later. | dialogs.py:338 | Hint text |

### File Dialogs

| String | Location | Context |
|--------|----------|---------|
| Select Video or Audio File | main_window.py:1043 | File open dialog title |
| Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*) | main_window.py:1045 | File filter |
| Select Recordings Folder | main_window.py:1363 | Folder selection dialog title |
| Save Transcription | main_window.py:1549 | File save dialog title |
| Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt) | main_window.py:1551 | Save format options |

### Audio Setup Help Dialog

| String | Location | Context |
|--------|----------|---------|
| Audio Setup Guide - {platform_display} | main_window.py:1105 | Dialog title |
| 🎙️ Audio Setup Guide for {platform_display} | main_window.py:1111 | Dialog header label |
| ## Microphone Setup | main_window.py:1095 | Section header |
| ## System Audio / YouTube Capture Setup | main_window.py:1100 | Section header |

### Message Boxes

#### No Microphone / Device Errors
| String | Location | Context |
|--------|----------|---------|
| No Microphone Found | main_window.py:1173, dialogs.py:181 | Message box title |
| No audio input device detected! | main_window.py:1174, dialogs.py:182 | Message text |
| Please:\n1. Connect a microphone\n2. Check your audio settings\n3. Make sure device is enabled\n\nClick 'Retry' to check again, or 'Cancel' to go back. | main_window.py:1176 | Detailed instructions |
| Device Found | main_window.py:1193 | Message box title |
| ✅ Audio input device detected!\n\nYou can now start recording. | main_window.py:1194 | Success message |

#### File/Transcription Errors
| String | Location | Context |
|--------|----------|---------|
| No Recording | main_window.py:975 | Message box title |
| No recording available. Please record first. | main_window.py:975 | Message text |
| No File | main_window.py:1420 | Message box title |
| Please select a file first. | main_window.py:1420 | Message text |
| No Transcription | main_window.py:1544 | Message box title |
| Please transcribe a file first. | main_window.py:1544 | Message text |

#### Language Selection Errors
| String | Location | Context |
|--------|----------|---------|
| No Languages Selected | dialogs.py:357 | Message box title |
| Select at least one language to proceed. | dialogs.py:357 | Message text |
| No Language Type Selected | dialogs.py:372 | Message box title |
| Please select either English or Other language. | dialogs.py:372 | Message text |

#### Save/Success Messages
| String | Location | Context |
|--------|----------|---------|
| Saved Successfully | main_window.py:1568 | Message box title |
| Transcription saved to:\n{file_path} | main_window.py:1568 | Message text |
| Settings Updated | main_window.py:1379 | Message box title |
| Recordings will now be saved to:\n{new_dir} | main_window.py:1379 | Message text |

#### Error Messages
| String | Location | Context |
|--------|----------|---------|
| Save Error | main_window.py:1572 | Message box title |
| Failed to save transcription:\n\n{e} | main_window.py:1572 | Error details |
| Could Not Open Folder | main_window.py:1407 | Message box title |
| Please navigate manually to:\n{recordings_dir} | main_window.py:1407 | Help text |
| Transcription Error | main_window.py:1784 | Message box title |
| Transcription failed:\n\n{error_message}\n\nPlease check the logs for more details. | main_window.py:1784 | Error details |

### Drop Zone Widget

| String | Location | Context |
|--------|----------|---------|
| Drag and drop video/audio file | widgets.py:126, 183 | Drop zone prompt |
| ✓ {filename} | widgets.py:177 | File selected indicator |

### Performance Metrics

| String | Location | Context |
|--------|----------|---------|
| {percent}% | widgets.py:261 | VU meter percentage |

---

## Translation Statistics

### By Category

| Category | Count | Examples |
|----------|-------|----------|
| Button Labels | 15 | Start Recording, Save Transcription, Close |
| Menu Items | 9 | Settings, Theme, Auto, Light, Dark |
| Dialog Titles | 6 | Audio Recording, Language Mode, Audio Setup Guide |
| Status Messages | 12 | Recording in progress, Transcription complete |
| Error Messages | 8 | No Microphone Found, Save Error |
| Informational Text | 8 | Tips, hints, descriptions |
| Tab/Section Headers | 10 | Record, Upload, Transcript, Settings |
| Language Options | 12 | English, French, Spanish, etc. |
| File Dialog Labels | 5 | Select Video or Audio File, Media Files |
| Placeholders | 2 | Transcription text will appear here |

### Total Unique Strings: 87

### Breakdown by Priority

**HIGH PRIORITY (Core Functionality):**
- Window titles
- Tab names
- Recording/Transcription status
- Critical error messages
- Button labels

**MEDIUM PRIORITY (User Guidance):**
- Informational tips
- Dialog instructions
- Help text
- Settings labels

**LOW PRIORITY (Utility):**
- Debug messages
- Advanced settings
- Optional preferences

---

## Current Translation Infrastructure

**Status:** No existing translation system found
**Framework Support:** PySide6 supports Qt translation system (`.ts` and `.qm` files)
**Locale Configuration:** No locale-specific strings found

---

## Recommendations for Localization

### 1. Recommended Approach
- Use Qt's `QTranslator` and `.ts` files for translation
- Create translation files for each supported language
- Use `.lupdate` tool to extract strings
- Use `.lrelease` tool to compile translations

### 2. Key Areas to Prioritize
1. User-facing messages and dialogs
2. Button and menu labels
3. Error messages
4. Help/instruction text
5. Status bar messages

### 3. Language Support Strategy
- Start with: Spanish, French, German, Chinese (Simplified)
- Then expand to: Japanese, Korean, Portuguese, Russian
- Platform-specific support recommended for help text

### 4. Technical Implementation
- Wrap all user strings with `QCoreApplication.translate()`
- Create `i18n/` directory for translation files
- Implement language switcher in settings
- Store language preference in config file

---

## File-by-File Translation Guide

### `/home/user/video2text/gui/main_window.py` (1875 lines)
- **Strings needing translation:** 45
- **Key areas:** Status messages, error dialogs, menu items, button labels

### `/home/user/video2text/gui/dialogs.py` (383 lines)
- **Strings needing translation:** 28
- **Key areas:** Dialog titles, language selection, recording instructions

### `/home/user/video2text/gui/widgets.py` (506 lines)
- **Strings needing translation:** 4
- **Key areas:** Drop zone prompts, button labels

### `/home/user/video2text/gui/workers.py` (491 lines)
- **Strings needing translation:** 6
- **Key areas:** Progress messages, status updates

### `/home/user/video2text/gui/utils.py` (439 lines)
- **Strings needing translation:** 4
- **Key areas:** Help text, audio setup instructions

---

## Application UI Flow for Translators

1. **Startup** → Window title, Ready status
2. **Tab Navigation** → Record, Upload, Transcript labels
3. **Recording** → Start/Stop buttons, duration display, progress messages
4. **File Selection** → File dialog, drag-drop prompts
5. **Language Selection** → Multi-language or single-language dialog
6. **Transcription** → Progress updates, model loading, extraction, transcribing
7. **Results** → Save dialog, success/error messages
8. **Settings** → Theme options, folder selection

---

## Special Considerations

### Emojis in UI
Many strings include emojis (🎙️, 📁, 📄, etc.) for visual clarity. These should be preserved in translations to maintain the visual design.

### Dynamic Content
Some strings contain placeholders (e.g., `{duration:.1f}s`, `{lang_name}`, `{percent}%`) that should not be translated.

### Platform-Specific Text
Help text varies by platform (Windows, macOS, Linux) and should be translated accordingly.

### Language Names
The language selection dialog includes 12 language names that should be translated to the target language.

