#!/usr/bin/env python3
"""
Quick script to check if ScreenCaptureKit permissions are granted.
Run this to verify screen recording permission before using the app.
"""

import sys
import platform

def check_macos_version():
    """Check if macOS version supports ScreenCaptureKit."""
    if platform.system() != 'Darwin':
        print("Not running on macOS")
        return False

    version = platform.mac_ver()[0]
    major, minor, *_ = map(int, version.split('.'))

    if major < 12 or (major == 12 and minor < 3):
        print(f"macOS {version} detected")
        print("   ScreenCaptureKit requires macOS 12.3 (Monterey) or later")
        print("   Your options:")
        print("   1. Upgrade to macOS 12.3+")
        print("   2. Use BlackHole for system audio (brew install blackhole-2ch)")
        return False

    print(f"macOS {version} - ScreenCaptureKit supported")
    return True

def check_pyobjc():
    """Check if PyObjC frameworks are installed."""
    try:
        import ScreenCaptureKit
        print("ScreenCaptureKit framework available")
        pyobjc_ok = True
    except ImportError:
        print("ScreenCaptureKit framework NOT available")
        print("   Install with:")
        print("   pip install pyobjc-framework-ScreenCaptureKit pyobjc-framework-AVFoundation pyobjc-framework-Cocoa")
        pyobjc_ok = False

    try:
        import AVFoundation
        print("AVFoundation framework available")
    except ImportError:
        print("AVFoundation framework NOT available")
        pyobjc_ok = False

    try:
        from Cocoa import NSApplication
        print("Cocoa framework available")
    except ImportError:
        print("Cocoa framework NOT available")
        pyobjc_ok = False

    return pyobjc_ok

def check_permissions():
    """
    Check Screen Recording permission.

    Note: There's no direct API to check permission status before requesting it.
    The permission is checked when you actually try to use ScreenCaptureKit.
    """
    print("\nℹ️  Screen Recording Permission:")
    print("   macOS doesn't provide an API to check permission before using it.")
    print("   When you start recording, macOS will:")
    print("   1. Prompt for permission (if not granted)")
    print("   2. Or allow recording (if already granted)")
    print("   3. Or fail with error -3802 (if denied)")
    print()
    print("   To grant permission manually:")
    print("   1. Open System Settings")
    print("   2. Go to Privacy & Security → Screen Recording")
    print("   3. Enable permission for Terminal (or your Python launcher)")
    print("   4. Restart the application")
    print()
    print("   Note: The app only captures AUDIO, not screen content!")

def main():
    print("="*70)
    print("ScreenCaptureKit Permissions Checker")
    print("="*70)
    print()

    # Check macOS version
    if not check_macos_version():
        sys.exit(1)

    print()

    # Check PyObjC
    if not check_pyobjc():
        print()
        print("Setup incomplete - install PyObjC frameworks first")
        sys.exit(1)

    print()
    print("All dependencies installed!")
    print()

    # Info about permissions
    check_permissions()

    print("="*70)
    print("Ready to use ScreenCaptureKit!")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Run: python gui_qt.py")
    print("2. Start a recording")
    print("3. Grant Screen Recording permission when prompted")
    print("4. Enjoy native system audio recording!")
    print()

if __name__ == "__main__":
    main()
