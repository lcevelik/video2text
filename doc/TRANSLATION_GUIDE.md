# FonixFlow Translation Guide

## Overview

FonixFlow now supports multi-language localization with **automatic system language detection**. When users start the application, it automatically detects their operating system language and loads the appropriate translation.

**Current Status:**
- ✅ Translation infrastructure implemented
- ✅ All 107 UI strings wrapped for translation
- ✅ Template files generated for 12 languages
- ✅ Automatic language detection on startup
- ✅ Fallback to English if translation unavailable

## Supported Languages (Templates Available)

Translation templates (.ts files) are ready for:

| Language | Code | File |
|----------|------|------|
| Spanish | es | `i18n/fonixflow_es.ts` |
| French | fr | `i18n/fonixflow_fr.ts` |
| German | de | `i18n/fonixflow_de.ts` |
| Chinese (Simplified) | zh_CN | `i18n/fonixflow_zh_CN.ts` |
| Japanese | ja | `i18n/fonixflow_ja.ts` |
| Portuguese (Brazil) | pt_BR | `i18n/fonixflow_pt_BR.ts` |
| Russian | ru | `i18n/fonixflow_ru.ts` |
| Korean | ko | `i18n/fonixflow_ko.ts` |
| Italian | it | `i18n/fonixflow_it.ts` |
| Polish | pl | `i18n/fonixflow_pl.ts` |
| Arabic | ar | `i18n/fonixflow_ar.ts` |
| Czech | cs | `i18n/fonixflow_cs.ts` |

## For Translators: Quick Start

### Option 1: Using Qt Linguist (Recommended)

1. **Install Qt Linguist:**
   ```bash
   # macOS (with Homebrew)
   brew install qt

   # Linux (Ubuntu/Debian)
   sudo apt-get install qttools5-dev-tools

   # Windows
   # Download from https://www.qt.io/download
   ```

2. **Open your language file:**
   ```bash
   linguist i18n/fonixflow_<your_lang>.ts
   ```

3. **Translate the strings in the GUI**

4. **Save the file** (marks translations as finished)

5. **Compile to .qm:**
   ```bash
   lrelease i18n/fonixflow_<your_lang>.ts
   # or
   pyside6-lrelease i18n/fonixflow_<your_lang>.ts
   ```

### Option 2: Manual Editing (Text Editor)

1. **Open the .ts file** in any text editor (VS Code, Sublime, etc.)

2. **Find unfinished translations:**
   ```xml
   <message>
     <source>Record</source>
     <translation type="unfinished"/>
   </message>
   ```

3. **Add your translation:**
   ```xml
   <message>
     <source>Record</source>
     <translation>Grabar</translation>
   </message>
   ```

4. **Compile to .qm:**
   ```bash
   python compile_translations.py
   ```

## Translation Files Explained

### .ts Files (Source)
- **Format:** XML
- **Purpose:** Human-readable translation source
- **Edit with:** Qt Linguist or text editor
- **Location:** `i18n/fonixflow_<lang>.ts`

### .qm Files (Compiled)
- **Format:** Binary
- **Purpose:** Loaded by application at runtime
- **Generated from:** .ts files
- **Location:** `i18n/fonixflow_<lang>.qm`

## Translation Guidelines

### 1. Preserve Emojis
Many strings contain emojis for visual clarity. **Always preserve emojis** in translations:

```xml
<!-- CORRECT -->
<source>🎙️ Record</source>
<translation>🎙️ Grabar</translation>

<!-- WRONG -->
<source>🎙️ Record</source>
<translation>Grabar</translation>
```

### 2. Preserve Placeholders
Some strings contain dynamic placeholders. **Never translate the placeholder syntax:**

```xml
<!-- CORRECT -->
<source>Duration: {duration:.1f}s</source>
<translation>Duración: {duration:.1f}s</translation>

<!-- WRONG -->
<source>Duration: {duration:.1f}s</source>
<translation>Duración: {duracion:.1f}s</translation>
```

### 3. Preserve Newlines
Some strings contain `\n` for line breaks. Keep them in the same positions:

```xml
<source>Line 1\nLine 2</source>
<translation>Línea 1\nLínea 2</translation>
```

### 4. File Extensions
Don't translate file extensions or technical formats:

```xml
<source>Text Files (*.txt);;SRT Subtitles (*.srt);;VTT Subtitles (*.vtt)</source>
<translation>Archivos de Texto (*.txt);;Subtítulos SRT (*.srt);;Subtítulos VTT (*.vtt)</translation>
```

### 5. Language Names
Translate language names to your target language:

```xml
<!-- Spanish translation -->
<source>English</source>
<translation>Inglés</translation>

<source>French</source>
<translation>Francés</translation>
```

### 6. Context Matters
The application is an audio recording and transcription tool. Keep translations consistent with this context:

