# Multi-Platform Release Guide

> **📘 For complete release workflow including code signing, notarization, and DMG creation, see [doc/RELEASE_WORKFLOW.md](./doc/RELEASE_WORKFLOW.md)**

## Overview

FonixFlow supports 4 platforms with separate update channels:
- **macOS Intel** (x86_64)
- **macOS Apple Silicon** (arm64 / M1/M2/M3/M4)
- **Windows**
- **Linux**

Each platform has its own manifest and release packages.

## GCS Bucket Structure

```
gs://fonixflow-files/
├── releases/                          # First-time downloads (DMG files)
│   ├── FonixFlow_1.0.0_macos-arm.dmg
│   ├── FonixFlow_1.0.0_macos-intel.dmg
│   └── ...
└── updates/                           # Auto-updates (ZIP files)
    ├── macos-intel/
    │   ├── manifest.json
    │   └── FonixFlow_1.0.0_macos-intel.zip
    ├── macos-arm/
    │   ├── manifest.json
    │   └── FonixFlow_1.0.0_macos-arm.zip
    ├── windows/
    │   ├── manifest.json
    │   └── FonixFlow_1.0.0_windows.zip
    └── linux/
        ├── manifest.json
        └── FonixFlow_1.0.0_linux.tar.gz
```

**Distribution Strategy:**
- **DMG files** (`releases/`) → For first-time downloaders from website
- **ZIP files** (`updates/`) → For automatic updates within the app

## Public URLs

Each platform has its own manifest URL:

- **macOS Intel**: https://storage.googleapis.com/fonixflow-files/updates/macos-intel/manifest.json
- **macOS ARM**: https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json
- **Windows**: https://storage.googleapis.com/fonixflow-files/updates/windows/manifest.json
- **Linux**: https://storage.googleapis.com/fonixflow-files/updates/linux/manifest.json

## Platform Detection

The app automatically detects the platform at startup:

```python
# macOS Apple Silicon
System: Darwin, Machine: arm64 → macos-arm

# macOS Intel
System: Darwin, Machine: x86_64 → macos-intel

# Windows
System: Windows → windows

# Linux
System: Linux → linux
```

## Release Process

### 1. Build for Target Platform

#### macOS (Intel)
```bash
# On Intel Mac or use cross-compilation
pyinstaller fonixflow_qt.spec
# Produces: dist/FonixFlow.app
```

#### macOS (Apple Silicon)
```bash
# On Apple Silicon Mac
pyinstaller fonixflow_qt.spec
# Produces: dist/FonixFlow.app
```

#### Windows
```bash
# On Windows or use PyInstaller on Windows VM
pyinstaller fonixflow_qt.spec
# Produces: dist/FonixFlow.exe
```

#### Linux
```bash
# On Linux
pyinstaller fonixflow_qt.spec
# Produces: dist/FonixFlow (binary)
```

### 2. Release to GCS

```bash
# macOS Intel
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-intel

# macOS Apple Silicon
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-arm

# Windows
./scripts/release_to_gcs_multiplatform.sh 1.0.1 windows

# Linux
./scripts/release_to_gcs_multiplatform.sh 1.0.1 linux
```

### 3. What the Script Does

For each platform:
1. ✓ Creates platform-specific package:
   - macOS: ZIP with .app bundle
   - Windows: ZIP with .exe
   - Linux: tar.gz with binary
2. ✓ Generates SHA256 hash
3. ✓ Uploads to `gs://fonixflow-files/updates/{platform}/`
4. ✓ Creates platform-specific manifest.json
5. ✓ Uploads manifest
6. ✓ Verifies deployment

## Release All Platforms

To release all platforms at once:

```bash
#!/bin/bash
VERSION="1.0.1"

# Build and release each platform
for platform in macos-intel macos-arm windows linux; do
    echo "Releasing $platform..."

    # Build for platform (you'd need builds for each)
    # pyinstaller fonixflow_qt_${platform}.spec

    # Release
    ./scripts/release_to_gcs_multiplatform.sh $VERSION $platform

    echo "✓ $platform released"
    echo ""
done

echo "All platforms released!"
```

