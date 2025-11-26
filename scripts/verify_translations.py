#!/usr/bin/env python3
"""
Verify and analyze all translation files (.ts) in the i18n directory.

This script:
1. Parses each .ts file to count total strings
2. Identifies translated vs unfinished/empty translations
3. Compares with the expected string count from create_translation_templates.py
4. Generates a comprehensive report of translation status
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple
import sys


# Import the expected string count from create_translation_templates.py
sys.path.insert(0, str(Path(__file__).parent))
from create_translation_templates import TRANSLATABLE_STRINGS


class TranslationAnalyzer:
    """Analyze translation file completeness and accuracy."""

    def __init__(self, ts_file_path: Path):
        self.ts_file_path = ts_file_path
        self.lang_code = self._extract_lang_code()
        self.tree = None
        self.root = None
        self.total_strings = 0
        self.translated_strings = 0
        self.unfinished_strings = 0
        self.empty_translations = 0
        self.missing_strings = []

    def _extract_lang_code(self) -> str:
        """Extract language code from filename (e.g., 'fonixflow_es.ts' -> 'es')."""
        return self.ts_file_path.stem.replace('fonixflow_', '')

    def parse(self) -> bool:
        """Parse the .ts XML file."""
        try:
            self.tree = ET.parse(self.ts_file_path)
            self.root = self.tree.getroot()
            return True
        except Exception as e:
            print(f"Error parsing {self.ts_file_path}: {e}")
            return False

    def analyze(self) -> Dict:
        """Analyze the translation file and return statistics."""
        if not self.parse():
            return None

        # Track all source strings found in this file
        found_sources = set()

        # Iterate through all contexts and messages
        for context in self.root.findall('context'):
            for message in context.findall('message'):
                source = message.find('source')
                translation = message.find('translation')

                if source is not None and translation is not None:
                    self.total_strings += 1
                    source_text = source.text or ""
                    translation_text = translation.text or ""
                    translation_type = translation.get('type', '')

                    # Track this source string
                    found_sources.add(source_text)

                    # Check if translation is finished
                    if translation_type == 'unfinished':
                        self.unfinished_strings += 1
                    elif not translation_text or translation_text.strip() == '':
                        self.empty_translations += 1
                    else:
                        self.translated_strings += 1

        # Check for missing strings (in template but not in this file)
        expected_sources = {source_text for _, source_text in TRANSLATABLE_STRINGS}
        self.missing_strings = list(expected_sources - found_sources)

        return self.get_stats()

    def get_stats(self) -> Dict:
        """Return statistics dictionary."""
        completion_rate = 0
        if self.total_strings > 0:
            completion_rate = (self.translated_strings / self.total_strings) * 100

        return {
            'lang_code': self.lang_code,
            'file_path': str(self.ts_file_path),
            'total_strings': self.total_strings,
            'translated': self.translated_strings,
            'unfinished': self.unfinished_strings,
            'empty': self.empty_translations,
            'completion_rate': completion_rate,
            'missing_strings': self.missing_strings,
            'missing_count': len(self.missing_strings),
            'expected_total': len(TRANSLATABLE_STRINGS)
        }


def analyze_all_translations(i18n_dir: Path) -> List[Dict]:
    """Analyze all .ts files in the i18n directory."""
    results = []

    # Find all .ts files
    ts_files = sorted(i18n_dir.glob('fonixflow_*.ts'))

    if not ts_files:
        print(f"No .ts files found in {i18n_dir}")
        return results

    for ts_file in ts_files:
        analyzer = TranslationAnalyzer(ts_file)
        stats = analyzer.analyze()
        if stats:
            results.append(stats)

    return results


def print_summary_report(results: List[Dict]):
    """Print a summary report of all translation files."""
    print("=" * 80)
    print("TRANSLATION VERIFICATION REPORT")
    print("=" * 80)
    print()

    # Language name mapping
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

    print(f"Total languages: {len(results)}")
    print(f"Expected strings per language: {results[0]['expected_total'] if results else 'N/A'}")
    print()
    print("=" * 80)
    print(f"{'Language':<25} {'Total':<8} {'Done':<8} {'Missing':<10} {'Status':<15}")
    print("=" * 80)

    fully_translated = []
    partially_translated = []
    not_translated = []

    for stats in sorted(results, key=lambda x: x['completion_rate'], reverse=True):
        lang_name = lang_names.get(stats['lang_code'], stats['lang_code'])
        lang_display = f"{lang_name} ({stats['lang_code']})"

        # Calculate status
        if stats['completion_rate'] == 100 and stats['missing_count'] == 0:
            status = "COMPLETE"
            fully_translated.append(stats)
        elif stats['completion_rate'] >= 50:
            status = "PARTIAL"
            partially_translated.append(stats)
        else:
            status = "INCOMPLETE"
            not_translated.append(stats)

        # Check if file has correct number of strings
        string_count_issue = ""
        if stats['total_strings'] != stats['expected_total']:
            string_count_issue = f" (!={stats['expected_total']})"

        print(f"{lang_display:<25} {stats['total_strings']:<8} "
              f"{stats['translated']:<8} {stats['missing_count']:<10} {status:<15}")

    print("=" * 80)
    print()

    # Summary statistics
    print("SUMMARY:")
    print(f"  Fully translated: {len(fully_translated)} languages")
    print(f"  Partially translated: {len(partially_translated)} languages")
    print(f"  Incomplete: {len(not_translated)} languages")
    print()

    return fully_translated, partially_translated, not_translated


def print_detailed_report(results: List[Dict]):
    """Print detailed report for each language."""
    print()
    print("=" * 80)
    print("DETAILED ANALYSIS")
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

    for stats in sorted(results, key=lambda x: x['completion_rate'], reverse=True):
        lang_name = lang_names.get(stats['lang_code'], stats['lang_code'])

        print(f"\n{lang_name} ({stats['lang_code']})")
        print("-" * 60)
        print(f"  File: {Path(stats['file_path']).name}")
        print(f"  Total strings: {stats['total_strings']} (expected: {stats['expected_total']})")
        print(f"  Translated: {stats['translated']}")
        print(f"  Unfinished: {stats['unfinished']}")
        print(f"  Empty: {stats['empty']}")
        print(f"  Completion: {stats['completion_rate']:.1f}%")

        # Check for issues
        issues = []
        if stats['total_strings'] != stats['expected_total']:
            diff = stats['total_strings'] - stats['expected_total']
            if diff > 0:
                issues.append(f"Has {diff} extra strings")
            else:
                issues.append(f"Missing {abs(diff)} strings from template")

        if stats['missing_count'] > 0:
            issues.append(f"{stats['missing_count']} source strings not found in file")

        if stats['unfinished'] > 0:
            issues.append(f"{stats['unfinished']} strings marked as unfinished")

        if stats['empty'] > 0:
            issues.append(f"{stats['empty']} strings have empty translations")

        if issues:
            print(f"  Issues:")
            for issue in issues:
                print(f"    {issue}")
        else:
            print(f"  No issues found!")

        # Show missing strings if any
        if stats['missing_strings']:
            print(f"\n  Missing source strings ({len(stats['missing_strings'])}):")
            for i, missing in enumerate(stats['missing_strings'][:5], 1):
                print(f"    {i}. {missing[:60]}{'...' if len(missing) > 60 else ''}")
            if len(stats['missing_strings']) > 5:
                print(f"    ... and {len(stats['missing_strings']) - 5} more")


def main():
    """Main entry point."""
    print("Starting translation verification...\n")

    # Find i18n directory
    script_dir = Path(__file__).parent
    i18n_dir = script_dir.parent / 'i18n'

    if not i18n_dir.exists():
        print(f"Error: i18n directory not found at {i18n_dir}")
        return 1

    # Analyze all translation files
    results = analyze_all_translations(i18n_dir)

    if not results:
        print("No translation files found to analyze.")
        return 1

    # Print reports
    fully_done, partial, incomplete = print_summary_report(results)
    print_detailed_report(results)

    print()
    print("=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

    # Return exit code based on results
    if incomplete:
        print("\nSome translations are incomplete. Please review the report above.")
        return 1
    elif partial:
        print("\nSome translations are partially complete.")
        return 0
    else:
        print("\nAll translations are complete!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
