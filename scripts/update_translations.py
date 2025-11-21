#!/usr/bin/env python3
"""
Update translation files with new strings while preserving existing translations.

This script:
1. Reads existing .ts translation files
2. Preserves all existing translations
3. Adds any new strings from the template as 'unfinished'
4. Removes obsolete strings that are no longer in the source code
5. Maintains the same structure and formatting
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, Set, Tuple
import sys


# Import the expected string list from create_translation_templates.py
sys.path.insert(0, str(Path(__file__).parent))
from create_translation_templates import TRANSLATABLE_STRINGS


class TranslationUpdater:
    """Update translation files while preserving existing translations."""

    def __init__(self, ts_file_path: Path):
        self.ts_file_path = ts_file_path
        self.lang_code = self._extract_lang_code()
        self.existing_translations = {}  # {(context, source): (translation_text, translation_type)}
        self.new_strings = set()
        self.removed_strings = set()
        self.updated = False

    def _extract_lang_code(self) -> str:
        """Extract language code from filename."""
        return self.ts_file_path.stem.replace('fonixflow_', '')

    def load_existing_translations(self) -> bool:
        """Load existing translations from the .ts file."""
        try:
            tree = ET.parse(self.ts_file_path)
            root = tree.getroot()

            for context in root.findall('context'):
                context_name_elem = context.find('name')
                if context_name_elem is None:
                    continue
                context_name = context_name_elem.text or ""

                for message in context.findall('message'):
                    source = message.find('source')
                    translation = message.find('translation')

                    if source is not None and translation is not None:
                        source_text = source.text or ""
                        translation_text = translation.text or ""
                        translation_type = translation.get('type', '')

                        # Store existing translation
                        key = (context_name, source_text)
                        self.existing_translations[key] = (translation_text, translation_type)

            return True
        except Exception as e:
            print(f"Warning: Could not load existing translations from {self.ts_file_path}: {e}")
            return False

    def update_translation_file(self) -> bool:
        """Update the translation file with new strings while preserving existing translations."""
        # Load existing translations first
        self.load_existing_translations()

        # Create new root element
        root = ET.Element('TS')
        root.set('version', '2.1')
        root.set('language', self.lang_code)

        # Group strings by context
        contexts = {}
        for context, source_text in TRANSLATABLE_STRINGS:
            if context not in contexts:
                contexts[context] = []
            contexts[context].append(source_text)

        # Track which strings we've seen from template
        template_keys = set()

        # Create context elements
        for context_name, messages in sorted(contexts.items()):
            context = ET.SubElement(root, 'context')

            name_elem = ET.SubElement(context, 'name')
            name_elem.text = context_name

            # Add each message
            for source_text in messages:
                message = ET.SubElement(context, 'message')

                source = ET.SubElement(message, 'source')
                source.text = source_text

                # Check if we have an existing translation
                key = (context_name, source_text)
                template_keys.add(key)

                if key in self.existing_translations:
                    # Preserve existing translation
                    translation_text, translation_type = self.existing_translations[key]
                    translation = ET.SubElement(message, 'translation')
                    if translation_type:
                        translation.set('type', translation_type)
                    translation.text = translation_text
                else:
                    # New string - add as unfinished
                    translation = ET.SubElement(message, 'translation')
                    translation.set('type', 'unfinished')
                    translation.text = ''
                    self.new_strings.add(source_text)
                    self.updated = True

        # Find removed strings (in old file but not in template)
        for key in self.existing_translations:
            if key not in template_keys:
                self.removed_strings.add(f"{key[0]}: {key[1]}")
                self.updated = True

        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')

        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        pretty_xml = '\n'.join(lines)

        # Write to file
        with open(self.ts_file_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

        return True

    def get_summary(self) -> Dict:
        """Return summary of changes."""
        return {
            'lang_code': self.lang_code,
            'file': self.ts_file_path.name,
            'new_strings_count': len(self.new_strings),
            'removed_strings_count': len(self.removed_strings),
            'existing_translations': len(self.existing_translations),
            'new_strings': sorted(list(self.new_strings))[:10],  # First 10 for display
            'removed_strings': sorted(list(self.removed_strings))[:10],
            'updated': self.updated
        }


def update_all_translations(i18n_dir: Path) -> list:
    """Update all translation files in the i18n directory."""
    results = []

    # Find all .ts files
    ts_files = sorted(i18n_dir.glob('fonixflow_*.ts'))

    if not ts_files:
        print(f"No .ts files found in {i18n_dir}")
        return results

    for ts_file in ts_files:
        updater = TranslationUpdater(ts_file)
        if updater.update_translation_file():
            summary = updater.get_summary()
            results.append(summary)

    return results


def print_update_report(results: list):
    """Print a report of all updates."""
    print("=" * 80)
    print("TRANSLATION UPDATE REPORT")
    print("=" * 80)
    print()

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

    print(f"Updated {len(results)} translation files\n")
    print("=" * 80)
    print(f"{'Language':<25} {'New Strings':<15} {'Removed':<15} {'Status':<15}")
    print("=" * 80)

    total_new = 0
    total_removed = 0

    for summary in results:
        lang_name = lang_names.get(summary['lang_code'], summary['lang_code'])
        lang_display = f"{lang_name} ({summary['lang_code']})"

        status = "✅ Updated" if summary['updated'] else "✓ No changes"

        print(f"{lang_display:<25} {summary['new_strings_count']:<15} "
              f"{summary['removed_strings_count']:<15} {status:<15}")

        total_new += summary['new_strings_count']
        total_removed += summary['removed_strings_count']

    print("=" * 80)
    print(f"\nTotal new strings added: {total_new}")
    print(f"Total obsolete strings removed: {total_removed}")

    # Show details of new strings (from first file that has them)
    for summary in results:
        if summary['new_strings_count'] > 0:
            print(f"\nNew strings added (showing first 10):")
            for i, string in enumerate(summary['new_strings'][:10], 1):
                display = string[:65] + '...' if len(string) > 65 else string
                print(f"  {i}. {display}")
            if summary['new_strings_count'] > 10:
                print(f"  ... and {summary['new_strings_count'] - 10} more")
            break

    print("\n" + "=" * 80)
    print("Next steps:")
    print("1. Review the changes with: git diff i18n/")
    print("2. Translate new strings (marked as 'unfinished')")
    print("3. Compile translations: python scripts/compile_translations.py")
    print("4. Test in the application")
    print("=" * 80)


def main():
    """Main entry point."""
    print("Updating translation files...\n")

    # Find i18n directory
    script_dir = Path(__file__).parent
    i18n_dir = script_dir.parent / 'i18n'

    if not i18n_dir.exists():
        print(f"Error: i18n directory not found at {i18n_dir}")
        return 1

    # Update all translation files
    results = update_all_translations(i18n_dir)

    if not results:
        print("No translation files found to update.")
        return 1

    # Print report
    print_update_report(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