## Version Management

### Same Version Across Platforms

```bash
# Release v1.0.1 for all platforms
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-intel
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-arm
./scripts/release_to_gcs_multiplatform.sh 1.0.1 windows
./scripts/release_to_gcs_multiplatform.sh 1.0.1 linux
```

### Different Versions Per Platform

```bash
# Windows has a critical bug fix
./scripts/release_to_gcs_multiplatform.sh 1.0.2 windows

# Other platforms stay at 1.0.1
# (no action needed)
```

## Testing

### Test Platform Detection

```bash
python3 -c "
from gui.update_manager import UpdateManager
mgr = UpdateManager('1.0.0')
print(f'Platform: {mgr.platform}')
print(f'Manifest URL: {mgr.manifest_url}')
"
```

### Test Update Check

```bash
# macOS ARM example
curl https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json
```

### Test in App

1. Launch app on each platform
2. Wait 3 seconds for automatic check
3. Update dialog should show platform-specific update

## Manifest Format

Each platform's `manifest.json`:

```json
{
  "latest_version": "1.0.1",
  "platform": "macos-arm",
  "platform_name": "macOS (Apple Silicon)",
  "download_url": "https://storage.googleapis.com/fonixflow-files/updates/macos-arm/FonixFlow_1.0.1_macos-arm.zip",
  "release_notes": "## FonixFlow 1.0.1 (macOS Apple Silicon)\n\n- Bug fixes\n- Platform optimizations",
  "force_update": false,
  "file_hash": "abc123...",
  "minimum_version": "1.0.0",
  "release_date": "2025-11-28",
  "file_size_mb": 450
}
```

## Build Considerations

### Cross-Platform Builds

**macOS Intel on Apple Silicon:**
```bash
# Use Universal Binary or cross-compile
arch -x86_64 pyinstaller fonixflow_qt.spec
```

**Windows on macOS/Linux:**
- Use Windows VM or CI/CD (GitHub Actions)
- Use Wine + PyInstaller (not recommended for production)

**Linux on macOS:**
- Use Docker: `docker run --rm -v $(pwd):/app python:3.11 ...`
- Use Linux VM

### Recommended Approach: CI/CD

Use GitHub Actions to build all platforms:

```yaml
# .github/workflows/release.yml
name: Multi-Platform Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos-intel:
    runs-on: macos-13  # Intel runner
    # ... build and upload

  build-macos-arm:
    runs-on: macos-14  # Apple Silicon runner
    # ... build and upload

  build-windows:
    runs-on: windows-latest
    # ... build and upload

  build-linux:
    runs-on: ubuntu-latest
    # ... build and upload
```

## Troubleshooting

**"Wrong manifest URL"**
- Check logs: `logger.info(f"Update manager initialized for platform: {self.platform}")`
- Verify platform detection

**"Update not showing on specific platform"**
- Check manifest exists: `curl https://storage.googleapis.com/fonixflow-files/updates/{platform}/manifest.json`
- Verify version is higher: `"latest_version": "1.0.1"` > current app version

**"Download fails"**
- Check file exists: `gsutil ls gs://fonixflow-files/updates/{platform}/`
- Verify SHA256 hash matches

## Migration from Single Platform

If you have existing `updates/manifest.json`:

```bash
# Move old manifest to macos-arm (or your primary platform)
gsutil cp gs://fonixflow-files/updates/manifest.json \
          gs://fonixflow-files/updates/macos-arm/manifest.json

# Create other platform manifests
./scripts/release_to_gcs_multiplatform.sh 1.0.0 macos-intel
./scripts/release_to_gcs_multiplatform.sh 1.0.0 windows
./scripts/release_to_gcs_multiplatform.sh 1.0.0 linux
```

## Security

- All platforms use SHA256 hash verification
- HTTPS-only downloads
- 24-hour update check throttle per platform
- Separate manifests prevent platform mix-ups
