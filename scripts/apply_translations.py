#!/usr/bin/env python3
"""
Apply translations from translation_data.py to all .ts files.
Marks translated strings as finished.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Import translations from translation_data.py
sys.path.insert(0, str(Path(__file__).parent))
from translation_data import SOURCE_STRINGS, LANGUAGE_TRANSLATIONS

def create_translation_dict(lang_code):
    """Create a dictionary mapping source strings to translations."""
    if lang_code not in LANGUAGE_TRANSLATIONS:
        return {}

    translations = LANGUAGE_TRANSLATIONS[lang_code]

    # Map source strings to their translations
    translation_map = {}
    for i, source in enumerate(SOURCE_STRINGS):
        if i < len(translations):
            translation_map[source] = translations[i]

    return translation_map

def apply_translations_to_file(ts_file: Path, lang_code: str):
    """Apply translations to a .ts file."""
    translation_map = create_translation_dict(lang_code)

    if not translation_map:
        print(f"⚠️  No translations available for {lang_code}")
        return 0, 0

    tree = ET.parse(ts_file)
    root = tree.getroot()

    translated_count = 0
    total_unfinished = 0

    for context in root.findall('context'):
        for message in context.findall('message'):
            source_elem = message.find('source')
            translation_elem = message.find('translation')

            if source_elem is not None and translation_elem is not None:
                source_text = source_elem.text
                trans_type = translation_elem.get('type', '')

                # Count unfinished
                if trans_type == 'unfinished':
                    total_unfinished += 1

                    # Apply translation if available
                    if source_text in translation_map:
                        translation_elem.text = translation_map[source_text]
                        # Remove unfinished marker
                        if 'type' in translation_elem.attrib:
                            del translation_elem.attrib['type']
                        translated_count += 1

    # Save with proper formatting
    indent_xml(root)
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)

    # Fix XML declaration format
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("<?xml version='1.0' encoding='utf-8'?>",
                             '<?xml version="1.0" encoding="utf-8"?>')
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return translated_count, total_unfinished

def indent_xml(elem, level=0):
    """Add pretty-printing indentation to XML."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent

def main():
    """Apply translations to all .ts files."""
    i18n_dir = Path('/home/user/video2text/i18n')

    lang_names = {
        'ar': 'Arabic',
        'cs': 'Czech',
        'de': 'German',
        'es': 'Spanish',
        'fr': 'French',
        'it': 'Italian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'pl': 'Polish',
        'pt_BR': 'Portuguese (Brazil)',
        'ru': 'Russian',
        'zh_CN': 'Chinese (Simplified)'
    }

    print("=" * 80)
    print("APPLYING TRANSLATIONS FROM translation_data.py")
    print("=" * 80)

    total_translated = 0
    total_unfinished_before = 0

    for ts_file in sorted(i18n_dir.glob('fonixflow_*.ts')):
        lang_code = ts_file.stem.replace('fonixflow_', '')
        lang_name = lang_names.get(lang_code, lang_code)

        translated, unfinished_before = apply_translations_to_file(ts_file, lang_code)
        total_translated += translated
        total_unfinished_before += unfinished_before

        remaining = unfinished_before - translated
        status = "✅" if remaining == 0 else f"⚠️  {remaining} remaining"

        print(f"{lang_name:20s} {translated:2d}/{unfinished_before:2d} translated  {status}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total translations applied: {total_translated}")
    print(f"Total unfinished before: {total_unfinished_before}")
    print(f"Total still unfinished: {total_unfinished_before - total_translated}")

    # Show final completion status
    print("\n" + "=" * 80)
    print("FINAL COMPLETION STATUS")
    print("=" * 80)

    for ts_file in sorted(i18n_dir.glob('fonixflow_*.ts')):
        lang_code = ts_file.stem.replace('fonixflow_', '')
        lang_name = lang_names.get(lang_code, lang_code)

        tree = ET.parse(ts_file)
        root = tree.getroot()

        total = 0
        finished = 0

        for context in root.findall('context'):
            for message in context.findall('message'):
                translation = message.find('translation')
                if translation is not None:
                    trans_type = translation.get('type', '')
                    if trans_type != 'vanished':
                        total += 1
                        if trans_type != 'unfinished' and translation.text:
                            finished += 1

        pct = (finished / total * 100) if total > 0 else 0
        status = "✅" if pct == 100 else "⚠️" if pct >= 80 else "❌"
        print(f"{lang_name:20s} {finished:3d}/{total:3d} ({pct:5.1f}%) {status}")

if __name__ == "__main__":
    main()
