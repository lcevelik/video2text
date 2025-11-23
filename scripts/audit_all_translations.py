#!/usr/bin/env python3
"""
Comprehensive translation audit script.
Verifies ALL translation strings against actual source code.
Identifies:
- Strings in .ts files that DON'T exist in source (obsolete)
- Strings in source that DON'T exist in .ts files (missing)
- Hardcoded strings that SHOULD be translatable
"""

import re
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Tuple

class SourceCodeAnalyzer:
    """Extract all translatable strings from source code."""

    def __init__(self, gui_dir: Path):
        self.gui_dir = gui_dir
        self.strings_with_context = []  # [(context, string, file, line)]
        self.all_strings = set()

    def extract_tr_strings(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Extract all .tr() strings with line numbers."""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Find class definitions for context
        class_pattern = r'class\s+(\w+)'
        classes = []
        for line in lines:
            match = re.search(class_pattern, line)
            if match:
                classes.append(match.group(1))

        # Use first class name or filename as context
        if classes:
            context = classes[0]
        else:
            context = file_path.stem

        # Match .tr() calls - capture full string with quotes
        pattern = r'\.tr\((["\'][^"\']*(?:\\.[^"\']*)*["\'])'

        results = []
        for line_num, line in enumerate(lines, 1):
            matches = re.findall(pattern, line)
            for match in matches:
                try:
                    # Unescape python string (handles \n, \", etc.)
                    unescaped = ast.literal_eval(match)
                    results.append((context, unescaped, line_num))
                except Exception:
                    # Fallback if evaluation fails (shouldn't happen with valid python)
                    pass

        return results

    def analyze_all_files(self):
        """Scan all Python files in gui directory."""
        print("=" * 80)
        print("SCANNING SOURCE CODE")
        print("=" * 80)

        for py_file in sorted(self.gui_dir.rglob('*.py')):
            if '__pycache__' in str(py_file):
                continue

            strings = self.extract_tr_strings(py_file)
            if strings:
                rel_path = py_file.relative_to(self.gui_dir.parent)
                print(f"\n{rel_path}: {len(strings)} strings")

                for context, string, line_num in strings:
                    self.strings_with_context.append((context, string, str(rel_path), line_num))
                    self.all_strings.add(string)

        print(f"\nTotal unique strings in source: {len(self.all_strings)}")
        return self.all_strings

class TranslationFileAnalyzer:
    """Analyze .ts translation files."""

    def __init__(self, i18n_dir: Path):
        self.i18n_dir = i18n_dir
        self.ts_strings = {}  # {lang: set of strings}

    def extract_ts_strings(self, ts_file: Path) -> Set[str]:
        """Extract all source strings from a .ts file."""
        tree = ET.parse(ts_file)
        root = tree.getroot()

        strings = set()
        for context in root.findall('context'):
            for message in context.findall('message'):
                source = message.find('source')
                translation = message.find('translation')

                if source is not None and source.text:
                    # Skip vanished/obsolete strings
                    if translation is not None:
                        trans_type = translation.get('type', '')
                        if trans_type != 'vanished':
                            strings.add(source.text)

        return strings

    def analyze_all_files(self):
        """Scan all .ts files."""
        print("\n" + "=" * 80)
        print("SCANNING TRANSLATION FILES")
        print("=" * 80)

        for ts_file in sorted(self.i18n_dir.glob('fonixflow_*.ts')):
            lang = ts_file.stem.replace('fonixflow_', '')
            strings = self.extract_ts_strings(ts_file)
            self.ts_strings[lang] = strings
            print(f"{ts_file.name}: {len(strings)} strings")

        # All .ts files should have the same source strings
        if self.ts_strings:
            first_lang = list(self.ts_strings.keys())[0]
            return self.ts_strings[first_lang]
        return set()

class HardcodedStringDetector:
    """Detect hardcoded strings that should be translatable."""

    def __init__(self, gui_dir: Path):
        self.gui_dir = gui_dir
        self.hardcoded_candidates = []

    def find_hardcoded_strings(self):
        """Find strings in message boxes, labels, etc. that aren't translated."""
        print("\n" + "=" * 80)
        print("DETECTING HARDCODED STRINGS")
        print("=" * 80)

        patterns = [
            # QMessageBox patterns
            r'QMessageBox\.\w+\([^,]+,[^,]+,\s*["\']([^"\']+)["\']',
            # setText patterns without .tr()
            r'\.setText\(["\']([^"\']{20,})["\']',  # Long strings likely need translation
        ]

        for py_file in sorted(self.gui_dir.rglob('*.py')):
            if '__pycache__' in str(py_file):
                continue

            with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Look for QMessageBox with hardcoded strings
            # Pattern: QMessageBox.method(self, self.tr("Title"), "hardcoded message")
            qmsg_pattern = r'QMessageBox\.\w+\([^,]+,\s*[^,]+,\s*["\']([^"\']+)["\']'
            matches = re.findall(qmsg_pattern, content)

            if matches:
                rel_path = py_file.relative_to(self.gui_dir.parent)
                for match in matches:
                    if len(match) > 10:  # Only report substantial strings
                        self.hardcoded_candidates.append((str(rel_path), match))

        return self.hardcoded_candidates

def main():
    """Run comprehensive translation audit."""
    # Use the script's location to find the project root
    base_dir = Path(__file__).resolve().parent.parent
    gui_dir = base_dir / 'gui'
    i18n_dir = base_dir / 'i18n'

    # Analyze source code
    source_analyzer = SourceCodeAnalyzer(gui_dir)
    source_strings = source_analyzer.analyze_all_files()

    # Analyze translation files
    ts_analyzer = TranslationFileAnalyzer(i18n_dir)
    ts_strings = ts_analyzer.analyze_all_files()

    # Find hardcoded strings
    hardcoded_detector = HardcodedStringDetector(gui_dir)
    hardcoded_strings = hardcoded_detector.find_hardcoded_strings()

    # Compare and report
    print("\n" + "=" * 80)
    print("AUDIT RESULTS")
    print("=" * 80)

    # Strings in .ts but NOT in source (obsolete)
    obsolete = ts_strings - source_strings
    print(f"\n❌ OBSOLETE STRINGS (in .ts but NOT in source): {len(obsolete)}")
    if obsolete:
        print("-" * 80)
        for s in sorted(obsolete):
            print(f"  - {s}")

    # Strings in source but NOT in .ts (missing)
    missing = source_strings - ts_strings
    print(f"\n⚠️  MISSING STRINGS (in source but NOT in .ts): {len(missing)}")
    if missing:
        print("-" * 80)
        for s in sorted(missing):
            # Find where this string appears
            for context, string, file_path, line_num in source_analyzer.strings_with_context:
                if string == s:
                    print(f"  - {s}")
                    print(f"    → {file_path}:{line_num} (context: {context})")
                    break

    # Hardcoded strings that should be translatable
    print(f"\n💡 HARDCODED STRINGS (should be wrapped in .tr()): {len(hardcoded_strings)}")
    if hardcoded_strings:
        print("-" * 80)
        seen = set()
        for file_path, string in hardcoded_strings:
            if string not in seen:
                seen.add(string)
                print(f"  - {string}")
                print(f"    → {file_path}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✓ Strings in source code: {len(source_strings)}")
    print(f"✓ Strings in .ts files: {len(ts_strings)}")
    print(f"❌ Obsolete (remove from .ts): {len(obsolete)}")
    print(f"⚠️  Missing (add to .ts): {len(missing)}")
    print(f"💡 Hardcoded (need .tr()): {len(hardcoded_strings)}")

    # Detailed source string locations
    print("\n" + "=" * 80)
    print("DETAILED SOURCE STRING LOCATIONS")
    print("=" * 80)

    # Group by context
    by_context = defaultdict(list)
    for context, string, file_path, line_num in source_analyzer.strings_with_context:
        by_context[context].append((string, file_path, line_num))

    for context in sorted(by_context.keys()):
        strings = by_context[context]
        print(f"\n{context} ({len(set(s[0] for s in strings))} unique strings):")
        print("-" * 80)

        # Show unique strings with their locations
        seen_strings = {}
        for string, file_path, line_num in strings:
            if string not in seen_strings:
                seen_strings[string] = (file_path, line_num)

        for string in sorted(seen_strings.keys())[:20]:  # Show first 20
            file_path, line_num = seen_strings[string]
            display = string[:70] + '...' if len(string) > 70 else string
            print(f"  {file_path}:{line_num}")
            print(f"    → {display}")

        if len(seen_strings) > 20:
            print(f"  ... and {len(seen_strings) - 20} more")

    return {
        'source_strings': source_strings,
        'ts_strings': ts_strings,
        'obsolete': obsolete,
        'missing': missing,
        'hardcoded': hardcoded_strings
    }

if __name__ == "__main__":
    results = main()
