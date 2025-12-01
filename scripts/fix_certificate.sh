#!/bin/bash
# Fix certificate installation - ensure private key is accessible

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "Fixing Certificate Installation"
echo "=========================================="
echo ""

# Check if certificate exists
CERT_NAME="Developer ID Application: Libor Cevelik (8BLXD56D6K)"

echo -e "${YELLOW}Step 1: Checking certificate in keychain...${NC}"

# Check if certificate exists
if security find-certificate -c "$CERT_NAME" -a 2>/dev/null | grep -q "keychain"; then
    echo -e "${GREEN}✅ Certificate found in keychain${NC}"
else
    echo -e "${RED}❌ Certificate not found${NC}"
    echo ""
    echo "Please make sure you:"
    echo "1. Downloaded the certificate from Apple Developer portal"
    echo "2. Double-clicked the .cer file to install it"
    echo ""
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 2: Checking for private key...${NC}"

# Check if private key exists
KEYCHAIN_PATH="$HOME/Library/Keychains/login.keychain-db"

# Try to access the certificate with private key
if security find-identity -v -p codesigning 2>&1 | grep -q "$CERT_NAME"; then
    echo -e "${GREEN}✅ Certificate is available for code signing!${NC}"
    echo ""
    echo "Available identity:"
    security find-identity -v -p codesigning | grep "$CERT_NAME"
    echo ""
    
    # Set environment variable
    IDENTITY="$CERT_NAME"
    echo -e "${YELLOW}Step 3: Setting CODESIGN_IDENTITY...${NC}"
    
    # Add to .zshrc if not already there
    if ! grep -q "CODESIGN_IDENTITY.*$CERT_NAME" ~/.zshrc 2>/dev/null; then
        echo "" >> ~/.zshrc
        echo "# FonixFlow Code Signing" >> ~/.zshrc
        echo "export CODESIGN_IDENTITY=\"$IDENTITY\"" >> ~/.zshrc
        echo -e "${GREEN}✅ Added to ~/.zshrc${NC}"
    else
        # Update existing
        sed -i '' "s|export CODESIGN_IDENTITY=.*|export CODESIGN_IDENTITY=\"$IDENTITY\"|" ~/.zshrc
        echo -e "${GREEN}✅ Updated ~/.zshrc${NC}"
    fi
    
    # Set for current session
    export CODESIGN_IDENTITY="$IDENTITY"
    
    echo ""
    echo -e "${GREEN}✅ Setup complete!${NC}"
    echo ""
    echo "CODESIGN_IDENTITY is now:"
    echo "  $IDENTITY"
    echo ""
    echo "Run: source ~/.zshrc (or restart terminal)"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Certificate found but private key is missing${NC}"
    echo ""
    echo "This usually means:"
    echo "1. The certificate was installed without the private key"
    echo "2. The private key is in a different keychain"
    echo ""
    echo "Solution:"
    echo "1. Go to Apple Developer portal"
    echo "2. Download the certificate again (it should include the private key)"
    echo "3. Make sure you're downloading from the same Mac where you created the CSR"
    echo ""
    echo "OR if you have the certificate on another Mac:"
    echo "1. Export both certificate AND private key from that Mac"
    echo "2. Import both on this Mac"
    echo ""
    
    # Check Keychain Access
    echo "Opening Keychain Access to check..."
    open -a "Keychain Access"
    echo ""
    echo "In Keychain Access:"
    echo "1. Select 'login' keychain"
    echo "2. Click 'My Certificates'"
    echo "3. Look for '$CERT_NAME'"
    echo "4. Expand it - you should see a private key underneath"
    echo "5. If no private key, you need to re-download/import the certificate"
    echo ""
    exit 1
fi
