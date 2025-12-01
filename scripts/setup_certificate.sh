#!/bin/bash
# Interactive certificate setup helper

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Code Signing Certificate Setup${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Step 1: Check current certificates
echo -e "${YELLOW}Step 1: Checking current certificates...${NC}"
CERT_OUTPUT=$(security find-identity -v -p codesigning 2>&1)

if echo "$CERT_OUTPUT" | grep -q "Developer ID Application"; then
    echo -e "${GREEN}✅ Developer ID Application certificate found!${NC}"
    echo ""
    echo "Available certificates:"
    echo "$CERT_OUTPUT" | grep "Developer ID Application"
    echo ""
    
    # Ask if they want to use existing
    read -p "Do you want to use an existing certificate? (y/n): " USE_EXISTING
    if [ "$USE_EXISTING" = "y" ] || [ "$USE_EXISTING" = "Y" ]; then
        echo ""
        echo "Available Developer ID certificates:"
        echo "$CERT_OUTPUT" | grep "Developer ID Application" | nl
        echo ""
        read -p "Enter the number of the certificate to use: " CERT_NUM
        SELECTED_CERT=$(echo "$CERT_OUTPUT" | grep "Developer ID Application" | sed -n "${CERT_NUM}p" | sed 's/.*"\(.*\)".*/\1/')
        
        if [ -n "$SELECTED_CERT" ]; then
            echo ""
            echo -e "${GREEN}Selected: $SELECTED_CERT${NC}"
            echo ""
            echo "Setting CODESIGN_IDENTITY..."
            echo "export CODESIGN_IDENTITY=\"$SELECTED_CERT\"" >> ~/.zshrc
            export CODESIGN_IDENTITY="$SELECTED_CERT"
            echo -e "${GREEN}✅ CODESIGN_IDENTITY set!${NC}"
            echo ""
            echo "Run: source ~/.zshrc (or restart terminal) to make it permanent"
            echo ""
            exit 0
        fi
    fi
else
    echo -e "${RED}❌ No Developer ID Application certificate found${NC}"
    echo ""
    if echo "$CERT_OUTPUT" | grep -q "Apple Development"; then
        echo -e "${YELLOW}⚠️  You have Apple Development certificates (development only)${NC}"
        echo "You need a 'Developer ID Application' certificate for distribution."
        echo ""
    fi
fi

# Step 2: Open Apple Developer Portal
echo -e "${YELLOW}Step 2: Opening Apple Developer Portal...${NC}"
echo ""
echo "You need to:"
echo "1. Sign in to Apple Developer portal"
echo "2. Go to Certificates section"
echo "3. Create or download 'Developer ID Application' certificate"
echo ""
read -p "Press Enter to open Apple Developer portal..."
open "https://developer.apple.com/account/resources/certificates/list"
echo ""

# Step 3: Check if certificate exists in portal
echo -e "${YELLOW}Step 3: Check if certificate exists${NC}"
echo ""
echo "In the browser, look for:"
echo "  ✅ 'Developer ID Application' certificate"
echo ""
read -p "Do you see a 'Developer ID Application' certificate? (y/n): " HAS_CERT

if [ "$HAS_CERT" = "y" ] || [ "$HAS_CERT" = "Y" ]; then
    # Step 4: Download existing certificate
    echo ""
    echo -e "${YELLOW}Step 4: Download the certificate${NC}"
    echo ""
    echo "1. Click on the 'Developer ID Application' certificate"
    echo "2. Click 'Download' button"
    echo "3. The file will download as 'developerID_application.cer'"
    echo ""
    read -p "Press Enter after you've downloaded the certificate..."
    
    # Step 5: Install certificate
    echo ""
    echo -e "${YELLOW}Step 5: Install the certificate${NC}"
    echo ""
    CERT_FILE="$HOME/Downloads/developerID_application.cer"
    
    if [ ! -f "$CERT_FILE" ]; then
        echo "Certificate file not found in Downloads."
        read -p "Enter the full path to the .cer file: " CERT_FILE
    fi
    
    if [ -f "$CERT_FILE" ]; then
        echo "Installing certificate..."
        open "$CERT_FILE"
        echo -e "${GREEN}✅ Certificate installation started${NC}"
        echo ""
        echo "The certificate should now be in your Keychain."
        sleep 2
    else
        echo -e "${RED}❌ Certificate file not found: $CERT_FILE${NC}"
        echo "Please download the certificate and run this script again."
        exit 1
    fi
else
    # Step 4: Create new certificate
    echo ""
    echo -e "${YELLOW}Step 4: Create new Developer ID Application certificate${NC}"
    echo ""
    echo "Opening certificate creation page..."
    open "https://developer.apple.com/account/resources/certificates/add"
    echo ""
    echo "In the browser:"
    echo "1. Under 'Software' section, select 'Developer ID Application'"
    echo "2. Click 'Continue'"
    echo "3. Follow the instructions"
    echo ""
    read -p "Press Enter when you're ready to create CSR (Certificate Signing Request)..."
    
    # Step 5: Create CSR
    echo ""
    echo -e "${YELLOW}Step 5: Create Certificate Signing Request (CSR)${NC}"
    echo ""
    echo "Opening Keychain Access..."
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
    
    # Step 6: Upload CSR
    echo ""
    echo -e "${YELLOW}Step 6: Upload CSR to Apple${NC}"
    echo ""
    echo "Back in the browser (certificate creation page):"
    echo "1. Click 'Choose File'"
    echo "2. Select the CSR file from Desktop"
    echo "3. Click 'Continue'"
    echo "4. Download the generated certificate"
    echo ""
    read -p "Press Enter after you've downloaded the certificate..."
    
    # Step 7: Install certificate
    echo ""
    echo -e "${YELLOW}Step 7: Install the certificate${NC}"
    echo ""
    CERT_FILE="$HOME/Downloads/developerID_application.cer"
    
    if [ ! -f "$CERT_FILE" ]; then
        echo "Certificate file not found in Downloads."
        read -p "Enter the full path to the .cer file: " CERT_FILE
    fi
    
    if [ -f "$CERT_FILE" ]; then
        echo "Installing certificate..."
        open "$CERT_FILE"
        echo -e "${GREEN}✅ Certificate installation started${NC}"
        echo ""
        echo "The certificate should now be in your Keychain."
        sleep 2
    else
        echo -e "${RED}❌ Certificate file not found: $CERT_FILE${NC}"
        echo "Please download the certificate and run this script again."
        exit 1
    fi
fi

# Step 8: Verify installation
echo ""
echo -e "${YELLOW}Step 8: Verifying certificate installation...${NC}"
sleep 3  # Give Keychain time to process

CERT_OUTPUT=$(security find-identity -v -p codesigning 2>&1)

if echo "$CERT_OUTPUT" | grep -q "Developer ID Application"; then
    echo -e "${GREEN}✅ Certificate installed successfully!${NC}"
    echo ""
    echo "Available Developer ID certificates:"
    echo "$CERT_OUTPUT" | grep "Developer ID Application"
    echo ""
    
    # Extract the identity
    IDENTITY=$(echo "$CERT_OUTPUT" | grep "Developer ID Application" | head -1 | sed 's/.*"\(.*\)".*/\1/')
    
    if [ -n "$IDENTITY" ]; then
        echo -e "${YELLOW}Step 9: Setting CODESIGN_IDENTITY environment variable...${NC}"
        echo ""
        echo "Found certificate: $IDENTITY"
        echo ""
        
        # Add to .zshrc
        if ! grep -q "CODESIGN_IDENTITY" ~/.zshrc 2>/dev/null; then
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
        echo "CODESIGN_IDENTITY is now set to:"
        echo "  $IDENTITY"
        echo ""
        echo "To use in current terminal session, run:"
        echo "  source ~/.zshrc"
        echo ""
        echo "Or restart your terminal."
        echo ""
    fi
else
    echo -e "${RED}❌ Certificate not found after installation${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure you double-clicked the .cer file"
    echo "2. Check Keychain Access → My Certificates"
    echo "3. Try running: security find-identity -v -p codesigning"
    echo ""
    exit 1
fi

# Step 10: Test
echo -e "${YELLOW}Step 10: Testing setup...${NC}"
echo ""
./scripts/check_certificates.sh

echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}✅ Certificate setup complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Run: source ~/.zshrc (or restart terminal)"
echo "2. Test signing: ./scripts/sign_app.sh"
echo "3. Full release: ./scripts/full_release.sh 1.0.1"
echo ""
