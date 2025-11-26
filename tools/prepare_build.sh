#!/bin/bash
# Prepare build by encoding license file
# Run this before building the distributable app

set -e

echo "=================================================="
echo "FonixFlow Build Preparation"
echo "=================================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if licenses.txt exists
if [ ! -f "$PROJECT_ROOT/licenses.txt" ]; then
    echo "❌ Error: licenses.txt not found in project root"
    echo "   Create licenses.txt with one license key per line"
    exit 1
fi

echo "✓ Found licenses.txt"
echo ""

# Encode licenses.txt to licenses.dat
echo "Encoding license file..."
python3 "$SCRIPT_DIR/license_encoder.py" encode "$PROJECT_ROOT/licenses.txt" "$PROJECT_ROOT/licenses.dat"
echo ""

# Remove plaintext licenses.txt from build (it will stay in git, but not in dist)
echo "✓ Encoded licenses.dat created"
echo "  The plaintext licenses.txt will NOT be included in the build"
echo "  (PyInstaller will bundle licenses.dat instead)"
echo ""

echo "=================================================="
echo "Build preparation complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run PyInstaller: pyinstaller fonixflow_qt.spec"
echo "  2. The app will use the encoded licenses.dat file"
echo "  3. Test license validation in the built app"
echo ""
