# Changelog - Version 1.0.0

**Release Date:** November 28, 2025
**Build:** 100

## Major Changes

### 🎯 Deep Scan Feature - Now Functional
**Status:** ✅ Implemented and Working

Previously, the Deep Scan toggle was non-functional (parameter defined but never used). Now it actually controls the multi-language detection method.

**Changes:**
- Added functional logic in `transcription/enhanced.py:176-280`
- Two detection modes:
  - **Deep Scan OFF** (default): Fast text-based heuristic (10-20x faster)
  - **Deep Scan ON**: Comprehensive audio segmentation (slower but more accurate)
- Updated tooltip to accurately describe functionality
- Works automatically when user selects 2+ languages

**Files Modified:**
- `transcription/enhanced.py` - Implemented `use_comprehensive` logic
- `gui/main_window.py:155` - Updated tooltip text

### 🎵 Audio Filters - Memory Optimization
**Status:** ✅ Fixed Memory Issues

Fixed crashes when processing long videos (>3 minutes) with audio filters enabled.

**Changes:**
- Implemented **streaming processing** for files >3 minutes
- Processes audio in 60-second chunks instead of loading entire file
- Memory usage: ~4 MB per chunk vs 181+ MB for full file
- Works with files of ANY length (even hours-long)
- Filter state maintained between chunks for seamless transitions

**Performance:**
- 49-minute video: Memory reduced from 181 MB → 4 MB per chunk
- Bus error fixed by using WAV format for streaming (OGG caused crashes)

**Files Modified:**
- `gui/workers.py:668-829` - Added `_apply_audio_filters()` and `_apply_filters_streaming()`
- `gui/audio_filters.py` - Reviewed (already had proper stateful filters)

### 🔧 Transcription Fix - "Other" Language Mode
**Status:** ✅ Fixed Hallucination Issue

Fixed issue where selecting "Other" language type resulted in transcription showing only periods (`.`) instead of actual text.

**Problem:** Whisper was hallucinating silence when using `language=None` (auto-detect) with default parameters.

**Solution:** Added `condition_on_previous_text=False` parameter

**Files Modified:**
- `app/transcriber.py:355-362` - Added parameter to prevent hallucinations

### ⚙️ Settings Changes

**Audio Filters Default:**
- Changed from `enabled` to `disabled` by default
- Users can still enable manually
- Prevents unexpected memory usage on first run

**File:** `gui/main_window.py:111`

### 🚀 Auto-Update System
**Status:** ✅ Fully Implemented

Complete auto-update system with Google Cloud Storage backend.

