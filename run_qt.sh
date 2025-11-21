#!/bin/bash
# Modern Qt GUI Launcher for Linux/macOS

echo "========================================"
echo "FonixFlow - Modern Qt Interface"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
echo "Checking Python version..."
python3 --version
echo ""

# Check if PySide6 is installed
if ! python3 -c "import PySide6" &> /dev/null; then
    echo "PySide6 not found. Installing..."
    pip3 install PySide6>=6.6.0
    echo ""
fi

# Launch the Qt application
echo "Starting Modern Qt Interface..."
echo ""
python3 fonixflow_qt.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with error code: $?"
    echo "Check the logs folder for details."
fi

echo ""
read -p "Press Enter to exit..."
