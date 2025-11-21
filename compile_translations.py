#!/usr/bin/env python3
"""
Compile Qt .ts translation files to binary .qm files.

The .qm files are loaded by the application at runtime based on the system language.

Usage:
    python compile_translations.py [language_code]

Examples:
    python compile_translations.py          # Compile all languages
    python compile_translations.py es       # Compile only Spanish
    python compile_translations.py zh_CN    # Compile only Chinese (Simplified)
"""

import subprocess
import sys
from pathlib import Path


def compile_ts_file(ts_file):
    """
    Compile a .ts file to .qm using lrelease or pyside6-lrelease.

    Args:
        ts_file: Path to the .ts file

    Returns:
        bool: True if successful, False otherwise
    """
    qm_file = ts_file.with_suffix('.qm')

    # Try lrelease first (standard Qt tool)
    commands = [
        ['lrelease', str(ts_file), '-qm', str(qm_file)],
        ['pyside6-lrelease', str(ts_file)],  # Creates .qm automatically
        ['pyside6-lrelease', str(ts_file), '-qm', str(qm_file)],
    ]

    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"  ✓ {ts_file.name} → {qm_file.name}")
                if result.stdout and 'warning' not in result.stdout.lower():
                    # Show summary if present
                    for line in result.stdout.strip().split('\n'):
                        if 'translated' in line.lower() or 'unfinished' in line.lower():
                            print(f"    {line.strip()}")
                return True
            elif 'not found' not in result.stderr and 'command not found' not in result.stderr:
                # Command exists but failed - show error
                if result.stderr:
                    print(f"  ✗ Error: {result.stderr.strip()}")
        except FileNotFoundError:
            continue  # Try next command

    print(f"  ✗ Failed to compile {ts_file.name}")
    print(f"    Please install Qt tools: pip install PySide6")
    print(f"    Or install system Qt: apt-get install qt6-tools (Linux) / brew install qt (macOS)")
    return False


def main():
    """Main function."""
    i18n_dir = Path(__file__).parent / "i18n"

    if not i18n_dir.exists():
        print(f"Error: {i18n_dir} directory not found!")
        sys.exit(1)

    # Get list of .ts files to compile
    if len(sys.argv) > 1:
        # Compile specific language
        lang_code = sys.argv[1]
        ts_files = list(i18n_dir.glob(f"fonixflow_{lang_code}.ts"))
        if not ts_files:
            print(f"Error: No translation file found for language '{lang_code}'")
            print(f"Expected file: {i18n_dir}/fonixflow_{lang_code}.ts")
            sys.exit(1)
    else:
        # Compile all languages
        ts_files = sorted(i18n_dir.glob("fonixflow_*.ts"))
        if not ts_files:
            print(f"Error: No .ts files found in {i18n_dir}")
            sys.exit(1)

    print("="*60)
    print("Compiling Translation Files (.ts → .qm)")
    print("="*60)
    print(f"\nFound {len(ts_files)} translation file(s) to compile:\n")

    success_count = 0
    fail_count = 0

    for ts_file in ts_files:
        print(f"{ts_file.stem.replace('fonixflow_', '')}:")
        if compile_ts_file(ts_file):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "="*60)
    print(f"Compilation Results: {success_count} succeeded, {fail_count} failed")
    print("="*60)

    if success_count > 0:
        print(f"\n✓ Compiled files are ready in: {i18n_dir}")
        print("  The application will automatically load them based on system language.")

    if fail_count > 0:
        print(f"\n✗ {fail_count} file(s) failed to compile")
        print("  Install Qt tools to compile translations:")
        print("    pip install PySide6")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
