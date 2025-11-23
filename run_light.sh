#!/bin/bash
echo "========================================================"
echo "FonixFlow - Setup & Run"
echo "========================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found."
    echo "Please install Python 3 (e.g., brew install python)"
    exit 1
fi

# Create venv
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARN] FFmpeg not found."
    echo "Attempting to run dependency manager..."
    # python scripts/dependency_manager.py  <-- We haven't bundled this script in the light build bat yet
    # Ideally we should copy scripts/ too.
fi

# Run App
echo "[INFO] Starting FonixFlow..."
python app/fonixflow_qt.py
