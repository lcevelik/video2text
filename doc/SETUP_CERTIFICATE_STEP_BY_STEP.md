# Step-by-Step: Setting Up Code Signing Certificate

This guide will walk you through getting a "Developer ID Application" certificate on your Mac.

## Prerequisites

- ✅ Apple Developer Program membership ($99/year)
- ✅ Apple ID with active Developer account
- ✅ This Mac (where you want to sign)

## Step 1: Check Your Current Certificates

First, let's see what you have:

```bash
cd /Users/liborcevelik/Desktop/Codeabse/video2text
./scripts/check_certificates.sh
```

**Expected output:** You'll see "Apple Development" certificates but no "Developer ID Application" certificate.

---

## Step 2: Open Apple Developer Portal

1. **Open your browser** and go to:
   ```
   https://developer.apple.com/account/resources/certificates/list
   ```

2. **Sign in** with your Apple ID (the one associated with your Developer account)

3. **You should see** a list of certificates (if any exist)

---

## Step 3: Check if Developer ID Certificate Already Exists

**Look for:**
- ✅ "Developer ID Application" - **This is what you need!**
- ❌ "Apple Development" - Not for distribution
- ❌ "Mac App Distribution" - For App Store only

**If you see "Developer ID Application":**
- ✅ **Great!** Skip to Step 5 (Download and Install)

**If you DON'T see it:**
- Continue to Step 4 (Create New Certificate)

---

## Step 4: Create Developer ID Application Certificate

### 4a. Go to Create Certificate Page

1. Click the **"+" button** (top right) or go directly to:
   ```
   https://developer.apple.com/account/resources/certificates/add
   ```

### 4b. Select Certificate Type

1. Under **"Software"** section, find:
   - **"Developer ID Application"** ← **Select this one!**

2. **DO NOT select:**
   - ❌ "Apple Development" (development only)
   - ❌ "Mac App Distribution" (App Store only)

3. Click **"Continue"**

### 4c. Follow the Wizard

1. **Read the information** about Developer ID certificates
2. Click **"Continue"**

### 4d. Upload CSR (Certificate Signing Request)

**Option A: Create CSR on This Mac (Recommended)**

1. **Open Keychain Access:**
   - Press `Cmd + Space`
   - Type "Keychain Access"
   - Press Enter

2. **Create Certificate Request:**
   - Menu: **Keychain Access** → **Certificate Assistant** → **Request a Certificate From a Certificate Authority...**

3. **Fill in the form:**
   - **User Email Address:** Your email (libor.cevelik@me.com)
   - **Common Name:** Your name (Libor Cevelik)
   - **CA Email Address:** Leave empty
   - **Request is:** Select **"Saved to disk"**
   - Click **"Continue"**

4. **Save the file:**
   - Save as: `CertificateSigningRequest.certSigningRequest`
   - Save to: `~/Desktop` (or anywhere easy to find)

5. **Back in browser:**
   - Click **"Choose File"**
   - Select the `CertificateSigningRequest.certSigningRequest` file you just created
   - Click **"Continue"**

**Option B: Use Existing CSR (If You Have One)**

- If you already have a CSR file from another Mac, upload that instead

### 4e. Download Certificate

1. After uploading CSR, Apple will generate the certificate
2. Click **"Download"** button
3. The file will download as: `developerID_application.cer`

---

## Step 5: Install Certificate on This Mac

### 5a. Install the Certificate

1. **Find the downloaded file:**
   - Usually in `~/Downloads/`
   - File name: `developerID_application.cer`

2. **Double-click the file**
   - macOS will automatically open Keychain Access
   - Certificate will be added to your **"login"** keychain

3. **Verify installation:**
   ```bash
   security find-identity -v -p codesigning
   ```

4. **You should now see:**
   ```
   1) ABC123... "Developer ID Application: Libor Cevelik (TEAMID)"
   ```

### 5b. Verify Certificate Details

1. **Open Keychain Access** (if not already open)
2. **Select "login" keychain** (left sidebar)
3. **Click "My Certificates"** (bottom of left sidebar)
4. **Find:** "Developer ID Application: Libor Cevelik (...)"
5. **Double-click** to view details
6. **Verify:**
   - ✅ Type: Developer ID Application
   - ✅ Valid: Shows expiration date
   - ✅ Private key: Should be present

---

## Step 6: Set Environment Variable

Now tell the scripts which certificate to use:

### 6a. Find Your Certificate Identity

Run this command:
```bash
security find-identity -v -p codesigning | grep "Developer ID Application"
```

**Copy the full identity string**, for example:
```
"Developer ID Application: Libor Cevelik (8BLXD56D6K)"
```

### 6b. Set Environment Variable (Temporary - Current Session)

```bash
export CODESIGN_IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"
```

**Replace with your actual identity from Step 6a!**

### 6c. Set Environment Variable (Permanent - All Sessions)

Add to your shell profile so it's always available:

**For zsh (default on macOS):**
```bash
echo 'export CODESIGN_IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"' >> ~/.zshrc
source ~/.zshrc
```

