#!/bin/bash
# Enhanced Video to Text Launcher for Linux/macOS
# This script launches the enhanced version of the application

echo "========================================"
echo "Video/Audio to Text - Enhanced Version"
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

# Check if required files exist
if [ ! -f "main_enhanced.py" ]; then
    echo "ERROR: main_enhanced.py not found!"
    echo "Make sure you're running this script from the correct directory."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Launch the application
echo "Starting application..."
echo ""
python3 main_enhanced.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with error code: $?"
    echo "Check the logs folder for details."
fi

echo ""
read -p "Press Enter to exit..."