- **Record** = Start recording audio
- **Upload** = Upload a video/audio file
- **Transcript** = View transcription results
- **Transcribe** = Process audio to text

## String Categories

### High Priority (Translate First)
1. Window titles
2. Tab names (Record, Upload, Transcript)
3. Button labels (Start, Stop, Save)
4. Error messages
5. Status messages

### Medium Priority
1. Menu items
2. Settings labels
3. Dialog instructions
4. Success messages

### Low Priority
1. Advanced settings
2. Technical help text
3. Optional features

## Testing Your Translation

### 1. Compile the .qm File
```bash
pyside6-lrelease i18n/fonixflow_<lang>.ts
```

### 2. Change Your System Language
- **macOS:** System Settings → Language & Region
- **Windows:** Settings → Time & Language → Language
- **Linux:** System Settings → Region & Language

### 3. Run the Application
```bash
python fonixflow_qt.py
```

The app should automatically load your translation!

### 4. Verify All Strings
- Check all tabs (Record, Upload, Transcript)
- Test all dialogs (Recording, Language Selection)
- Trigger error messages
- Check menu items
- Verify settings panel

## Common Issues

### Translation Not Loading

**Check:**
1. Is the .qm file in the `i18n/` directory?
2. Does the filename match the pattern: `fonixflow_<lang>.qm`?
3. Is your system language set correctly?
4. Check the console logs for error messages

**Debug:**
```bash
# Run with verbose logging
python fonixflow_qt.py
# Check console output for: "System locale detected: ..."
```

### Text Overflow

If translated text is too long and gets cut off:

1. **Use abbreviations** where appropriate
2. **Shorten the translation** while keeping meaning
3. **Report the issue** so UI can be adjusted

### Missing Strings

If you find untranslated strings:

1. **Report them** in an issue
2. Include the English text
3. Include where you found it (which tab/dialog)

## Sample Translation (Spanish)

Here's a complete example showing proper translation:

```xml
<context>
  <name>FonixFlowQt</name>
  <message>
    <source>FonixFlow - Whisper Transcription</source>
    <translation>FonixFlow - Transcripción Whisper</translation>
  </message>
  <message>
    <source>Ready</source>
    <translation>Listo</translation>
  </message>
  <message>
    <source>🎙️ Record</source>
    <translation>🎙️ Grabar</translation>
  </message>
  <message>
    <source>💾 Save Transcription</source>
    <translation>💾 Guardar Transcripción</translation>
  </message>
  <message>
    <source>Recording in progress...</source>
    <translation>Grabación en progreso...</translation>
  </message>
  <message>
    <source>No audio input device detected!</source>
    <translation>¡No se detectó ningún dispositivo de entrada de audio!</translation>
  </message>
</context>
```

## Compiling Translations

### Using Python Script (Easiest)
```bash
python compile_translations.py
```

### Manual Compilation
```bash
# Single language
lrelease i18n/fonixflow_es.ts -qm i18n/fonixflow_es.qm

# Or with PySide6 tools
pyside6-lrelease i18n/fonixflow_es.ts

# All languages
for file in i18n/*.ts; do
    lrelease "$file"
done
```

## Adding a New Language

To add a language not in the template list:

1. **Copy an existing .ts file:**
   ```bash
   cp i18n/fonixflow_es.ts i18n/fonixflow_<your_lang>.ts
   ```

2. **Update the language attribute:**
   ```xml
   <TS version="2.1" language="<your_lang>">
   ```

3. **Translate all strings**

4. **Compile to .qm**

5. **Test by changing your system language**

## Contribution Workflow

1. Fork the repository
2. Create a branch: `git checkout -b translation/<lang>`
3. Translate the .ts file for your language
4. Compile to .qm and test thoroughly
5. Commit both .ts and .qm files
6. Submit a pull request

## Getting Help

- **Found untranslated strings?** Open an issue
- **Translation questions?** Create a discussion
- **Technical problems?** Check the main README.md

## Statistics

- **Total translatable strings:** 107
- **Unique contexts:** 4
  - FonixFlowQt (main window)
  - RecordingDialog
  - MultiLanguageChoiceDialog
  - DropZone
  - TranscriptionWorker

## Language-Specific Notes

### Right-to-Left Languages (Arabic, Hebrew)
Qt automatically handles RTL layout. Just translate the strings normally.

### CJK Languages (Chinese, Japanese, Korean)
Ensure your editor uses UTF-8 encoding to preserve characters correctly.

### Special Characters
All .ts files use UTF-8 encoding. Special characters (ñ, ö, ü, ç, etc.) are fully supported.

## Thank You!

Your translations help make FonixFlow accessible to users worldwide. Every translation, no matter how small, makes a difference! 🌍✨
