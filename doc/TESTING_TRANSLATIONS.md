# Testing FonixFlow Translations

This guide explains how to test FonixFlow in different languages **without changing your system language**.

## Quick Start

### Option 1: Interactive Language Tester (Recommended)

The easiest way to test all languages:

```bash
python test_languages.py
```

This will show you a menu of all available languages with their translation status:
- ✓ Ready (compiled) - Has .qm file (fastest)
- ○ Ready (source) - Has .ts file with translations
- ✗ Template only - No translations yet (shows English)

Just select a number to launch the app in that language!

### Option 2: Command-Line Flags

Launch the app directly in any language:

```bash
# Spanish
python fonixflow_qt.py --lang es

# French
python fonixflow_qt.py --lang fr

# German
python fonixflow_qt.py --lang de

# Czech
python fonixflow_qt.py --lang cs

# Chinese (Simplified)
python fonixflow_qt.py --lang zh_CN

# Portuguese (Brazil)
python fonixflow_qt.py --lang pt_BR

# Any other language code
python fonixflow_qt.py --lang <code>
```

### Option 3: Default Behavior (No Flag)

Without `--lang`, the app automatically uses your system language:

```bash
python fonixflow_qt.py  # Uses system language
```

## Available Languages

### ✅ Fully Translated (Ready to Test)

These languages have complete translations with all 107 strings translated:

| Language | Code | Command |
|----------|------|---------|
| 🇪🇸 Spanish | es | `python fonixflow_qt.py --lang es` |
| 🇫🇷 French | fr | `python fonixflow_qt.py --lang fr` |
| 🇩🇪 German | de | `python fonixflow_qt.py --lang de` |
| 🇨🇿 Czech | cs | `python fonixflow_qt.py --lang cs` |

### ⏳ Templates Available (Need Translation)

These languages have template files ready but need translations:

- 🇨🇳 Chinese (Simplified) - zh_CN
- 🇯🇵 Japanese - ja
- 🇧🇷 Portuguese (Brazil) - pt_BR
- 🇷🇺 Russian - ru
- 🇰🇷 Korean - ko
- 🇮🇹 Italian - it
- 🇵🇱 Polish - pl
- 🇸🇦 Arabic - ar

## What to Test

When testing a language, verify these areas:

### 1. Main Window
- [ ] Window title
- [ ] Tab names (Record, Upload, Transcript)
- [ ] Status bar messages

### 2. Menus
- [ ] Settings menu (⚙️ Settings)
- [ ] Theme submenu (🎨 Theme)
- [ ] Theme options (Auto, Light, Dark)
- [ ] Recording directory options

### 3. Sidebars
- [ ] Left sidebar actions
- [ ] Right sidebar settings
- [ ] Collapsible section headers

### 4. Upload Tab
- [ ] Drag & drop text
- [ ] Progress messages
- [ ] Transcription button

### 5. Record Tab
- [ ] Start/Stop Recording button
- [ ] VU meter labels (Microphone, Speaker)
- [ ] Duration display
- [ ] Transcribe Recording button

### 6. Transcript Tab
- [ ] Save Transcription button
- [ ] Result display area

### 7. Dialogs
- [ ] Recording Dialog
  - Title
  - Instructions
  - What will be recorded
  - Start/Stop buttons
- [ ] Language Selection Dialog
  - Title
  - Question
  - Language options
  - Confirm buttons

### 8. Messages
- [ ] Error messages (try triggering without microphone)
- [ ] Success messages (save a transcription)
- [ ] Info messages

### 9. File Dialogs
- [ ] Open file dialog
- [ ] Save file dialog
- [ ] File type filters

## Testing Checklist

For each language you test:

1. **Launch the app:**
   ```bash
   python fonixflow_qt.py --lang <code>
   ```

2. **Verify console output:**
   ```
   Language override: es (using --lang flag)
   Translation loaded: /path/to/i18n/fonixflow_es.ts [source (.ts)]
   ```

3. **Check all UI elements:**
   - Navigate through all tabs
   - Open all dialogs
   - Trigger messages
   - Check tooltips