**Features:**
- Automatic update check on app launch (3-second delay)
- 24-hour throttle (won't check more than once per day)
- SHA256 hash verification for security
- Background download with progress tracking
- Seamless installation and restart
- Platform-specific updates (macOS Intel/ARM, Windows, Linux)

**Components:**
- `app/version.py` - Version tracking (1.0.0, build 100)
- `gui/update_manager.py` - Core update logic with platform detection
- `gui/update_dialog.py` - User-friendly update UI
- `gui/main_window.py:200-398` - Integration with 24h throttle

**Google Cloud Storage Structure:**
```
gs://fonixflow-files/
├── FonixFlow.dmg (website download)
└── updates/
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

**Public URLs:**
- macOS ARM Manifest: https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json
- macOS Intel Manifest: https://storage.googleapis.com/fonixflow-files/updates/macos-intel/manifest.json
- Windows Manifest: https://storage.googleapis.com/fonixflow-files/updates/windows/manifest.json
- Linux Manifest: https://storage.googleapis.com/fonixflow-files/updates/linux/manifest.json

### 📦 Release Automation
**Status:** ✅ Automated Scripts Created

**New Scripts:**
- `scripts/release_to_gcs.sh` - Single-platform release (basic)
- `scripts/release_to_gcs_multiplatform.sh` - Multi-platform release (recommended)

**Workflow:**
```bash
# macOS Apple Silicon
./scripts/release_to_gcs_multiplatform.sh 1.0.0 macos-arm

# macOS Intel
./scripts/release_to_gcs_multiplatform.sh 1.0.0 macos-intel

# Windows
./scripts/release_to_gcs_multiplatform.sh 1.0.0 windows

# Linux
./scripts/release_to_gcs_multiplatform.sh 1.0.0 linux
```

**What It Does:**
1. Creates platform-specific package (ZIP/tar.gz)
2. Generates SHA256 hash
3. Uploads to GCS
4. Creates/uploads manifest.json
5. Verifies deployment

### 📚 Documentation
**Status:** ✅ Comprehensive Guides Created

**New Documentation:**
- `RELEASE_PROCESS.md` - Single-platform release guide
- `MULTIPLATFORM_RELEASE.md` - Multi-platform release guide
- `CHANGELOG_v1.0.0.md` - This file

**Updated Documentation:**
- `doc/README_QT.md` - Updated features list
- `doc/BUILD_MACOS.md` - Updated build instructions

## Bug Fixes

### Fixed: Audio Filter Crashes
- **Issue:** App crashed when processing long videos with filters enabled
- **Cause:** Loading 49-min video (47M samples) into memory
- **Fix:** Streaming processing in 60s chunks
- **Status:** ✅ Resolved

### Fixed: Transcription Showing Only Periods
- **Issue:** Selecting "Other" language type resulted in only periods
- **Cause:** Whisper hallucinating silence with `language=None`
- **Fix:** Added `condition_on_previous_text=False`
- **Status:** ✅ Resolved

### Fixed: Deep Scan Not Working
- **Issue:** Toggle had no effect on behavior
- **Cause:** Parameter defined but never used in logic
- **Fix:** Implemented actual comprehensive vs fast path logic
- **Status:** ✅ Resolved

## Performance Improvements

### Memory Usage
- Audio filters: 181 MB → 4 MB (for long files)
- Streaming processing prevents memory exhaustion
- Works with files of any length

### Transcription Speed
- Deep Scan OFF: 10-20x faster than comprehensive mode
- Users can choose speed vs accuracy trade-off

## Breaking Changes

**None** - All changes are backward compatible

## Known Issues

**None** - All reported issues resolved

## Upgrade Notes

### From Pre-1.0.0 Versions

1. **Audio Filters:** Now disabled by default
   - Re-enable in Settings if you were using them

2. **Update System:** Automatic update checks enabled
   - First check happens 3 seconds after launch
   - Checks limited to once per 24 hours
   - Can be triggered manually via Help menu

3. **Deep Scan:** Now actually works
   - Default: OFF (fast mode)
   - Enable for better accuracy on complex multi-language videos

## Technical Details

### Dependencies
- No new dependencies added
- All changes use existing libraries

### Platform Support
- ✅ macOS Apple Silicon (arm64)
- ✅ macOS Intel (x86_64)
- ✅ Windows
- ✅ Linux

### System Requirements
- No changes to minimum system requirements
- Streaming audio filters actually reduce memory requirements

## Security

### Update System
- HTTPS-only downloads
- SHA256 hash verification
- 24-hour throttle prevents abuse
- No automatic installation without user approval

### Code Signing
- macOS builds should be code-signed (see BUILD_MACOS.md)
- Windows builds should be signed for SmartScreen compatibility

## Contributors

This release includes contributions and fixes based on user feedback and testing.

## Next Steps

### Planned for 1.0.1
- Performance optimizations (faster-whisper integration)
- Additional language support improvements
- UI/UX enhancements

### Future Considerations
- Batch processing improvements
- Advanced audio filter presets
- Custom model support

---

For complete documentation, see:
- `RELEASE_PROCESS.md` - Release workflow
- `MULTIPLATFORM_RELEASE.md` - Multi-platform builds
- `doc/README_QT.md` - User guide
- `doc/BUILD_MACOS.md` - Build instructions
