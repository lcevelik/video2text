#!/usr/bin/env python3
"""
Auto-translate ALL unfinished strings in all translation files using comprehensive translation data.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import sys

# Import translation data
sys.path.insert(0, str(Path(__file__).parent))
from translation_data import get_translations_dict, LANGUAGE_TRANSLATIONS


def translate_file(ts_file: Path, lang_code: str) -> tuple:
    """
    Translate unfinished strings in a .ts file.
    Returns: (translated_count, total_unfinished)
    """
    translations = get_translations_dict(lang_code)

    if not translations:
        print(f"No translations available for {lang_code}")
        return (0, 0)

    tree = ET.parse(ts_file)
    root = tree.getroot()

    translated_count = 0
    total_unfinished = 0

    for context in root.findall('context'):
        for message in context.findall('message'):
            source = message.find('source')
            translation = message.find('translation')

            if source is not None and translation is not None:
                source_text = source.text or ""
                trans_type = translation.get('type', '')

                # Count and translate unfinished strings
                if trans_type == 'unfinished':
                    total_unfinished += 1
                    if source_text in translations:
                        translation.text = translations[source_text]
                        del translation.attrib['type']  # Remove unfinished attribute
                        translated_count += 1
                    else:
                        print(f"  Missing translation for: {source_text[:50]}")

    # Format XML with proper indentation
    xml_str = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    pretty_xml = '\n'.join(lines)

    # Write back to file
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    return (translated_count, total_unfinished)


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    i18n_dir = script_dir.parent / 'i18n'

    if not i18n_dir.exists():
        print(f"Error: i18n directory not found at {i18n_dir}")
        return 1

    print("=" * 80)
    print("AUTO-TRANSLATING ALL LANGUAGES")
    print("=" * 80)
    print()

    lang_names = {
        'ar': 'Arabic (العربية)',
        'cs': 'Czech (Čeština)',
        'de': 'German (Deutsch)',
        'es': 'Spanish (Español)',
        'fr': 'French (Français)',
        'it': 'Italian (Italiano)',
        'ja': 'Japanese (日本語)',
        'ko': 'Korean (한국어)',
        'pl': 'Polish (Polski)',
        'pt_BR': 'Portuguese Brazil (Português)',
        'ru': 'Russian (Русский)',
        'zh_CN': 'Chinese Simplified (简体中文)'
    }

    total_translated = 0
    total_unfinished = 0
    results = []

    # Process each language
    for lang_code in sorted(LANGUAGE_TRANSLATIONS.keys()):
        ts_file = i18n_dir / f'fonixflow_{lang_code}.ts'

        if not ts_file.exists():
            print(f"{lang_names.get(lang_code, lang_code)}: File not found")
            continue

        lang_name = lang_names.get(lang_code, lang_code)
        print(f"Processing {lang_name}...", end=' ')

        translated, unfinished = translate_file(ts_file, lang_code)
        total_translated += translated
        total_unfinished += unfinished

        if translated == unfinished:
            print(f"{translated}/{unfinished} strings translated")
        else:
            print(f"{translated}/{unfinished} strings translated")

        results.append({
            'lang': lang_name,
            'code': lang_code,
            'translated': translated,
            'unfinished': unfinished
        })

    print()
    print("=" * 80)
    print("TRANSLATION SUMMARY")
    print("=" * 80)
    print(f"{'Language':<35} {'Translated':<15} {'Status':<15}")
    print("=" * 80)

    for result in results:
        status = "Complete" if result['translated'] == result['unfinished'] else f"Partial"
        print(f"{result['lang']:<35} {result['translated']}/{result['unfinished']:<10} {status:<15}")

    print("=" * 80)
    print(f"\nTotal strings translated: {total_translated}/{total_unfinished}")

    if total_translated == total_unfinished:
        print("\nAll translations completed successfully!")
    else:
        print(f"\n{total_unfinished - total_translated} strings still need translation")

    print("\nNext steps:")
    print("1. Verify translations: python scripts/verify_translations.py")
    print("2. Compile .qm files: python scripts/compile_translations.py")
    print("3. Test in application")

    return 0 if total_translated == total_unfinished else 1


if __name__ == "__main__":
    sys.exit(main())
