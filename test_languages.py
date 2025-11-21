#!/usr/bin/env python3
"""
Test FonixFlow in different languages.

This script provides an interactive menu to launch FonixFlow in different languages
for testing without changing your system language.

Usage:
    python test_languages.py
"""

import subprocess
import sys
from pathlib import Path


# Available languages with translations
LANGUAGES = [
    ('en', 'English', '🇬🇧'),
    ('es', 'Spanish (Español)', '🇪🇸'),
    ('fr', 'French (Français)', '🇫🇷'),
    ('de', 'German (Deutsch)', '🇩🇪'),
    ('zh_CN', 'Chinese Simplified (简体中文)', '🇨🇳'),
    ('ja', 'Japanese (日本語)', '🇯🇵'),
    ('pt_BR', 'Portuguese Brazil (Português)', '🇧🇷'),
    ('ru', 'Russian (Русский)', '🇷🇺'),
    ('ko', 'Korean (한국어)', '🇰🇷'),
    ('it', 'Italian (Italiano)', '🇮🇹'),
    ('pl', 'Polish (Polski)', '🇵🇱'),
    ('ar', 'Arabic (العربية)', '🇸🇦'),
    ('cs', 'Czech (Čeština)', '🇨🇿'),
]


def check_translation_status(lang_code):
    """
    Check if translation exists for the language.

    Args:
        lang_code: Language code (e.g., 'es', 'fr')

    Returns:
        tuple: (has_qm, has_ts, status_symbol)
    """
    i18n_dir = Path(__file__).parent / "i18n"
    qm_file = i18n_dir / f"fonixflow_{lang_code}.qm"
    ts_file = i18n_dir / f"fonixflow_{lang_code}.ts"

    has_qm = qm_file.exists()
    has_ts = ts_file.exists()

    if lang_code == 'en':
        return (True, True, '✓')  # English is built-in
    elif has_qm:
        return (True, has_ts, '✓')  # Compiled translation
    elif has_ts:
        # Check if .ts file has translations (not just template)
        try:
            with open(ts_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for finished translations
                if 'type="unfinished"' not in content or '</translation>' in content:
                    return (False, True, '○')  # Has .ts source
        except:
            pass
        return (False, True, '○')  # Template only
    else:
        return (False, False, '✗')  # No translation


def launch_app(lang_code=None):
    """
    Launch FonixFlow with specified language.

    Args:
        lang_code: Language code or None for default
    """
    cmd = [sys.executable, 'fonixflow_qt.py']

    if lang_code and lang_code != 'en':
        cmd.extend(['--lang', lang_code])

    print(f"\nLaunching FonixFlow{f' in {lang_code}' if lang_code else ''}...")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nApplication closed")
    except Exception as e:
        print(f"Error launching app: {e}")


def show_menu():
    """Show interactive language selection menu."""
    print("="*70)
    print("FonixFlow Language Tester".center(70))
    print("="*70)
    print("\nAvailable languages:\n")

    # Display languages with status
    for i, (code, name, flag) in enumerate(LANGUAGES, 1):
        has_qm, has_ts, status = check_translation_status(code)

        status_text = ""
        if code == 'en':
            status_text = "(Built-in)"
        elif has_qm:
            status_text = "✓ Ready (compiled)"
        elif has_ts:
            status_text = "○ Ready (source)"
        else:
            status_text = "✗ Template only"

        print(f"  {i:2d}. {flag}  {name:35s}  {status_text}")

    print(f"\n  {len(LANGUAGES) + 1:2d}. Launch with system language (automatic)")
    print(f"   0. Exit")

    print("\n" + "-"*70)

    # Legend
    print("\nLegend:")
    print("  ✓ Ready (compiled) - .qm file exists (fastest)")
    print("  ○ Ready (source)   - .ts file with translations (works for testing)")
    print("  ✗ Template only    - No translations yet (will show English)")


def main():
    """Main interactive loop."""
    while True:
        show_menu()

        try:
            choice = input("\nSelect language number: ").strip()

            if not choice or choice == '0':
                print("Goodbye!")
                break

            choice_num = int(choice)

            if choice_num == len(LANGUAGES) + 1:
                # System language
                launch_app(None)
            elif 1 <= choice_num <= len(LANGUAGES):
                lang_code, lang_name, _ = LANGUAGES[choice_num - 1]
                launch_app(lang_code)
            else:
                print(f"\n✗ Invalid choice. Please select 1-{len(LANGUAGES) + 1} or 0 to exit.")
                input("\nPress Enter to continue...")
                continue

        except ValueError:
            print("\n✗ Please enter a number.")
            input("\nPress Enter to continue...")
            continue
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            input("\nPress Enter to continue...")
            continue


if __name__ == "__main__":
    # Check if running from correct directory
    if not Path('fonixflow_qt.py').exists():
        print("Error: Please run this script from the video2text directory")
        print(f"Current directory: {Path.cwd()}")
        sys.exit(1)

    main()
