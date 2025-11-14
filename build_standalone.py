"""
Standalone Build Script using PyInstaller

This script creates a standalone executable that includes:
- Python runtime
- All dependencies
- Bundled tiny model (optional)
- No installation required

Usage:
    python build_standalone.py [--include-model] [--onefile]

Options:
    --include-model: Bundle tiny model with the executable
    --onefile: Create single executable file (slower startup)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import platform


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("❌ PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        return False


def build_executable(include_model=False, onefile=False):
    """Build standalone executable using PyInstaller."""

    print("=" * 60)
    print("Building Standalone Video2Text Application")
    print("=" * 60)
    print()

    if not check_pyinstaller():
        return False

    # Determine platform-specific settings
    is_windows = platform.system() == "Windows"
    is_mac = platform.system() == "Darwin"
    is_linux = platform.system() == "Linux"

    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=Video2Text",
        "--windowed" if is_windows or is_mac else "--console",
        "--clean",
        "--noconfirm",
    ]

    # Add icon if available
    if is_windows and os.path.exists("icon.ico"):
        cmd.extend(["--icon=icon.ico"])
    elif is_mac and os.path.exists("icon.icns"):
        cmd.extend(["--icon=icon.icns"])

    # Onefile or onedir
    if onefile:
        cmd.append("--onefile")
        print("📦 Building single-file executable (slower startup)")
    else:
        cmd.append("--onedir")
        print("📦 Building directory-based executable (faster startup)")

    # Add data files
    print("📁 Including data files...")

    # Include README
    if os.path.exists("README.md"):
        cmd.extend(["--add-data", f"README.md{os.pathsep}."])

    # Include bundled model if requested
    if include_model:
        if os.path.exists("bundled_models"):
            print("✅ Including bundled tiny model")
            cmd.extend(["--add-data", f"bundled_models{os.pathsep}bundled_models"])
        else:
            print("⚠️  Bundled model not found. Run 'python bundle_model.py' first.")
            print("   Continuing without bundled model...")

    # Hidden imports for Whisper and dependencies
    print("📚 Configuring dependencies...")
    hidden_imports = [
        "whisper",
        "torch",
        "torchaudio",
        "numpy",
        "scipy",
        "sounddevice",
        "tkinter",
        "PIL",
        "ffmpeg"
    ]

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # Collect submodules
    cmd.extend([
        "--collect-submodules=whisper",
        "--collect-submodules=torch",
        "--collect-data=whisper",
        "--collect-data=torch",
    ])

    # Main entry point
    cmd.append("main_enhanced.py")

    print("\n🔨 Building executable...")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=False)

        print("\n" + "=" * 60)
        print("✅ Build completed successfully!")
        print("=" * 60)
        print()

        # Show output location
        output_dir = Path("dist/Video2Text")
        if onefile:
            executable = "dist/Video2Text.exe" if is_windows else "dist/Video2Text"
            print(f"📦 Executable: {executable}")
        else:
            print(f"📁 Application directory: {output_dir}")
            if is_windows:
                print(f"🚀 Run: {output_dir}/Video2Text.exe")
            else:
                print(f"🚀 Run: {output_dir}/Video2Text")

        print()
        print("Distribution checklist:")
        print("  ✓ Include the entire dist/Video2Text folder")
        if not include_model:
            print("  ⚠️  Users will need internet for first model download")
        else:
            print("  ✓ Tiny model included for offline use")
        print("  ✓ FFmpeg must be in PATH on user's system")
        print()

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build standalone Video2Text executable"
    )
    parser.add_argument(
        "--include-model",
        action="store_true",
        help="Bundle tiny model with the executable"
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Create single executable file (slower startup)"
    )

    args = parser.parse_args()

    success = build_executable(
        include_model=args.include_model,
        onefile=args.onefile
    )

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
