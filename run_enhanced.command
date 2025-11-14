#!/bin/bash
# Enhanced Video to Text Launcher for macOS (double-clickable)
# This script can be double-clicked in Finder

# Change to script directory
cd "$(dirname "$0")"

# Make the script executable (in case it wasn't)
chmod +x "$0"

# Run the main launcher
./run_enhanced.sh