**For bash:**
```bash
echo 'export CODESIGN_IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"' >> ~/.bash_profile
source ~/.bash_profile
```

**Replace with your actual identity from Step 6a!**

---

## Step 7: Verify Setup

### 7a. Check Certificate Script

```bash
cd /Users/liborcevelik/Desktop/Codeabse/video2text
./scripts/check_certificates.sh
```

**You should see:**
- ✅ Developer ID Application certificate found
- ✅ CODESIGN_IDENTITY is set

### 7b. Test Code Signing

```bash
# First, build the app
./build_macos.sh

# Then test signing
./scripts/sign_app.sh
```

**If successful, you'll see:**
- ✅ App bundle signed
- ✅ Signature verification successful

---

## Step 8: Set Up Notarization (Optional but Recommended)

For notarization, you also need an **App-Specific Password**:

### 8a. Create App-Specific Password

1. Go to: https://appleid.apple.com
2. Sign in with your Apple ID
3. Go to **"Sign-In and Security"** → **"App-Specific Passwords"**
4. Click **"Generate an app-specific password"**
5. **Label it:** "FonixFlow Notarization" (or any name)
6. **Copy the password** (you'll only see it once!)
   - Format: `xxxx-xxxx-xxxx-xxxx`

### 8b. Set Environment Variables

```bash
export APPLE_ID="libor.cevelik@me.com"
export TEAM_ID="8BLXD56D6K"  # Your Team ID from Apple Developer
export APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # The app-specific password you just created
```

**Make permanent:**
```bash
# Add to ~/.zshrc
cat >> ~/.zshrc << 'EOF'
export APPLE_ID="libor.cevelik@me.com"
export TEAM_ID="8BLXD56D6K"
export APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
EOF

source ~/.zshrc
```

**⚠️ Security Note:** App-specific passwords are sensitive. Consider using a password manager.

---

## Step 9: Test Full Release

Now test the complete workflow:

```bash
cd /Users/liborcevelik/Desktop/Codeabse/video2text
./scripts/full_release.sh 1.0.1 --skip-notarize  # Test without notarization first
```

**If successful, you'll see:**
- ✅ App signed
- ✅ DMG created
- ✅ Files uploaded to GCS

---

## Troubleshooting

### "No identity found" when signing

**Check:**
1. Certificate is installed: `security find-identity -v -p codesigning`
2. `CODESIGN_IDENTITY` is set correctly: `echo $CODESIGN_IDENTITY`
3. Identity matches exactly (including Team ID)

**Fix:**
```bash
# Re-export the identity
export CODESIGN_IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"
```

### "Permission denied" when signing

**Fix:**
```bash
# Unlock keychain
security unlock-keychain ~/Library/Keychains/login.keychain-db

# Or set keychain to not require password
security set-keychain-settings -t 3600 ~/Library/Keychains/login.keychain-db
```

### Certificate not showing in Keychain

**Fix:**
1. Double-click the `.cer` file again
2. Or manually import:
   ```bash
   security import ~/Downloads/developerID_application.cer \
       -k ~/Library/Keychains/login.keychain-db
   ```

### "Certificate expired"

**Solution:**
1. Go back to Apple Developer portal
2. Create new certificate
3. Download and install
4. Update `CODESIGN_IDENTITY` if name changed

---

## Quick Reference Commands

```bash
# Check certificates
./scripts/check_certificates.sh

# View all certificates
security find-identity -v -p codesigning

# Set identity (temporary)
export CODESIGN_IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"

# Test signing
./scripts/sign_app.sh

# Full release (with signing)
./scripts/full_release.sh 1.0.1
```

---

## Summary Checklist

- [ ] Step 1: Checked current certificates
- [ ] Step 2: Opened Apple Developer portal
- [ ] Step 3: Checked for existing Developer ID certificate
- [ ] Step 4: Created Developer ID Application certificate (if needed)
- [ ] Step 5: Downloaded and installed certificate
- [ ] Step 6: Set CODESIGN_IDENTITY environment variable
- [ ] Step 7: Verified setup with check script
- [ ] Step 8: Set up App-Specific Password (for notarization)
- [ ] Step 9: Tested full release workflow

---

## Next Steps

Once certificates are set up:

1. **Test signing:**
   ```bash
   ./build_macos.sh
   ./scripts/sign_app.sh
   ```

2. **Test full release:**
   ```bash
   ./scripts/full_release.sh 1.0.1
   ```

3. **Verify signed app:**
   ```bash
   codesign --verify --deep --strict --verbose=2 dist/FonixFlow.app
   ```

---

## Using on Multiple Macs

**The same certificate works on all your Macs!**

1. **On this Mac:** Follow steps above
2. **On another Mac:**
   - Download the same certificate from Apple Developer portal
   - Or export/import from this Mac (see CODE_SIGNING_SETUP.md)
   - Set `CODESIGN_IDENTITY` environment variable
   - Done!

**No need to create separate certificates for each Mac.**

---

## Need Help?

- Check `doc/CODE_SIGNING_SETUP.md` for detailed information
- Run `./scripts/check_certificates.sh` to diagnose issues
- Apple Developer Support: https://developer.apple.com/support/