4. **Look for issues:**
   - [ ] Text too long (overflows)
   - [ ] Text too short (looks awkward)
   - [ ] Emojis missing
   - [ ] Placeholders translated (they shouldn't be)
   - [ ] Untranslated strings (still in English)

5. **Test functionality:**
   - All buttons work
   - Dialogs open/close properly
   - Messages display correctly

## Reporting Issues

If you find any issues:

1. **Translation errors:**
   - Note the English text
   - Note the incorrect translation
   - Where it appears in the UI

2. **Layout issues:**
   - Take a screenshot
   - Note which language
   - Describe the problem

3. **Untranslated strings:**
   - Note the English text
   - Where it appears
   - Which language you were testing

## Console Output Examples

### Successful Translation Load

```
2025-11-21 10:30:15 - __main__ - INFO - Language override: es (using --lang flag)
2025-11-21 10:30:15 - __main__ - INFO - Translation loaded: /home/user/video2text/i18n/fonixflow_es.ts [source (.ts)]
```

### No Translation Available

```
2025-11-21 10:30:15 - __main__ - INFO - Language override: ja (using --lang flag)
2025-11-21 10:30:15 - __main__ - INFO - No translation found for ja, using English
```

### System Language (Auto)

```
2025-11-21 10:30:15 - __main__ - INFO - System locale detected: en_US (language: en)
2025-11-21 10:30:15 - __main__ - INFO - English locale detected, using default strings
```

## Tips for Translators

### Testing Your Translation

1. **Edit the .ts file:**
   ```bash
   # Open in text editor or Qt Linguist
   nano i18n/fonixflow_<lang>.ts
   ```

2. **Make your changes**

3. **Test immediately:**
   ```bash
   python fonixflow_qt.py --lang <lang>
   ```

4. **Iterate:**
   - See your changes live
   - No need to compile
   - Edit and test again

### Common Issues

**Problem:** Text is cut off

**Solution:** Use abbreviations or shorter phrases

---

**Problem:** Emoji missing in translation

**Solution:** Copy the emoji from the English text:
```xml
<source>🎙️ Record</source>
<translation>🎙️ Grabar</translation>  <!-- Include emoji! -->
```

---

**Problem:** Placeholder is translated

**Solution:** Never translate {variable} syntax:
```xml
<source>Duration: {duration:.1f}s</source>
<translation>Duración: {duration:.1f}s</translation>  <!-- Keep {duration:.1f} unchanged -->
```

---

**Problem:** File extensions translated

**Solution:** Keep extensions as-is:
```xml
<source>Text Files (*.txt)</source>
<translation>Fichiers Texte (*.txt)</translation>  <!-- Keep *.txt -->
```

## Advanced: Compiling to .qm Files

For production or faster loading, compile .ts to .qm:

### With PySide6 Tools

```bash
# Install PySide6
pip install PySide6

# Compile all languages
python compile_translations.py

# Compile specific language
python compile_translations.py es
```

### With Qt Tools (lrelease)

```bash
# Single file
lrelease i18n/fonixflow_es.ts -qm i18n/fonixflow_es.qm

# All files
for file in i18n/*.ts; do lrelease "$file"; done
```

## Performance

- **.ts files:** Slightly slower to load (milliseconds), but fine for testing
- **.qm files:** Optimized binary format, faster loading (production)

For development and testing, .ts files work perfectly!

## Help & Support

Need help?

- Check the main [TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md)
- Review [i18n/README.md](i18n/README.md)
- Open an issue on GitHub

## Quick Reference

| Task | Command |
|------|---------|
| Test Spanish | `python fonixflow_qt.py --lang es` |
| Test French | `python fonixflow_qt.py --lang fr` |
| Test German | `python fonixflow_qt.py --lang de` |
| Test Czech | `python fonixflow_qt.py --lang cs` |
| Interactive menu | `python test_languages.py` |
| System language | `python fonixflow_qt.py` |
| Get help | `python fonixflow_qt.py --help` |

---

**Happy Testing! 🌍** Every bug you find makes FonixFlow better for users worldwide!
