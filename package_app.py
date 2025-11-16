#!/usr/bin/env python3
"""
ONE-COMMAND PACKAGING SCRIPT

This script does EVERYTHING for you:
1. Bundles Whisper models (your choice of size)
2. Downloads FFmpeg binaries
3. Builds self-contained executable
4. Creates distribution package

Usage:
    # Best quality (large model, ~3.5GB total)
    python package_app.py --quality best

    # Balanced (medium model, ~1.2GB total)
    python package_app.py --quality balanced

    # Lightweight (base model, ~500MB total)
    python package_app.py --quality lightweight

    # Custom
    python package_app.py --models large medium --gui qt
"""

import sys
import subprocess
import argparse
from pathlib import Path


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_color(text, color=Colors.END):
    """Print colored text."""
    print(f"{color}{text}{Colors.END}")


def print_header(text):
    """Print a header."""
    print()
    print_color("=" * 80, Colors.BOLD)
    print_color(text.center(80), Colors.BOLD)
    print_color("=" * 80, Colors.BOLD)
    print()


def run_command(cmd, description):
    """Run a command and handle errors."""
    print_color(f"\n▶ {description}...", Colors.BLUE)
    print(f"  Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True)
        print_color(f"✓ {description} completed", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_color(f"✗ {description} failed: {e}", Colors.RED)
        return False
    except FileNotFoundError:
        print_color(f"✗ Script not found: {cmd[0]}", Colors.RED)
        print(f"  Make sure you're in the correct directory")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="One-command packaging for Video2Text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Preset Quality Levels:
  best       - Large model (~3.5GB total, best accuracy)
  balanced   - Medium model (~1.2GB total, good accuracy)
  lightweight- Base model (~500MB total, fast)

Examples:
  python package_app.py --quality best
  python package_app.py --quality balanced --gui enhanced
  python package_app.py --models large medium small --gui qt
        """
    )

    # Preset quality levels
    parser.add_argument(
        '--quality',
        choices=['best', 'balanced', 'lightweight'],
        help='Preset quality level (recommended)'
    )

    # Or custom models
    parser.add_argument(
        '--models',
        nargs='+',
        choices=['tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en',
                 'medium', 'medium.en', 'large'],
        help='Custom model selection'
    )

    # GUI choice
    parser.add_argument(
        '--gui',
        choices=['qt', 'enhanced', 'original'],
        default='qt',
        help='GUI version (default: qt)'
    )

    # Build mode
    parser.add_argument(
        '--onefile',
        action='store_true',
        help='Build single file instead of directory'
    )

    # Skip steps
    parser.add_argument(
        '--skip-models',
        action='store_true',
        help='Skip model bundling (use existing)'
    )

    parser.add_argument(
        '--skip-build',
        action='store_true',
        help='Skip build (only bundle models)'
    )

    args = parser.parse_args()

    # Determine models to bundle
    if args.quality:
        quality_presets = {
            'best': ['large'],
            'balanced': ['medium'],
            'lightweight': ['base']
        }
        models = quality_presets[args.quality]
        quality_name = args.quality.upper()
    elif args.models:
        models = args.models
        quality_name = 'CUSTOM'
    else:
        print_color("Error: Specify --quality or --models", Colors.RED)
        parser.print_help()
        sys.exit(1)

    # Print configuration
    print_header("VIDEO2TEXT - ONE-COMMAND PACKAGER")

    print_color("Configuration:", Colors.BOLD)
    print(f"  Quality Preset: {quality_name}")
    print(f"  Models: {', '.join(models)}")
    print(f"  GUI Version: {args.gui}")
    print(f"  Build Mode: {'Single File' if args.onefile else 'Directory'}")
    print()

    # Estimate final size
    size_estimates = {
        'tiny': 0.04, 'tiny.en': 0.04,
        'base': 0.07, 'base.en': 0.07,
        'small': 0.24, 'small.en': 0.24,
        'medium': 0.77, 'medium.en': 0.77,
        'large': 3.0
    }

    base_size = 0.4  # Python + deps + FFmpeg
    total_size = base_size + sum(size_estimates.get(m, 0) for m in models)

    print_color(f"Estimated package size: ~{total_size:.1f} GB", Colors.YELLOW)
    print()

    # Confirm
    response = input("Continue? [Y/n]: ").strip().lower()
    if response and response != 'y':
        print("Cancelled.")
        sys.exit(0)

    # Step 1: Bundle models
    if not args.skip_models:
        cmd = [
            sys.executable,
            'bundle_models_enhanced.py',
            '--models'
        ] + models

        if not run_command(cmd, "Bundling Whisper models"):
            print_color("\n❌ Model bundling failed!", Colors.RED)
            sys.exit(1)
    else:
        print_color("\n⏭  Skipping model bundling (using existing)", Colors.YELLOW)

    # Step 2: Build standalone package
    if not args.skip_build:
        cmd = [
            sys.executable,
            'build_standalone_enhanced.py',
            '--bundle-all',
            '--gui', args.gui
        ]

        if args.onefile:
            cmd.append('--onefile')

        if not run_command(cmd, "Building standalone package"):
            print_color("\n❌ Build failed!", Colors.RED)
            sys.exit(1)
    else:
        print_color("\n⏭  Skipping build (models only)", Colors.YELLOW)
        print_header("MODELS BUNDLED!")
        print_color("Next step: Run the build command:", Colors.BOLD)
        print(f"  python build_standalone_enhanced.py --bundle-all --gui {args.gui}")
        sys.exit(0)

    # Success!
    print_header("🎉 PACKAGING COMPLETE!")

    app_name = f"Video2Text_{args.gui.capitalize()}"
    dist_path = Path('dist') / app_name

    print_color("Your self-contained application is ready!", Colors.GREEN)
    print()
    print_color("📦 Package Details:", Colors.BOLD)
    print(f"   Location: {dist_path.absolute()}")
    print(f"   Models: {', '.join(models)}")
    print(f"   GUI: {args.gui}")
    print()

    # Calculate actual size
    if dist_path.exists():
        total_bytes = sum(f.stat().st_size for f in dist_path.rglob('*') if f.is_file())
        total_gb = total_bytes / (1024**3)
        print_color(f"   Actual Size: {total_gb:.2f} GB", Colors.GREEN)
        print()

    print_color("📋 Distribution Steps:", Colors.BOLD)
    print("   1. Test the application:")
    print(f"      cd {dist_path}")
    print(f"      ./{app_name}")
    print()
    print("   2. Create distribution archive:")
    print(f"      zip -r Video2Text_{quality_name}.zip {dist_path.name}")
    print()
    print("   3. Share with users - they just unzip and run!")
    print()

    print_color("✨ What users get:", Colors.BOLD)
    print("   ✓ No Python installation needed")
    print("   ✓ No dependencies needed")
    print("   ✓ No FFmpeg installation needed")
    print("   ✓ Models pre-loaded (works offline)")
    print("   ✓ Just download, extract, and run!")
    print()

    print_color("See PACKAGING_GUIDE.md for distribution tips!", Colors.YELLOW)
    print()


if __name__ == "__main__":
    main()
