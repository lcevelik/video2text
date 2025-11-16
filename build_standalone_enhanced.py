"""
Enhanced Standalone Build Script - 100% Self-Contained

Creates a FULLY standalone application with:
- Python runtime bundled
- All dependencies bundled
- FFmpeg binaries bundled (no PATH requirements!)
- Whisper models pre-loaded
- Zero installation required
- Works completely offline

Usage:
    # Build with bundled FFmpeg + models (RECOMMENDED)
    python build_standalone_enhanced.py --bundle-all --gui qt

    # Build with specific options
    python build_standalone_enhanced.py --bundle-ffmpeg --bundle-models --gui enhanced

    # Build minimal (still needs FFmpeg in PATH)
    python build_standalone_enhanced.py --gui qt

Options:
    --gui: Choose GUI version (qt, enhanced, or original)
    --bundle-ffmpeg: Include FFmpeg binaries
    --bundle-models: Include pre-downloaded models
    --bundle-all: Bundle everything (FFmpeg + models)
    --onefile: Single executable (slower) vs folder (faster)
"""

import os
import sys
import subprocess
import argparse
import platform
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path

# Color output
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

def print_step(step_num, total_steps, text):
    """Print a step."""
    print_color(f"[{step_num}/{total_steps}] {text}", Colors.BLUE)


# FFmpeg download URLs
FFMPEG_URLS = {
    'Windows': 'https://github.com/GyanD/codexffmpeg/releases/download/7.1/ffmpeg-7.1-full_build.zip',
    'Linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz',
    'Darwin': 'https://evermeet.cx/ffmpeg/getrelease/zip'  # macOS
}


def check_dependencies():
    """Check if required tools are installed."""
    print_step(1, 7, "Checking dependencies...")

    missing = []

    # Check PyInstaller
    try:
        import PyInstaller
        print_color("  ✓ PyInstaller found", Colors.GREEN)
    except ImportError:
        print_color("  ✗ PyInstaller not found", Colors.RED)
        missing.append("pyinstaller")

    # Check core dependencies
    try:
        import whisper
        print_color("  ✓ Whisper found", Colors.GREEN)
    except ImportError:
        print_color("  ✗ Whisper not found", Colors.RED)
        missing.append("openai-whisper")

    try:
        import torch
        print_color("  ✓ PyTorch found", Colors.GREEN)
    except ImportError:
        print_color("  ✗ PyTorch not found", Colors.RED)
        missing.append("torch")

    if missing:
        print_color(f"\n❌ Missing dependencies: {', '.join(missing)}", Colors.RED)
        print_color(f"Install with: pip install {' '.join(missing)}", Colors.YELLOW)
        return False

    print_color("\n✓ All dependencies satisfied\n", Colors.GREEN)
    return True


def download_ffmpeg(platform_name, output_dir="ffmpeg_bundle"):
    """Download FFmpeg binaries for the current platform."""
    print_step(2, 7, "Downloading FFmpeg binaries...")

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    if platform_name not in FFMPEG_URLS:
        print_color(f"  ✗ No FFmpeg URL for platform: {platform_name}", Colors.RED)
        return False

    url = FFMPEG_URLS[platform_name]
    filename = url.split('/')[-1]
    download_path = output_path / filename

    try:
        # Download
        print(f"  Downloading from: {url}")
        print(f"  This may take a few minutes...")

        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                print(f"\r  Progress: {percent:.1f}%", end='')

        urllib.request.urlretrieve(url, download_path, progress_hook)
        print()  # New line after progress

        print_color(f"  ✓ Downloaded: {filename}", Colors.GREEN)

        # Extract
        print(f"  Extracting...")
        extract_path = output_path / "extracted"
        extract_path.mkdir(exist_ok=True)

        if filename.endswith('.zip'):
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        elif filename.endswith(('.tar.xz', '.tar.gz')):
            with tarfile.open(download_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_path)

        # Find ffmpeg and ffprobe binaries
        ffmpeg_bin = None
        ffprobe_bin = None

        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.startswith('ffmpeg') and (file == 'ffmpeg' or file == 'ffmpeg.exe'):
                    ffmpeg_bin = Path(root) / file
                if file.startswith('ffprobe') and (file == 'ffprobe' or file == 'ffprobe.exe'):
                    ffprobe_bin = Path(root) / file

        if ffmpeg_bin and ffmpeg_bin.exists():
            # Copy to bin directory
            bin_path = output_path / "bin"
            bin_path.mkdir(exist_ok=True)

            shutil.copy2(ffmpeg_bin, bin_path / ffmpeg_bin.name)
            if ffprobe_bin and ffprobe_bin.exists():
                shutil.copy2(ffprobe_bin, bin_path / ffprobe_bin.name)

            print_color(f"  ✓ FFmpeg binaries ready in: {bin_path}", Colors.GREEN)
            print()
            return True
        else:
            print_color(f"  ✗ Could not find ffmpeg binary in archive", Colors.RED)
            return False

    except Exception as e:
        print_color(f"  ✗ Failed to download FFmpeg: {e}", Colors.RED)
        return False


