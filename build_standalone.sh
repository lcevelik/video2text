#!/bin/bash
# Build FonixFlow as a standalone macOS application
# with ALL dependencies bundled (ffmpeg, Whisper models, etc.)

set -e  # Exit on error

echo "========================================="
echo "FonixFlow Standalone Build Script"
echo "========================================="
echo ""

# Check for required tools
echo "Checking required tools..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

if ! command -v pyinstaller &> /dev/null; then
    echo "❌ Error: pyinstaller not found. Install with: pip3 install pyinstaller"
    exit 1
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: ffmpeg not found. Install with: brew install ffmpeg"
    echo "   (App will work but won't be able to process video files)"
else
    echo "✓ ffmpeg found: $(which ffmpeg)"
fi

# Check for Whisper models
echo ""
echo "Checking Whisper models..."
WHISPER_CACHE="$HOME/.cache/whisper"
if [ -d "$WHISPER_CACHE" ]; then
    MODEL_COUNT=$(ls -1 "$WHISPER_CACHE"/*.pt 2>/dev/null | wc -l)
    if [ "$MODEL_COUNT" -gt 0 ]; then
        echo "✓ Found $MODEL_COUNT Whisper model(s) in cache"
        ls -lh "$WHISPER_CACHE"/*.pt | awk '{print "  -", $9, "("$5")"}'
    else
        echo "⚠️  No Whisper models found in cache"
        echo "   Models will be downloaded on first use in the app"
    fi
else
    echo "⚠️  Whisper cache directory not found"
    echo "   Models will be downloaded on first use in the app"
fi

# Optional: Download commonly used models
echo ""
read -p "Download Whisper models before building? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Which models would you like to download?"
    echo "1) tiny (72 MB) - Fast, basic quality"
    echo "2) base (139 MB) - Balanced (Recommended)"
    echo "3) small (461 MB) - Better quality"
    echo "4) medium (1.4 GB) - High quality"
    echo "5) large (2.9 GB) - Best quality"
    echo "6) All of the above"
    echo "0) Skip download"
    read -p "Enter choice (0-6): " MODEL_CHOICE

    case $MODEL_CHOICE in
        1) MODELS="tiny" ;;
        2) MODELS="base" ;;
        3) MODELS="small" ;;
        4) MODELS="medium" ;;
        5) MODELS="large-v3" ;;
        6) MODELS="tiny base small medium large-v3" ;;
        *) MODELS="" ;;
    esac

    if [ -n "$MODELS" ]; then
        echo "Downloading models: $MODELS"
        python3 -c "
import whisper
models = '$MODELS'.split()
for model in models:
    print(f'Downloading {model}...')
    whisper.load_model(model)
    print(f'✓ {model} downloaded')
"
        echo "✓ Models downloaded successfully"
    fi
fi

# Clean previous build
echo ""
echo "Cleaning previous build..."
rm -rf build dist
echo "✓ Cleaned"

# Build with PyInstaller
echo ""
echo "Building standalone app..."
echo "This may take several minutes..."
pyinstaller FonixFlow.spec

# Check if build succeeded
if [ ! -d "dist/FonixFlow.app" ]; then
    echo "❌ Build failed - FonixFlow.app not found"
    exit 1
fi

# Clean up resource forks
echo ""
echo "Cleaning up resource forks..."
find dist/FonixFlow.app -name "._*" -delete 2>/dev/null || true

# Get app size
APP_SIZE=$(du -sh dist/FonixFlow.app | cut -f1)

echo ""
echo "========================================="
echo "✓ Build complete!"
echo "========================================="
echo ""
echo "App location: dist/FonixFlow.app"
echo "App size: $APP_SIZE"
echo ""
echo "To test: open dist/FonixFlow.app"
echo "To share: cd dist && zip -r FonixFlow.zip FonixFlow.app"
echo ""
echo "Bundled resources:"
if [ -d "dist/FonixFlow.app/Contents/Frameworks/bin" ]; then
    echo "  ✓ ffmpeg/ffprobe binaries (Contents/Frameworks/bin/)"
fi
if [ -d "dist/FonixFlow.app/Contents/Resources/cache/whisper" ]; then
    MODEL_COUNT=$(ls -1 dist/FonixFlow.app/Contents/Resources/cache/whisper/*.pt 2>/dev/null | wc -l)
    echo "  ✓ $MODEL_COUNT Whisper model(s) (Contents/Resources/cache/whisper/)"
    ls -lh dist/FonixFlow.app/Contents/Resources/cache/whisper/*.pt | awk '{print "    -", $9, "("$5")"}'
fi
echo ""
