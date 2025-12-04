# Code Signing Certificate Setup Guide

## Overview

Code signing certificates are **tied to your Apple Developer account**, not to a specific Mac. You can install the same certificate on multiple Macs.

## Quick Check: Do You Have Certificates?

Run this command to see what certificates are installed:

```bash
security find-identity -v -p codesigning
```

### Certificate Types

**For Distribution (What You Need):**
```
"Developer ID Application: Your Name (TEAMID)"
```
✅ **This is what you need for distributing outside App Store**

**For Development Only:**
```
"Apple Development: Your Name (TEAMID)"
```
⚠️ **This is for development/testing only, cannot be used for distribution**

**If you see:**
```
Valid identities found
     0 valid identities found
```
❌ **No certificates found.** You need to install them.

## Installing Certificates

### Option 1: Download from Apple Developer Portal (Recommended)

1. **Go to Apple Developer Portal:**
   - https://developer.apple.com/account/resources/certificates/list
   - Sign in with your Apple ID

2. **Download Developer ID Certificate:**
   - Look for "Developer ID Application" certificate
   - Click "Download"
   - Double-click the `.cer` file to install in Keychain

3. **Verify Installation:**
   ```bash
   security find-identity -v -p codesigning
   ```

### Option 2: Create New Certificate (If You Don't Have One)

**Important:** You need a **"Developer ID Application"** certificate for distribution, NOT "Apple Development".

1. **Go to Apple Developer Portal:**
   - https://developer.apple.com/account/resources/certificates/add
   - Select **"Developer ID Application"** (NOT "Apple Development")
   - Follow the wizard to create certificate
   - Download and install

**Note:** "Apple Development" certificates won't work for distribution. You specifically need "Developer ID Application".

### Option 3: Export/Import from Another Mac

If you have certificates on another Mac:

**On the Mac with certificates:**
```bash
# Export certificate and private key
security find-identity -v -p codesigning
# Note the identity hash (e.g., ABC123DEF456)

# Export certificate
security export -k ~/Library/Keychains/login.keychain-db \
    -t identities -f pkcs12 -P "password" \
    -o ~/Desktop/certificate.p12
```

**On this Mac:**
```bash
# Import certificate
security import ~/Desktop/certificate.p12 \
    -k ~/Library/Keychains/login.keychain-db \
    -P "password" \
    -T /usr/bin/codesign
```

## Setting Up for FonixFlow

### 1. Find Your Certificate Identity

```bash
security find-identity -v -p codesigning
```

Look for a line like:
```
1) ABC123DEF456 "Developer ID Application: Libor Cevelik (8BLXD56D6K)"
```

### 2. Set Environment Variable

**Temporary (for current session):**
```bash
export CODESIGN_IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"
```

**Permanent (add to `~/.zshrc` or `~/.bash_profile`):**
```bash
# Add this line
export CODESIGN_IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

### 3. Test Signing

```bash
# Build app first
./build_macos.sh

# Try signing
./scripts/sign_app.sh
```

## Working Without Certificates

**You can still build and release without code signing!**

### Skip Code Signing

The `full_release.sh` script will automatically skip signing if:
- `CODESIGN_IDENTITY` is not set
- Certificate is not found

**Just run:**
```bash
./scripts/full_release.sh 1.0.1 --skip-notarize
```

This will:
- ✓ Build the app
- ✗ Skip code signing (no certificate)
- ✗ Skip notarization (requires signing)
- ✓ Create DMG
- ✓ Upload to GCS

### Limitations Without Signing

- ⚠️ Users will see "unidentified developer" warning
- ⚠️ App won't pass Gatekeeper on first launch
- ⚠️ Cannot notarize (notarization requires signing)
- ✓ App will still work (users can bypass warning)
- ✓ Auto-updates will still work

## Multiple Macs Setup

### Same Certificate on Multiple Macs

**Yes, you can use the same certificate on multiple Macs!**

1. **Install certificate on each Mac:**
   - Download from Apple Developer portal
   - Or export/import from another Mac (see Option 3 above)

2. **Set environment variable on each Mac:**
   ```bash
   export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
   ```

3. **That's it!** Same certificate works on all Macs.

### Team Certificates

If you're part of a team:
- Team Admin creates the certificate
- Team members can download and use it
- All team members sign with the same certificate

## Troubleshooting

### "No identity found"

**Solution:**
1. Check if certificate exists: `security find-identity -v -p codesigning`
2. If not found, download from Apple Developer portal
3. If found but script can't use it, check Keychain access:
   ```bash
   # Allow codesign to access certificate
   security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "your-keychain-password" ~/Library/Keychains/login.keychain-db
   ```

### "Certificate expired"

**Solution:**
1. Go to Apple Developer portal
2. Create new certificate
3. Download and install
4. Update `CODESIGN_IDENTITY` if name changed

### "Permission denied" when signing

**Solution:**
```bash
# Unlock keychain (if locked)
security unlock-keychain ~/Library/Keychains/login.keychain-db

# Or set keychain to not lock
security set-keychain-settings -t 3600 ~/Library/Keychains/login.keychain-db
```

## Quick Reference

### Check Certificates
```bash
security find-identity -v -p codesigning
```

### Set Identity (Temporary)
```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
```

### Set Identity (Permanent)
```bash
echo 'export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"' >> ~/.zshrc
source ~/.zshrc
```

### Test Signing
```bash
./scripts/sign_app.sh
```

### Release Without Signing
```bash
./scripts/full_release.sh 1.0.1 --skip-notarize
```

### Set Up Notarization
For complete setup including App-Specific Password, see:
- **[NOTARIZATION_SETUP.md](./NOTARIZATION_SETUP.md)** - Complete guide for notarization setup

## Apple Developer Account Requirements

To get certificates, you need:
- **Apple Developer Program membership** ($99/year)
- **Team ID** (found in Apple Developer portal)
- **Developer ID Application certificate** (for distribution outside App Store)

**Free Apple ID won't work** - you need a paid Developer account.

## Summary

- ✅ **Certificates are account-based**, not Mac-specific
- ✅ **Same certificate works on multiple Macs**
- ✅ **Install once, use everywhere**
- ✅ **Can work without certificates** (with limitations)
- ✅ **Scripts handle missing certificates gracefully**
