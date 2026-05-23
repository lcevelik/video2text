# Changelog - Version 1.0.3

**Release Date:** 2026-05-22
**Build:** 103

## Changes

### Windows Build — No Console Windows
All subprocess calls now suppress console windows on Windows via `CREATE_NO_WINDOW`:
- `app/audio_extractor.py` — ffmpeg/ffprobe calls
- `transcription/audio_processing.py` — ffmpeg sampling and chunk extraction
- `app/transcriber.py` — Whisper's internal ffmpeg calls (global monkey-patch of `subprocess.Popen`)

Uses a `_NO_WIN` dict (`{'creationflags': CREATE_NO_WINDOW} if sys.platform == 'win32' else {}`) so the same code works on macOS without changes.

### License Validation — User Data Directory
License files are now read exclusively from `~/.fonixflow/`:
- `~/.fonixflow/licenses.dat` (XOR+base64 encoded, checked first)
- `~/.fonixflow/licenses.txt` (plaintext fallback)

Previously both `gui/dialogs.py` and `gui/main_window.py` looked in the app bundle directory. This fixes license validation for distributed macOS builds where the bundle is read-only.

### Update Dialog — Theme Support
`gui/update_dialog.py` refactored:
- Picks up dark/light mode from the parent window's `theme_manager`
- All colours now use `Theme.get()` tokens instead of hardcoded hex values
- Progress bar styled consistently with the rest of the app
- On successful install, shows the message returned by `install_update` and enables a "Close" button (instead of auto-restarting)

### Update Manager — Platform-Specific Install
`gui/update_manager.py` `install_update()` now handles two platforms:
- **Windows:** extracts the `.exe` to `~/.fonixflow/updates/`, opens Explorer to that folder, and returns an instruction message
- **macOS:** replaces `/Applications/FonixFlow.app` in-place, returns a "please restart" message

Returns a descriptive string on success (used by the dialog) or `False` on failure.

### Mac Build — Dynamic Version in Spec
`fonixflow_qt.spec` now reads `__version__` from `app/version.py` at build time (same pattern as the Windows spec). Version 1.0.3 flows automatically into `CFBundleVersion`, `CFBundleShortVersionString`, and the BUNDLE `version` field.

The `licenses.txt` binary entry was removed from the spec — it is no longer bundled since validation reads from `~/.fonixflow/` instead.

`build_macos.sh` DMG filename now includes the version (`FonixFlow_1.0.3_macOS.dmg`).

### macOS Release — 1.0.3 Deployed
- App signed: Developer ID Application: Libor Cevelik (8BLXD56D6K)
- App notarized: Notarized Developer ID (Apple)
- DMG notarized and stapled
- First-time download: `https://storage.googleapis.com/fonixflow-files/releases/FonixFlow_1.0.3_macos-arm.dmg`
- Auto-update manifest: `https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json`

## Bug Fixes

- Fixed: WASAPI loopback silent-packet crash (`AUDCLNT_BUFFERFLAGS_SILENT` check)
- Fixed: Update dialog success path showed stale "will restart now" message when auto-restart was removed

## Platform Support

| Platform | Status |
|---|---|
| macOS Apple Silicon | ✅ 1.0.3 released |
| macOS Intel | build from source |
| Windows | ✅ 1.0.3 released |
| Linux | build from source |