def prepare_models(models_dir="bundled_models"):
    """Check if models are bundled."""
    print_step(3, 7, "Checking for bundled models...")

    models_path = Path(models_dir)

    if not models_path.exists() or not list(models_path.glob("*")):
        print_color("  ⚠ No bundled models found", Colors.YELLOW)
        print(f"  Run: python bundle_models_enhanced.py --recommended")
        print(f"  (or continue without bundled models)")
        print()
        return False

    # Count model files
    model_files = list(models_path.glob("*.pt")) + list(models_path.glob("*.pth"))
    print_color(f"  ✓ Found {len(model_files)} model file(s)", Colors.GREEN)

    # List them
    for model_file in model_files:
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"    - {model_file.name} ({size_mb:.1f} MB)")

    print()
    return True


def build_executable(gui_version, bundle_ffmpeg, bundle_models, onefile):
    """Build standalone executable using PyInstaller."""
    print_step(4, 7, "Configuring PyInstaller build...")

    # Determine entry point
    entry_points = {
        'qt': 'gui_qt.py',
        'enhanced': 'main_enhanced.py',
        'original': 'main.py'
    }

    if gui_version not in entry_points:
        print_color(f"  ✗ Unknown GUI version: {gui_version}", Colors.RED)
        return False

    entry_point = entry_points[gui_version]

    if not Path(entry_point).exists():
        print_color(f"  ✗ Entry point not found: {entry_point}", Colors.RED)
        return False

    print_color(f"  ✓ GUI: {gui_version}", Colors.GREEN)
    print_color(f"  ✓ Entry point: {entry_point}", Colors.GREEN)

    # Platform detection
    is_windows = platform.system() == "Windows"
    is_mac = platform.system() == "Darwin"
    is_linux = platform.system() == "Linux"

    print(f"  ✓ Platform: {platform.system()}")

    # Build PyInstaller command
    app_name = f"Video2Text_{gui_version.capitalize()}"

    cmd = [
        "pyinstaller",
        f"--name={app_name}",
        "--clean",
        "--noconfirm",
    ]

    # Windowed or console
    if gui_version == 'qt' or gui_version == 'enhanced':
        if is_windows or is_mac:
            cmd.append("--windowed")
        else:
            cmd.append("--console")  # Linux GUI apps need console
    else:
        cmd.append("--console")

    # Onefile or onedir
    if onefile:
        cmd.append("--onefile")
        print_color("  ✓ Mode: Single file (slower startup)", Colors.YELLOW)
    else:
        cmd.append("--onedir")
        print_color("  ✓ Mode: Directory (faster startup, RECOMMENDED)", Colors.GREEN)

    print()
    print_step(5, 7, "Adding bundled resources...")

    # Add FFmpeg binaries
    if bundle_ffmpeg:
        ffmpeg_path = Path("ffmpeg_bundle/bin")
        if ffmpeg_path.exists():
            cmd.extend(["--add-binary", f"{ffmpeg_path}{os.pathsep}ffmpeg"])
            print_color("  ✓ FFmpeg binaries will be bundled", Colors.GREEN)
        else:
            print_color("  ✗ FFmpeg binaries not found!", Colors.RED)
            return False

    # Add bundled models
    if bundle_models:
        models_path = Path("bundled_models")
        if models_path.exists():
            cmd.extend(["--add-data", f"{models_path}{os.pathsep}bundled_models"])
            print_color("  ✓ Whisper models will be bundled", Colors.GREEN)
        else:
            print_color("  ⚠ Bundled models not found, skipping", Colors.YELLOW)

    # Add README
    if Path("README.md").exists():
        cmd.extend(["--add-data", f"README.md{os.pathsep}."])

    # Hidden imports
    hidden_imports = [
        "whisper",
        "torch",
        "torchaudio",
        "numpy",
        "scipy",
        "sounddevice",
        "tkinter",
        "PIL",
        "ffmpeg",
        "pydub",
        "tqdm"
    ]

    # Add PySide6 for Qt version
    if gui_version == 'qt':
        hidden_imports.extend(["PySide6", "PySide6.QtCore", "PySide6.QtWidgets", "PySide6.QtGui"])

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # Collect submodules
    cmd.extend([
        "--collect-submodules=whisper",
        "--collect-submodules=torch",
        "--collect-data=whisper",
        "--collect-data=torch",
    ])

    if gui_version == 'qt':
        cmd.extend([
            "--collect-submodules=PySide6",
            "--collect-data=PySide6",
        ])

    # Entry point
    cmd.append(entry_point)

    print()
    print_step(6, 7, "Building executable...")
    print()
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True)

        print()
        print_color("✓ Build completed successfully!", Colors.GREEN)
        print()

        return True

    except subprocess.CalledProcessError as e:
        print()
        print_color(f"✗ Build failed: {e}", Colors.RED)
        return False


