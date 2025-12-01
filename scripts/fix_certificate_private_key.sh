#!/bin/bash
# Fix certificate by ensuring private key is available

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Fix Certificate Private Key Issue${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

CERT_NAME="Developer ID Application: Libor Cevelik (8BLXD56D6K)"

echo -e "${YELLOW}Problem detected:${NC}"
echo "Certificate is installed but missing private key."
echo "This happens when certificate is downloaded without the private key."
echo ""

echo -e "${YELLOW}Solution Options:${NC}"
echo ""
echo "Option 1: Create CSR on THIS Mac (Recommended)"
echo "  - Create a new CSR on this Mac"
echo "  - Upload to Apple Developer portal"
echo "  - Download new certificate (will have private key)"
echo ""
echo "Option 2: Export from Another Mac"
echo "  - If certificate was created on another Mac"
echo "  - Export certificate + private key from that Mac"
echo "  - Import on this Mac"
echo ""

read -p "Which option? (1 or 2): " OPTION

if [ "$OPTION" = "1" ]; then
    echo ""
    echo -e "${YELLOW}Option 1: Create CSR on This Mac${NC}"
    echo ""
    echo "Step 1: Opening Keychain Access to create CSR..."
    open -a "Keychain Access"
    echo ""
    echo "In Keychain Access:"
    echo "1. Menu: Keychain Access → Certificate Assistant → Request a Certificate..."
    echo "2. Fill in:"
    echo "   - User Email: libor.cevelik@me.com"
    echo "   - Common Name: Libor Cevelik"
    echo "   - CA Email: (leave empty)"
    echo "   - Request is: 'Saved to disk'"
    echo "3. Click 'Continue'"
    echo "4. Save to Desktop as 'CertificateSigningRequest.certSigningRequest'"
    echo ""
    read -p "Press Enter after you've created the CSR file..."
    
    echo ""
    echo "Step 2: Opening Apple Developer portal..."
    open "https://developer.apple.com/account/resources/certificates/add"
    echo ""
    echo "In the browser:"
    echo "1. Select 'Developer ID Application'"
    echo "2. Click 'Continue'"
    echo "3. Upload the CSR file from Desktop"
    echo "4. Download the new certificate"
    echo ""
    read -p "Press Enter after you've downloaded the new certificate..."
    
    echo ""
    echo "Step 3: Removing old certificate (without private key)..."
    # Try to remove old certificate
    security delete-certificate -c "$CERT_NAME" 2>/dev/null || echo "Old certificate removal attempted"
    
    echo ""
    echo "Step 4: Installing new certificate (with private key)..."
    CERT_FILE="$HOME/Downloads/developerID_application.cer"
    
    if [ ! -f "$CERT_FILE" ]; then
        read -p "Enter path to downloaded .cer file: " CERT_FILE
    fi
    
    if [ -f "$CERT_FILE" ]; then
        open "$CERT_FILE"
        echo -e "${GREEN}✅ Installing certificate...${NC}"
        sleep 3
    else
        echo -e "${RED}❌ Certificate file not found${NC}"
        exit 1
    fi
    
elif [ "$OPTION" = "2" ]; then
    echo ""
    echo -e "${YELLOW}Option 2: Export from Another Mac${NC}"
    echo ""
    echo "On the Mac where the certificate was originally created:"
    echo ""
    echo "1. Open Keychain Access"
    echo "2. Select 'login' keychain → 'My Certificates'"
    echo "3. Find 'Developer ID Application: Libor Cevelik (8BLXD56D6K)'"
    echo "4. Expand it to see the private key"
    echo "5. Right-click the certificate → 'Export'"
    echo "6. Save as .p12 file (will ask for password)"
    echo "7. Transfer .p12 file to this Mac"
    echo ""
    read -p "Press Enter after you have the .p12 file on this Mac..."
    
    echo ""
    read -p "Enter path to .p12 file: " P12_FILE
    
    if [ -f "$P12_FILE" ]; then
        echo ""
        echo "Removing old certificate..."
        security delete-certificate -c "$CERT_NAME" 2>/dev/null || true
        
        echo ""
        read -sp "Enter password for .p12 file: " P12_PASSWORD
        echo ""
        
        echo "Importing certificate with private key..."
        security import "$P12_FILE" \
            -k ~/Library/Keychains/login.keychain-db \
            -P "$P12_PASSWORD" \
            -T /usr/bin/codesign
        
        echo -e "${GREEN}✅ Certificate imported${NC}"
    else
        echo -e "${RED}❌ File not found: $P12_FILE${NC}"
        exit 1
    fi
else
    echo -e "${RED}Invalid option${NC}"
    exit 1
fi

# Verify installation
echo ""
echo -e "${YELLOW}Verifying certificate installation...${NC}"
sleep 2

if security find-identity -v -p codesigning 2>&1 | grep -q "$CERT_NAME"; then
    echo -e "${GREEN}✅ Certificate is now available for code signing!${NC}"
    echo ""
    
    IDENTITY=$(security find-identity -v -p codesigning | grep "$CERT_NAME" | sed 's/.*"\(.*\)".*/\1/')
    
    echo "Setting CODESIGN_IDENTITY..."
    if ! grep -q "CODESIGN_IDENTITY.*$CERT_NAME" ~/.zshrc 2>/dev/null; then
        echo "" >> ~/.zshrc
        echo "# FonixFlow Code Signing" >> ~/.zshrc
        echo "export CODESIGN_IDENTITY=\"$IDENTITY\"" >> ~/.zshrc
    else
        sed -i '' "s|export CODESIGN_IDENTITY=.*|export CODESIGN_IDENTITY=\"$IDENTITY\"|" ~/.zshrc
    fi
    
    export CODESIGN_IDENTITY="$IDENTITY"
    
    echo -e "${GREEN}✅ CODESIGN_IDENTITY set!${NC}"
    echo ""
    echo "Identity: $IDENTITY"
    echo ""
    echo "Run: source ~/.zshrc (or restart terminal)"
    echo ""
else
    echo -e "${RED}❌ Certificate still not available for code signing${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure you created the CSR on THIS Mac"
    echo "2. Make sure you downloaded the certificate after uploading the CSR"
    echo "3. Check Keychain Access → My Certificates → expand certificate → should see private key"
    echo ""
fi
