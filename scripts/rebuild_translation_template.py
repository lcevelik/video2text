#!/usr/bin/env python3
"""
Rebuild translation template from actual source code.
This ensures the template matches what's REALLY in the code.
"""

import re
from pathlib import Path
from collections import defaultdict

def extract_tr_strings_with_context(file_path):
    """Extract all .tr() strings with their contexts from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find class definitions to determine context
    class_pattern = r'class\s+(\w+)'
    classes = re.findall(class_pattern, content)

    # If no class, use filename as context
    if not classes:
        context = file_path.stem
    else:
        context = classes[0]  # Use first class name

    # Match .tr() calls - handles self.tr(), window.tr(), etc.
    pattern = r'\.tr\(["\']([^"\']*(?:\\.[^"\']*)*)["\']'
    matches = re.findall(pattern, content, re.MULTILINE)

    return [(context, s) for s in matches]

def main():
    """Extract all translation strings from the codebase."""
    gui_dir = Path('/home/user/video2text/gui')

    # Collect all strings with contexts
    context_strings = defaultdict(set)
    all_strings = []

    for py_file in sorted(gui_dir.rglob('*.py')):
        if '__pycache__' in str(py_file):
            continue

        strings_with_context = extract_tr_strings_with_context(py_file)
        for context, string in strings_with_context:
            context_strings[context].add(string)
            all_strings.append((context, string))

    # Remove duplicates while preserving context info
    unique_strings = {}
    for context, string in all_strings:
        if string not in unique_strings:
            unique_strings[string] = context

    print("=" * 80)
    print("ACTUAL TRANSLATION STRINGS FROM SOURCE CODE")
    print("=" * 80)
    print(f"\nTotal unique strings: {len(unique_strings)}\n")

    # Print by context
    print("Strings by Context:")
    print("-" * 80)
    for context in sorted(context_strings.keys()):
        strings = sorted(context_strings[context])
        print(f"\n{context} ({len(strings)} strings):")
        for s in strings[:10]:  # Show first 10
            display = s[:70] + '...' if len(s) > 70 else s
            print(f"  - {display}")
        if len(strings) > 10:
            print(f"  ... and {len(strings) - 10} more")

    print("\n" + "=" * 80)
    print("PYTHON CODE FOR create_translation_templates.py:")
    print("=" * 80)
    print("\nTRANSLATABLE_STRINGS = [")

    # Generate the list in the format needed
    for string in sorted(unique_strings.keys()):
        context = unique_strings[string]
        # Escape quotes and backslashes
        escaped = string.replace('\\', '\\\\').replace('"', '\\"')
        print(f'    ("{context}", "{escaped}"),')

    print("]\n")
    print(f"Total: {len(unique_strings)} strings")

if __name__ == "__main__":
    main()