def create_launcher_script(app_name, bundle_ffmpeg):
    """Create launcher script with FFmpeg path setup."""
    print_step(7, 7, "Creating launcher scripts...")

    dist_path = Path("dist") / app_name

    if not dist_path.exists():
        print_color("  ✗ Distribution directory not found", Colors.RED)
        return

    # Create launcher for bundled FFmpeg
    if bundle_ffmpeg:
        if platform.system() == "Windows":
            # Windows batch launcher
            launcher_content = f"""@echo off
REM Video2Text Launcher - Sets up FFmpeg path

REM Add bundled FFmpeg to PATH
set FFMPEG_PATH=%~dp0ffmpeg
set PATH=%FFMPEG_PATH%;%PATH%

REM Run the application
"%~dp0{app_name}.exe" %*
"""
            launcher_path = dist_path / "launch.bat"
            launcher_path.write_text(launcher_content)
            print_color(f"  ✓ Created: launch.bat", Colors.GREEN)

        else:
            # Linux/Mac bash launcher
            launcher_content = f"""#!/bin/bash
# Video2Text Launcher - Sets up FFmpeg path

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"

# Add bundled FFmpeg to PATH
export PATH="$SCRIPT_DIR/ffmpeg:$PATH"

# Run the application
"$SCRIPT_DIR/{app_name}" "$@"
"""
            launcher_path = dist_path / "launch.sh"
            launcher_path.write_text(launcher_content)
            launcher_path.chmod(0o755)
            print_color(f"  ✓ Created: launch.sh", Colors.GREEN)

    # Create README for distribution
    readme_content = f"""# Video2Text - Standalone Distribution

## What's Included

This is a FULLY SELF-CONTAINED package. No installation required!

- Python runtime ✓
- All dependencies ✓
- FFmpeg binaries ✓{"" if not bundle_ffmpeg else ""}
- Whisper models ✓ (pre-downloaded)

## How to Run

### Windows:
1. Double-click `{app_name}.exe`
   {("OR run launch.bat (if FFmpeg issues occur)" if bundle_ffmpeg else "")}

### Linux/Mac:
1. Run: `./{app_name}`
   {("OR run: ./launch.sh (if FFmpeg issues occur)" if bundle_ffmpeg else "")}

## Features

- Transcribe video/audio files
- Multiple language support (99 languages)
- GPU acceleration (if NVIDIA GPU available)
- Export to TXT, SRT, VTT formats
- Audio recording capability

## File Size

Total package size depends on bundled models:
- No models: ~500MB
- Base model: ~600MB
- Small model: ~750MB
- Medium model: ~1.3GB
- Large model: ~3.5GB

## Support

For issues, visit: https://github.com/lcevelik/video2text

## License

See LICENSE file for details.
"""

    readme_path = dist_path / "README.txt"
    readme_path.write_text(readme_content)
    print_color(f"  ✓ Created: README.txt", Colors.GREEN)
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build fully self-contained Video2Text application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Recommended: Bundle everything
  python build_standalone_enhanced.py --bundle-all --gui qt

  # Bundle FFmpeg only
  python build_standalone_enhanced.py --bundle-ffmpeg --gui enhanced

  # Minimal build (requires FFmpeg in PATH)
  python build_standalone_enhanced.py --gui qt
        """
    )

    parser.add_argument(
        '--gui',
        choices=['qt', 'enhanced', 'original'],
        default='qt',
        help='GUI version to build (default: qt)'
    )

    parser.add_argument(
        '--bundle-ffmpeg',
        action='store_true',
        help='Download and bundle FFmpeg binaries'
    )

    parser.add_argument(
        '--bundle-models',
        action='store_true',
        help='Include pre-downloaded Whisper models'
    )

    parser.add_argument(
        '--bundle-all',
        action='store_true',
        help='Bundle both FFmpeg and models (RECOMMENDED)'
    )

    parser.add_argument(
        '--onefile',
        action='store_true',
        help='Create single executable file (slower startup)'
    )

    args = parser.parse_args()

    # Handle --bundle-all
    if args.bundle_all:
        args.bundle_ffmpeg = True
        args.bundle_models = True

    # Print header
    print_header("VIDEO2TEXT - ENHANCED STANDALONE BUILDER")

    print_color("Configuration:", Colors.BOLD)
    print(f"  GUI Version: {args.gui}")
    print(f"  Bundle FFmpeg: {'Yes' if args.bundle_ffmpeg else 'No'}")
    print(f"  Bundle Models: {'Yes' if args.bundle_models else 'No'}")
    print(f"  Build Mode: {'Single File' if args.onefile else 'Directory'}")
    print()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Download FFmpeg if requested
    if args.bundle_ffmpeg:
        if not download_ffmpeg(platform.system()):
            print_color("\n⚠ FFmpeg download failed, continuing without it", Colors.YELLOW)
            args.bundle_ffmpeg = False

    # Check for bundled models
    if args.bundle_models:
        if not prepare_models():
            print_color("\n⚠ No bundled models found, continuing without them", Colors.YELLOW)
            args.bundle_models = False

    # Build executable
    if not build_executable(
        args.gui,
        args.bundle_ffmpeg,
        args.bundle_models,
        args.onefile
    ):
        sys.exit(1)

    # Create launcher scripts
    app_name = f"Video2Text_{args.gui.capitalize()}"
    create_launcher_script(app_name, args.bundle_ffmpeg)

    # Final summary
    print_header("BUILD COMPLETE!")

    output_dir = Path("dist") / app_name
    print_color("📦 Distribution Package:", Colors.BOLD)
    print(f"   Location: {output_dir.absolute()}")
    print()

    print_color("✓ What's included:", Colors.GREEN)
    print("   • Python runtime")
    print("   • All Python dependencies")
    if args.bundle_ffmpeg:
        print("   • FFmpeg binaries")
    if args.bundle_models:
        print("   • Pre-downloaded Whisper models")
    print()

    print_color("📋 Next Steps:", Colors.BOLD)
    print("   1. Test the application:")
    if platform.system() == "Windows":
        print(f"      cd dist\\{app_name}")
        print(f"      {app_name}.exe")
    else:
        print(f"      cd dist/{app_name}")
        print(f"      ./{app_name}")
    print()
    print(f"   2. Distribute the ENTIRE '{output_dir.name}' folder")
    print("   3. Users can run without any installation!")
    print()

    if not args.bundle_ffmpeg:
        print_color("⚠ NOTE: Users will need FFmpeg in their PATH", Colors.YELLOW)
        print("  Rebuild with --bundle-ffmpeg to include it")
        print()

    if not args.bundle_models:
        print_color("⚠ NOTE: Models will download on first use", Colors.YELLOW)
        print("  Run: python bundle_models_enhanced.py --recommended")
        print("  Then rebuild with --bundle-models")
        print()

    print_color("🎉 Ready for distribution!", Colors.GREEN)
    print()


if __name__ == "__main__":
    main()
