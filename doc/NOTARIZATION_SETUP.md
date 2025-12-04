# Setting Up Notarization

Notarization is Apple's security process that verifies your app is safe to run. It's required for distribution outside the Mac App Store.

## Prerequisites

- ✅ **Code signing certificate** (Developer ID Application) - already set up
- ✅ **Apple Developer Program membership** ($99/year)
- ✅ **App-Specific Password** (this guide)

## What is an App-Specific Password?

An App-Specific Password is a special password that allows automated tools (like `notarytool`) to authenticate with Apple's notarization service without using your main Apple ID password.

## Step 1: Create App-Specific Password

1. **Go to Apple ID website:**
   ```
   https://appleid.apple.com
   ```

2. **Sign in** with your Apple ID:
   - Email: `libor.cevelik@me.com`
   - Use your regular Apple ID password

3. **Navigate to App-Specific Passwords:**
   - Click on **"Sign-In and Security"** (or "Security" in older interface)
   - Scroll down to **"App-Specific Passwords"**
   - Click **"Generate an app-specific password..."**

4. **Create the password:**
   - **Label:** `FonixFlow Notarization` (or any descriptive name)
   - Click **"Create"**
   - **Copy the password immediately!** It will look like: `xxxx-xxxx-xxxx-xxxx`
   - ⚠️ **You can only see it once!** If you lose it, you'll need to create a new one.

## Step 2: Set Environment Variable

### Option A: Temporary (Current Session Only)

```bash
export APP_PASSWORD="your-app-specific-password-here"
```

**Note:** This only works for the current terminal session. Close the terminal and you'll need to set it again.

### Option B: Permanent (Recommended)

Add it to your shell configuration file:

```bash
# For zsh (default on macOS)
echo 'export APP_PASSWORD="your-app-specific-password-here"' >> ~/.zshrc
source ~/.zshrc

# For bash
echo 'export APP_PASSWORD="your-app-specific-password-here"' >> ~/.bash_profile
source ~/.bash_profile
```

**Replace `your-app-specific-password-here`** with the actual password you copied from Apple.

## Step 3: Verify Setup

Check that the environment variable is set:

```bash
echo $APP_PASSWORD
```

You should see your password (or it will be blank if not set).

## Step 4: Test Notarization

Once set up, you can test notarization:

```bash
cd /Users/liborcevelik/Desktop/Codeabse/video2text

# Make sure app is built and signed first
./scripts/sign_app.sh

# Test notarization
./scripts/notarize_app.sh
```

Or run the full release with notarization:

```bash
./scripts/full_release.sh 1.0.1
```

## Environment Variables Summary

For notarization, you need these environment variables:

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `APP_PASSWORD` | (none) | ✅ **Yes** | App-Specific Password from Apple |
| `APPLE_ID` | `libor.cevelik@me.com` | No | Your Apple ID email |
| `TEAM_ID` | `8BLXD56D6K` | No | Your Apple Developer Team ID |

**Only `APP_PASSWORD` is required** - the others have defaults in the scripts.

## Troubleshooting

### "APP_PASSWORD environment variable is not set!"

**Solution:**
1. Make sure you've created an App-Specific Password (Step 1)
2. Set the environment variable (Step 2)
3. Verify it's set: `echo $APP_PASSWORD`

### "Invalid credentials" or "Authentication failed"

**Possible causes:**
- App-Specific Password is incorrect
- Password was revoked or expired
- Two-factor authentication is not enabled on your Apple ID

**Solution:**
1. Go back to https://appleid.apple.com
2. Check your App-Specific Passwords list
3. Revoke the old one and create a new one
4. Update the `APP_PASSWORD` environment variable

### "Notarization failed" or "Invalid signature"

**Solution:**
1. Make sure the app is properly code-signed first:
   ```bash
   ./scripts/sign_app.sh
   ```
2. Check the signature:
   ```bash
   codesign --verify --verbose dist/FonixFlow.app
   ```

### Notarization Takes Too Long

**Normal behavior:**
- Notarization typically takes **5-15 minutes**
- Apple processes submissions in a queue
- You'll see progress updates during the wait

**If it's stuck:**
- Check your internet connection
- Verify `APP_PASSWORD` is correct
- Check Apple's system status: https://developer.apple.com/system-status/

## Security Best Practices

1. **Never commit App-Specific Passwords to git**
   - They're in `.gitignore` by default
   - Use environment variables, not hardcoded values

2. **Use different passwords for different purposes**
   - One for notarization
   - One for other Apple services (if needed)

3. **Revoke old passwords**
   - If you suspect a password is compromised
   - If you're rotating credentials

4. **Keep passwords secure**
   - Don't share them
   - Don't put them in scripts or documentation

## Quick Reference

### Check if APP_PASSWORD is set:
```bash
if [ -z "$APP_PASSWORD" ]; then
    echo "❌ Not set"
else
    echo "✅ Set (hidden for security)"
fi
```

### Set temporarily:
```bash
export APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
```

### Set permanently:
```bash
echo 'export APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"' >> ~/.zshrc
source ~/.zshrc
```

### Run full release with notarization:
```bash
./scripts/full_release.sh 1.0.1
```

## Next Steps

Once notarization is set up:
- ✅ Your releases will be automatically notarized
- ✅ Users won't see "unidentified developer" warnings
- ✅ Apps will pass Gatekeeper checks
- ✅ Distribution is smoother and more professional

---

**Need help?** Check the main [CODE_SIGNING_SETUP.md](./CODE_SIGNING_SETUP.md) guide.
