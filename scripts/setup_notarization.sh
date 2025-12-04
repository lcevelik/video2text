#!/bin/bash

# Setup script for notarization credentials
# This helps you configure APP_PASSWORD for Apple notarization

set -e

echo "==========================================="
echo "FonixFlow Notarization Setup"
echo "==========================================="
echo ""

# Check current status
echo "Current status:"
if [ -z "$APP_PASSWORD" ]; then
    echo "  ❌ APP_PASSWORD: Not set"
else
    echo "  ✅ APP_PASSWORD: Set (hidden for security)"
fi

if [ -z "$APPLE_ID" ]; then
    echo "  ⚠️  APPLE_ID: Not set (will use default: libor.cevelik@me.com)"
else
    echo "  ✅ APPLE_ID: $APPLE_ID"
fi

if [ -z "$TEAM_ID" ]; then
    echo "  ⚠️  TEAM_ID: Not set (will use default: 8BLXD56D6K)"
else
    echo "  ✅ TEAM_ID: $TEAM_ID"
fi

echo ""
echo "==========================================="
echo ""

# Check if APP_PASSWORD is already set
if [ -n "$APP_PASSWORD" ]; then
    echo "✅ APP_PASSWORD is already set!"
    echo ""
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing APP_PASSWORD."
        exit 0
    fi
fi

echo "To set up notarization, you need an App-Specific Password from Apple."
echo ""
echo "Steps:"
echo "1. Go to: https://appleid.apple.com"
echo "2. Sign in with your Apple ID"
echo "3. Navigate to: Sign-In and Security → App-Specific Passwords"
echo "4. Click: 'Generate an app-specific password...'"
echo "5. Label it: 'FonixFlow Notarization'"
echo "6. Copy the password (format: xxxx-xxxx-xxxx-xxxx)"
echo ""
read -p "Press Enter when you have the password ready..."
echo ""

# Get the password
read -sp "Enter your App-Specific Password: " PASSWORD
echo ""

if [ -z "$PASSWORD" ]; then
    echo "❌ Error: Password cannot be empty!"
    exit 1
fi

# Validate format (should be xxxx-xxxx-xxxx-xxxx)
if [[ ! "$PASSWORD" =~ ^[a-z]{4}-[a-z]{4}-[a-z]{4}-[a-z]{4}$ ]]; then
    echo "⚠️  Warning: Password format doesn't match expected pattern (xxxx-xxxx-xxxx-xxxx)"
    echo "   Continuing anyway..."
fi

echo ""
echo "How do you want to save this password?"
echo "1) Temporary (current session only)"
echo "2) Permanent (add to ~/.zshrc)"
read -p "Choose option (1 or 2): " -n 1 -r
echo ""

case $REPLY in
    1)
        export APP_PASSWORD="$PASSWORD"
        echo "✅ APP_PASSWORD set for current session"
        echo ""
        echo "To use it now, run:"
        echo "  export APP_PASSWORD='$PASSWORD'"
        echo ""
        echo "⚠️  Note: This will be lost when you close the terminal."
        ;;
    2)
        # Check if already in .zshrc
        if grep -q "APP_PASSWORD" ~/.zshrc 2>/dev/null; then
            echo "⚠️  APP_PASSWORD already exists in ~/.zshrc"
            read -p "Do you want to replace it? (y/N): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                # Remove old line
                sed -i.bak '/^export APP_PASSWORD=/d' ~/.zshrc
                # Add new line
                echo "export APP_PASSWORD=\"$PASSWORD\"" >> ~/.zshrc
                echo "✅ Updated APP_PASSWORD in ~/.zshrc"
            else
                echo "Keeping existing entry."
                exit 0
            fi
        else
            # Add to .zshrc
            echo "" >> ~/.zshrc
            echo "# FonixFlow Notarization" >> ~/.zshrc
            echo "export APP_PASSWORD=\"$PASSWORD\"" >> ~/.zshrc
            echo "✅ Added APP_PASSWORD to ~/.zshrc"
        fi
        
        echo ""
        echo "To activate it, run:"
        echo "  source ~/.zshrc"
        echo ""
        echo "Or restart your terminal."
        ;;
    *)
        echo "❌ Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "==========================================="
echo "Setup Complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Test notarization:"
echo "   ./scripts/notarize_app.sh"
echo ""
echo "2. Or run full release with notarization:"
echo "   ./scripts/full_release.sh 1.0.1"
echo ""
echo "For more details, see: doc/NOTARIZATION_SETUP.md"
echo ""
