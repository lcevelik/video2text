#!/usr/bin/env python3
"""
Extract all actual translation strings from Python source code.
This will show us what strings are REALLY being used.
"""

import re
from pathlib import Path

def extract_tr_strings(file_path):
    """Extract all self.tr() strings from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match self.tr("string") or self.tr('string')
    # Handle multiline strings and escaped quotes
    pattern = r'self\.tr\(["\']([^"\']*(?:\\.[^"\']*)*)["\']'
    matches = re.findall(pattern, content, re.MULTILINE)

    return matches

def main():
    """Extract all translation strings from GUI files."""
    gui_dir = Path('/home/user/video2text/gui')

    all_strings = set()
    file_strings = {}

    for py_file in gui_dir.glob('*.py'):
        strings = extract_tr_strings(py_file)
        if strings:
            file_strings[py_file.name] = strings
            all_strings.update(strings)

    print("=" * 80)
    print("ACTUAL TRANSLATION STRINGS IN SOURCE CODE")
    print("=" * 80)
    print(f"\nTotal unique strings: {len(all_strings)}\n")

    print("Strings by file:")
    print("-" * 80)
    for filename, strings in sorted(file_strings.items()):
        print(f"\n{filename} ({len(strings)} strings):")
        for s in sorted(set(strings)):
            print(f"  - {s}")

    print("\n" + "=" * 80)
    print("ALL UNIQUE STRINGS (sorted):")
    print("=" * 80)
    for i, s in enumerate(sorted(all_strings), 1):
        print(f"{i:3d}. {s}")

    print(f"\n\nTotal: {len(all_strings)} unique translation strings")

if __name__ == "__main__":
    main()
