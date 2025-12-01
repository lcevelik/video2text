#!/bin/bash
# Check if code signing certificates are available

echo "=========================================="
echo "Checking Code Signing Certificates"
echo "=========================================="
echo ""

# Check for certificates
CERT_OUTPUT=$(security find-identity -v -p codesigning 2>&1)

# Check for Developer ID (for distribution)
if echo "$CERT_OUTPUT" | grep -q "Developer ID Application"; then
    echo "✅ Developer ID Application certificate found!"
    echo ""
    echo "Available Developer ID certificates:"
    echo "$CERT_OUTPUT" | grep "Developer ID Application"
    echo ""
    echo "You can use these for distribution."
    echo ""
    echo "To use, set:"
    echo '  export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"'
    echo ""
else
    echo "❌ No Developer ID Application certificate found"
    echo ""
fi

# Check for Apple Development (development only)
if echo "$CERT_OUTPUT" | grep -q "Apple Development"; then
    echo "⚠️  Apple Development certificates found (development only):"
    echo "$CERT_OUTPUT" | grep "Apple Development"
    echo ""
    echo "Note: These cannot be used for distribution outside App Store."
    echo "You need a 'Developer ID Application' certificate for distribution."
    echo ""
fi

# Show all certificates
echo "All available certificates:"
echo "$CERT_OUTPUT"
echo ""

# Check if CODESIGN_IDENTITY is set
if [ -z "$CODESIGN_IDENTITY" ]; then
    echo "⚠️  CODESIGN_IDENTITY environment variable is not set"
    echo ""
    echo "To set it, run:"
    echo '  export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"'
    echo ""
    echo "Or add to ~/.zshrc for permanent setup:"
    echo '  echo "export CODESIGN_IDENTITY=\"Developer ID Application: Your Name (TEAMID)\"" >> ~/.zshrc'
    echo ""
else
    echo "✅ CODESIGN_IDENTITY is set:"
    echo "   $CODESIGN_IDENTITY"
    echo ""
    
    # Verify the identity exists
    if echo "$CERT_OUTPUT" | grep -q "$CODESIGN_IDENTITY"; then
        echo "✅ Certificate matches installed identity"
    else
        echo "⚠️  Warning: CODESIGN_IDENTITY doesn't match any installed certificate"
        echo "   Update CODESIGN_IDENTITY to match one of the certificates above"
    fi
fi

echo "=========================================="
echo ""
echo "For distribution, you need:"
echo "  - Developer ID Application certificate"
echo "  - CODESIGN_IDENTITY environment variable set"
echo ""
echo "You can still build and release without certificates,"
echo "but users will see 'unidentified developer' warning."
echo ""
