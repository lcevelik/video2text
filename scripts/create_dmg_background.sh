#!/bin/bash

# Create custom DMG background from logo
# Fades logo to 20% opacity and scales to 600x400

set -e

LOGO_FILE="$1"
OUTPUT_FILE="$2"

if [ -z "$LOGO_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: $0 <input_logo.png> <output_background.png>"
    exit 1
fi

if [ ! -f "$LOGO_FILE" ]; then
    echo "Error: Logo file not found: $LOGO_FILE"
    exit 1
fi

echo "Creating DMG background from $LOGO_FILE..."

# Check if ImageMagick is available
if command -v magick &> /dev/null; then
    echo "Using ImageMagick..."
    # Create 600x400 background, scale logo to fit, and set opacity to 20%
    magick "$LOGO_FILE" \
        -resize 600x400 \
        -background white \
        -gravity center \
        -extent 600x400 \
        -alpha set \
        -channel A \
        -evaluate multiply 0.2 \
        +channel \
        "$OUTPUT_FILE"
    echo "✓ Background created: $OUTPUT_FILE"
else
    echo "ImageMagick not found. Using sips (basic version)..."
    # Create a copy and resize (sips doesn't support opacity, so we'll note this limitation)
    sips -z 400 600 "$LOGO_FILE" --out "$OUTPUT_FILE"
    echo "⚠ Note: sips doesn't support opacity. Consider installing ImageMagick:"
    echo "  brew install imagemagick"
    echo "✓ Background created (without opacity): $OUTPUT_FILE"
fi
