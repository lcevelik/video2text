# FonixFlow Translations Directory

This directory contains all translation files for FonixFlow's multi-language support.

## Files in This Directory

### Translation Source Files (.ts)
Human-readable XML files containing all translatable strings:
- `fonixflow_es.ts` - Spanish
- `fonixflow_fr.ts` - French
- `fonixflow_de.ts` - German
- `fonixflow_zh_CN.ts` - Chinese (Simplified)
- `fonixflow_ja.ts` - Japanese
- `fonixflow_pt_BR.ts` - Portuguese (Brazil)
- `fonixflow_ru.ts` - Russian
- `fonixflow_ko.ts` - Korean
- `fonixflow_it.ts` - Italian
- `fonixflow_pl.ts` - Polish
- `fonixflow_ar.ts` - Arabic
- `fonixflow_cs.ts` - Czech

### Compiled Binary Files (.qm)
Binary translation files loaded by the application at runtime:
- `fonixflow_<lang>.qm` - Generated from corresponding .ts files

## For Translators

**See the main [TRANSLATION_GUIDE.md](../TRANSLATION_GUIDE.md) for complete instructions.**

Quick start:
1. Edit the .ts file for your language (XML format)
2. Compile to .qm: `python ../compile_translations.py <lang>`
3. Test by running the app with your system language set

## For Developers

### Adding Translations
1. Wrap new UI strings with `self.tr("Your text here")`
2. Regenerate templates: `python ../create_translation_templates.py`
3. Update existing translations or create new ones

### Compiling Translations
```bash
# Compile all languages
python ../compile_translations.py

# Compile specific language
python ../compile_translations.py es
```

### File Format
.ts files are Qt Linguist translation source files in XML format:
```xml
<message>
  <source>Original English text</source>
  <translation>Translated text</translation>
</message>
```

### Loading Mechanism
The application (`fonixflow_qt.py`) automatically:
1. Detects system language on startup
2. Looks for `fonixflow_<lang>.qm` file
3. Loads translation if found
4. Falls back to English if not found

## Current Status

**Total translatable strings:** 107

**Coverage:**
- ✅ Template files generated for 12 languages
- ⏳ Translations needed (community contributions welcome!)

## Contributing

We welcome translation contributions! To contribute:

1. Fork the repository
2. Translate a .ts file
3. Test with `python ../compile_translations.py <lang>`
4. Submit a pull request with both .ts and .qm files

Every translation helps make FonixFlow accessible to more users worldwide! 🌍
