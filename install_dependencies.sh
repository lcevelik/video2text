#!/bin/bash
# Script to install required system dependencies for FonixFlow on Linux

set -e

echo "================================"
echo "FonixFlow Linux Dependencies Installer"
echo "================================"
echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Warning: Could not detect Linux distribution"
    DISTRO="unknown"
fi

echo "Detected distribution: $DISTRO"
echo ""

# Install based on distribution
case $DISTRO in
    ubuntu|debian)
        echo "Installing dependencies for Debian/Ubuntu..."
        sudo apt-get update
        sudo apt-get install -y \
            ffmpeg \
            libxcb-cursor0 \
            libxcb-cursor-dev
        ;;
    fedora|rhel|centos)
        echo "Installing dependencies for RHEL/CentOS/Fedora..."
        sudo yum install -y \
            ffmpeg \
            libxcb-cursor
        ;;
    arch|manjaro)
        echo "Installing dependencies for Arch Linux..."
        sudo pacman -S --noconfirm \
            ffmpeg \
            libxcb-cursor
        ;;
    *)
        echo "Unknown distribution. Please install manually:"
        echo "  - ffmpeg"
        echo "  - libxcb-cursor0 (or libxcb-cursor)"
        exit 1
        ;;
esac

echo ""
echo "================================"
echo "✓ Dependencies installed!"
echo "================================"
echo ""
echo "You can now rebuild the application:"
echo "  ./build_linux.sh"
echo ""

