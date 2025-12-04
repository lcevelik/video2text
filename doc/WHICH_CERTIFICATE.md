# Which Certificate Do I Need?

## For FonixFlow: **Developer ID Application** ✅

You need **"Developer ID Application"** certificate.

## Certificate Types Explained

### ✅ Developer ID Application (What You Need)

**Used for:**
- Code signing `.app` bundles
- Code signing executables
- Distribution outside Mac App Store
- DMG files (optional, but recommended)

**This is what FonixFlow uses!**

### ❌ Developer ID Installer (Not Needed)

**Used for:**
- Signing `.pkg` installer packages only
- Not for `.app` bundles
- Only if you distribute as `.pkg` instead of `.app`

**FonixFlow distributes as `.app` bundle, so you don't need this.**

### ❌ Apple Development (Not for Distribution)

**Used for:**
- Development and testing only
- Cannot be used for distribution
- Only works on your Mac

**You already have this, but it won't work for releases.**

## Quick Answer

**Create: "Developer ID Application"** ✅

This is the only certificate you need for FonixFlow releases.

## How to Create It

1. Go to: https://developer.apple.com/account/resources/certificates/add
2. Under **"Software"** section
3. Select **"Developer ID Application"** ← This one!
4. Follow the wizard
5. Create CSR on THIS Mac (so private key stays here)
6. Download and install

## Verification

After installing, verify:
```bash
./scripts/check_certificates.sh
```

You should see:
```
✅ Developer ID Application certificate found!
```

## Summary

| Certificate Type | Use For | FonixFlow? |
|-----------------|---------|------------|
| **Developer ID Application** | `.app` bundles | ✅ **YES - Use This!** |
| Developer ID Installer | `.pkg` packages | ❌ No |
| Apple Development | Development only | ❌ No |
