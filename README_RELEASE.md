# FonixFlow Release Documentation

This directory contains all documentation and scripts for building and releasing FonixFlow.

## Quick Links

- **[QUICK_START_RELEASE.md](./QUICK_START_RELEASE.md)** ⚡ - Fastest way to create a release
- **[doc/RELEASE_WORKFLOW.md](./doc/RELEASE_WORKFLOW.md)** 📘 - Complete release workflow guide
- **[doc/BUILD_MACOS.md](./doc/BUILD_MACOS.md)** 🔨 - Build instructions
- **[DMG_CREATION_GUIDE.md](./DMG_CREATION_GUIDE.md)** 💿 - DMG creation guide
- **[doc/DMG_SCRIPTS_GUIDE.md](./doc/DMG_SCRIPTS_GUIDE.md)** 📋 - Comparison of all DMG scripts
- **[MULTIPLATFORM_RELEASE.md](./MULTIPLATFORM_RELEASE.md)** 🌍 - Multi-platform release

## Release Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/full_release.sh` | **Complete automated release** (recommended) |
| `./build_macos.sh` | Build app only |
| `./scripts/sign_app.sh` | Code sign app |
| `./scripts/notarize_app.sh` | Notarize app |
| `./scripts/create_custom_dmg.sh` | Create DMG (with background) |
| `./create_clean_dmg.sh` | Create DMG (quick, no background) |
| `./create_dmg_working.sh` | Create DMG (custom layout) |
| `./create_icns.sh` | Create .icns icon file |
| `./scripts/release_to_gcs_multiplatform.sh` | Upload to GCS |

## Typical Workflow

### Option 1: Automated (Recommended)

```bash
# One command does everything
./scripts/full_release.sh 1.0.1
```

### Option 2: Step-by-Step

```bash
# 1. Build
./build_macos.sh

# 2. Sign
./scripts/sign_app.sh

# 3. Notarize
./scripts/notarize_app.sh

# 4. Create DMG
./scripts/create_custom_dmg.sh "FonixFlow" "dist/FonixFlow.app" "dist/FonixFlow.dmg"

# 5. Release to GCS
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-arm
```

## Environment Variables

Set these for automated scripts:

```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
export APPLE_ID="your@email.com"
export TEAM_ID="TEAMID"
export APP_PASSWORD="app-specific-password"
```

## Platform Support

- **macOS Apple Silicon** (arm64 / M1/M2/M3/M4)
- **macOS Intel** (x86_64)
- **Windows** (coming soon)
- **Linux** (coming soon)

## Need Help?

1. Check [QUICK_START_RELEASE.md](./QUICK_START_RELEASE.md) for common issues
2. See [doc/RELEASE_WORKFLOW.md](./doc/RELEASE_WORKFLOW.md) for detailed troubleshooting
3. Review script comments for specific error messages
