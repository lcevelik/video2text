#!/usr/bin/env python3
"""
Synchronize translation files with actual source code.
- Remove obsolete strings (in .ts but not in source)
- Add missing strings (in source but not in .ts)
- Preserve existing translations
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Set, Dict, Tuple
import re
from collections import defaultdict

def extract_source_strings_with_context(gui_dir: Path) -> Dict[str, str]:
    """Extract all .tr() strings from source with their contexts."""
    strings_with_context = {}  # {string: context}

    for py_file in sorted(gui_dir.rglob('*.py')):
        if '__pycache__' in str(py_file):
            continue

        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find class definitions
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, content)

        # Use first class name or filename as context
        if classes:
            context = classes[0]
        else:
            context = py_file.stem

        # Match .tr() calls
        pattern = r'\.tr\(["\']([^"\']*(?:\\.[^"\']*)*)["\']'
        matches = re.findall(pattern, content, re.MULTILINE)

        for match in matches:
            # Use first occurrence's context
            if match not in strings_with_context:
                strings_with_context[match] = context

    return strings_with_context

def sync_translation_file(ts_file: Path, source_strings: Dict[str, str]):
    """
    Sync a .ts file with source code strings.
    - Remove obsolete strings
    - Add missing strings
    - Preserve existing translations
    """
    print(f"\n{'='*80}")
    print(f"Syncing: {ts_file.name}")
    print(f"{'='*80}")

    # Parse existing .ts file
    tree = ET.parse(ts_file)
    root = tree.getroot()

    # Extract existing translations
    existing_translations = {}  # {(context, source): (translation_text, translation_type)}
    contexts_in_file = {}  # {context_name: context_element}

    for context_elem in root.findall('context'):
        name_elem = context_elem.find('name')
        if name_elem is not None and name_elem.text:
            context_name = name_elem.text
            contexts_in_file[context_name] = context_elem

            for message in context_elem.findall('message'):
                source_elem = message.find('source')
                translation_elem = message.find('translation')

                if source_elem is not None and source_elem.text:
                    source_text = source_elem.text

                    trans_text = translation_elem.text if translation_elem is not None else ""
                    trans_type = translation_elem.get('type', '') if translation_elem is not None else ""

                    # Skip vanished strings
                    if trans_type != 'vanished':
                        existing_translations[(context_name, source_text)] = (trans_text, trans_type)

    print(f"Existing translations: {len(existing_translations)}")

    # Group source strings by context
    strings_by_context = defaultdict(set)
    for source_text, context_name in source_strings.items():
        strings_by_context[context_name].add(source_text)

    # Rebuild contexts
    removed_count = 0
    added_count = 0
    preserved_count = 0

    # Clear all contexts
    for context_elem in list(root.findall('context')):
        root.remove(context_elem)

    # Rebuild with current strings only
    for context_name in sorted(strings_by_context.keys()):
        context_elem = ET.SubElement(root, 'context')
        name_elem = ET.SubElement(context_elem, 'name')
        name_elem.text = context_name

        for source_text in sorted(strings_by_context[context_name]):
            message_elem = ET.SubElement(context_elem, 'message')
            source_elem = ET.SubElement(message_elem, 'source')
            source_elem.text = source_text

            translation_elem = ET.SubElement(message_elem, 'translation')

            # Check if we have existing translation
            key = (context_name, source_text)
            if key in existing_translations:
                trans_text, trans_type = existing_translations[key]
                translation_elem.text = trans_text
                if trans_type:
                    translation_elem.set('type', trans_type)
                preserved_count += 1
            else:
                # New string - mark as unfinished
                translation_elem.set('type', 'unfinished')
                translation_elem.text = ""
                added_count += 1

    # Count removed strings
    all_source_texts = set(source_strings.keys())
    existing_sources = set(src for ctx, src in existing_translations.keys())
    removed_count = len(existing_sources - all_source_texts)

    # Write back with proper formatting
    indent_xml(root)
    tree.write(ts_file, encoding='utf-8', xml_declaration=True)

    # Fix XML declaration format (ElementTree uses single quotes, Qt uses double quotes)
    with open(ts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace("<?xml version='1.0' encoding='utf-8'?>",
                             '<?xml version="1.0" encoding="utf-8"?>')
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Preserved: {preserved_count} translations")
    print(f"+ Added: {added_count} new strings (marked unfinished)")
    print(f"- Removed: {removed_count} obsolete strings")

    return {
        'preserved': preserved_count,
        'added': added_count,
        'removed': removed_count
    }

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
    """Sync all translation files with source code."""
    base_dir = Path('/home/user/video2text')
    gui_dir = base_dir / 'gui'
    i18n_dir = base_dir / 'i18n'

    print("="*80)
    print("EXTRACTING SOURCE STRINGS")
    print("="*80)

    # Extract all strings from source code
    source_strings = extract_source_strings_with_context(gui_dir)
    print(f"\nTotal strings in source: {len(source_strings)}")

    # Show strings by context
    by_context = defaultdict(list)
    for string, context in source_strings.items():
        by_context[context].append(string)

    print("\nStrings by context:")
    for context in sorted(by_context.keys()):
        print(f"  {context}: {len(by_context[context])} strings")

    # Sync all .ts files
    print("\n" + "="*80)
    print("SYNCING TRANSLATION FILES")
    print("="*80)

    total_stats = {'preserved': 0, 'added': 0, 'removed': 0}

    for ts_file in sorted(i18n_dir.glob('fonixflow_*.ts')):
        stats = sync_translation_file(ts_file, source_strings)
        for key in stats:
            total_stats[key] += stats[key]

    # Summary
    print("\n" + "="*80)
    print("SYNC COMPLETE")
    print("="*80)
    print(f"✓ Total preserved: {total_stats['preserved']} translations")
    print(f"+ Total added: {total_stats['added']} new strings")
    print(f"- Total removed: {total_stats['removed']} obsolete strings")
    print(f"\nAll .ts files now have exactly {len(source_strings)} strings matching source code.")

if __name__ == "__main__":
    main()
