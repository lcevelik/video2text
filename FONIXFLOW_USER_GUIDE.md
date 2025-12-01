# FonixFlow - Complete User Guide for AI Assistant

**Version:** 1.0.0
**Last Updated:** November 28, 2025
**Purpose:** This document provides comprehensive information about FonixFlow for AI assistants helping users.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Core Features](#core-features)
4. [Interface Guide](#interface-guide)
5. [Settings & Configuration](#settings--configuration)
6. [Multi-Language Transcription](#multi-language-transcription)
7. [Audio Filters](#audio-filters)
8. [License System](#license-system)
9. [Troubleshooting](#troubleshooting)
10. [Technical Information](#technical-information)
11. [Frequently Asked Questions](#frequently-asked-questions)

---

## Overview

### What is FonixFlow?

FonixFlow is a professional audio and video transcription application that converts speech to text. It features:

- **Advanced Speech Recognition:** Powered by OpenAI's Whisper AI model
- **Multi-Language Support:** Transcribe content in 50+ languages with automatic detection
- **True Code-Switching:** Handle videos that switch between languages (e.g., Czech ↔ English)
- **Audio Recording:** Record microphone and system audio simultaneously
- **Professional Audio Processing:** Optional noise gate and compressor filters
- **Cross-Platform:** Available for macOS (Intel & Apple Silicon), Windows, and Linux

### Key Capabilities

- ✅ Transcribe audio and video files in 50+ languages
- ✅ Record audio directly from microphone and system audio
- ✅ Automatic language detection and code-switching support
- ✅ Export transcripts as TXT, SRT (subtitles), or VTT format
- ✅ Professional audio filters for cleaner transcriptions
- ✅ Offline operation (no internet required after model download)
- ✅ Free version with 500-word limit, premium version unlimited

---

## Getting Started

### System Requirements

**macOS:**
- macOS 12.3 (Monterey) or later
- Intel Mac or Apple Silicon (M1/M2/M3/M4)
- 8GB RAM minimum, 16GB recommended
- 5GB free disk space for models

**Windows:**
- Windows 10 or Windows 11 (64-bit)
- 8GB RAM minimum, 16GB recommended
- 5GB free disk space for models

**Linux:**
- Modern Linux distribution
- 8GB RAM minimum, 16GB recommended
- 5GB free disk space for models

### First Launch

1. **Grant Permissions** (macOS):
   - Microphone access: Required for recording
   - Screen recording: Required for system audio capture
   - The app will prompt you on first use

2. **Model Download**:
   - First transcription downloads AI models automatically (~3.1 GB)
   - This happens once; subsequent transcriptions are instant
   - Progress shown in the interface

3. **License** (Optional):
   - App works without license (500-word limit)
   - Activate license for unlimited transcription
   - See [License System](#license-system) section

### Quick Start Workflow

**To transcribe a file:**
1. Open FonixFlow
2. Click **Upload** tab (or drag & drop a file)
3. Select your audio/video file
4. Choose language settings when prompted
5. Wait for transcription to complete
6. View results in **Transcript** tab
7. Click **Save Transcription** to export

**To record and transcribe:**
1. Open FonixFlow
2. Click **Record** tab
3. Click **Start Recording**
4. Speak or play audio (recording duration shows in real-time)
5. Click **Stop Recording**
6. Recording is saved to your recordings folder
7. **"Transcribe Recording" button appears**
8. Click **"Transcribe Recording"**
9. Language selection dialog appears
10. Choose language(s) and transcription starts
11. Auto-switches to Transcript tab when complete

---

## Core Features

### 1. Audio/Video File Transcription

**Supported Formats:**
- Audio: MP3, WAV, M4A, AAC, FLAC, OGG, WMA
- Video: MP4, MOV, AVI, MKV, WMV, FLV, WEBM

**How it works:**
1. Drag and drop file or click to browse
2. FonixFlow extracts audio from video files
3. AI processes the audio and generates text
4. Results appear in Transcript tab with timestamps

**Processing Time:**
- Typical: 1-2 minutes per 10 minutes of audio
- Depends on: File length, language complexity, computer speed
- Multi-language content may take longer

### 2. Audio Recording

**What you can record:**
- **Microphone only:** Your voice
- **System audio only:** Computer speakers/headphones output
- **Both simultaneously:** Meetings, interviews, presentations

**Recording Controls:**
- **Start Recording:** Begin capturing audio
- **Stop Recording:** End recording and start automatic transcription
- **Recording location:** Configurable in Settings (default: ~/.fonixflow/recordings/)

**Best Practices:**
- Use a good quality microphone for best results
- Minimize background noise
- Speak clearly with natural pauses
- For meetings: Ensure system audio permission is granted

### 3. Transcription Output

**What you get:**
- Full text transcription
- Word-level timestamps (for SRT/VTT)
- Language detection information
- Segment count and duration
- Language timeline (for multi-language content)

**Export Formats:**

**TXT (Plain Text):**
- Simple text file
- No timestamps
- Easy to edit and share
- Best for: Documents, notes, general text

**SRT (SubRip Subtitles):**
- Industry-standard subtitle format
- Includes timestamps
- Works with video players, YouTube, etc.
- Best for: Adding subtitles to videos

**VTT (WebVTT):**
- Web-based subtitle format
- Includes timestamps
- Works with HTML5 video players
- Best for: Web videos, modern platforms

### 4. Language Support

**50+ Languages Supported:**
- English, Spanish, French, German, Italian, Portuguese
- Polish, Czech, Slovak, Russian, Ukrainian
- Chinese (Mandarin), Japanese, Korean
- Arabic, Hebrew, Turkish, Greek
- Hindi, Thai, Vietnamese, Indonesian
- Dutch, Swedish, Danish, Norwegian, Finnish
- Romanian, Hungarian, Bulgarian
- And many more...

**Language Detection:**
- Automatic: App detects the language automatically
- Manual: Choose specific language(s) before transcription
- Multi-language: Select multiple languages for code-switching content

---

## Interface Guide

### Layout Overview

```
┌────────────────────────────────────────────────────┐
│  [FonixFlow Logo]                                  │
├────────────────────────────────┬───────────────────┤
│                                │  🎙️ Record       │
│         Content Area           │  📁 Upload        │
│                                │  📄 Transcript    │
│                                │  ⚙️  Settings     │
└────────────────────────────────┴───────────────────┘
```

**Clean, minimal design with four main tabs (vertical on right side):**

### Record Tab

**What you see:**
- Large "Start Recording" button (center)
- Progress bar
- Recording status information

**Workflow:**
1. Click "Start Recording" → Button turns red, shows "Stop Recording"
2. Recording duration shown in real-time (e.g., 00:00:25)
3. Click "Stop Recording" → Recording is saved
4. Message shows: "Recording complete (X.Xs). Ready for manual transcription."
5. "Transcribe Recording" button appears below
6. Click "Transcribe Recording" → Language selection dialog appears
7. Choose language(s) → Transcription starts
8. Auto-switches to Transcript tab when complete

### Upload Tab

**What you see:**
- Drag & drop zone with dashed border
- "Drag and drop video/audio file" text
- Progress bar during transcription

**Workflow:**
1. Drag file onto zone OR click to browse
2. Language selection dialog appears
3. Choose single or multi-language mode
4. Select language(s) from list
5. Transcription starts automatically
6. Progress updates in real-time
7. Auto-switches to Transcript tab when complete

**Supported Actions:**
- Drag & drop: Fastest method
- Click to browse: Traditional file picker
- Multiple attempts: Click "New Transcription" to start over

### Transcript Tab

**What you see:**
- Language information header (after transcription)
- Large text area with transcription
- Format selector (TXT/SRT/VTT)
- Save button

**Transcription Display:**
```
Languages detected: Czech, English | 45 segments
Duration: 5 minutes 23 seconds

[Transcription text appears here]

============================================================
🌍 LANGUAGE TIMELINE:
============================================================

[00:00:00 - 00:00:05] Language: Czech (CS)
[00:00:05 - 00:00:10] Language: English (EN)
[00:00:10 - 00:00:15] Language: Czech (CS)
```

**Save Process:**
1. Review transcription text
2. Select export format (TXT/SRT/VTT)
3. Click "💾 Save Transcription"
4. Choose location and filename
5. File saved successfully

### Settings Tab

**Click the Settings tab** (⚙️ icon on right side) to access all configuration options.

**Quick Actions (row of buttons):**
- **Change Folder** - Change recording directory location
- **Open Folder** - Open recording directory in Finder/Explorer

**Recordings Directory Card:**
- Shows current recording location
- Updates automatically when changed

**Settings (row of toggle buttons):**
- **Enhance Audio** - Toggle audio filters (Noise Gate + Compressor)
  - Default: Disabled
  - See [Audio Filters](#audio-filters) section

- **Deep Scan** - Toggle comprehensive language detection
  - Default: Disabled (Fast Mode)
  - See [Multi-Language Transcription](#multi-language-transcription)

- **Activate** - License activation for unlimited transcription
  - Opens license key entry dialog
  - See [License System](#license-system)

**Logs:**
- **View Logs** - View application logs for troubleshooting

---

## Settings & Configuration

### Recording Directory

**Default Location:**
- macOS: `~/Music/FonixFlow`
- Windows: `%USERPROFILE%\Music\FonixFlow`
- Linux: `~/Music/FonixFlow`

**Change Directory:**
1. Click **Settings** tab (⚙️ icon on right side)
2. Click "Change Folder" button
3. Select folder in dialog
4. All future recordings saved there
5. Previous recordings remain in old location

**Open Directory:**
1. Click **Settings** tab (⚙️ icon on right side)
2. Click "Open Folder" button
3. Opens folder in Finder/Explorer for quick access to your recordings

### Audio Filters (Advanced)

**What it does:**
- **Noise Gate:** Removes background noise during silence
- **Compressor:** Balances volume levels for clearer speech
- **Inspired by:** OBS Studio's professional audio filters

**When to use:**
- ✅ Noisy environments (traffic, air conditioning)
- ✅ Inconsistent volume levels
- ✅ Low-quality microphone recordings
- ✅ Multiple speakers with different volumes

**When NOT to use:**
- ❌ High-quality studio recordings (already clean)
- ❌ Very short clips (< 1 minute)
- ❌ If unsure (disabled by default for a reason)

**How it works:**
- Processes audio before transcription
- Uses streaming processing for long videos (>3 minutes)
- Memory-efficient: Handles hours-long videos
- Creates temporary processed file
- Original file unchanged

**Performance:**
- Short files (<3 min): In-memory processing, very fast
- Long files (>3 min): Streaming 60-second chunks
- Memory usage: ~4MB per chunk (vs 181MB without streaming)
- Adds: ~10-30% processing time

**To enable:**
1. Click **Settings** tab (⚙️ icon on right side)
2. Click "Enhance Audio" button to toggle on
3. Applies to all future transcriptions
4. Disabled by default

**Note:** Audio filters are **disabled by default** because most audio files don't need them, and they add processing time.

### Deep Scan (Multi-Language)

**What it is:**
Two modes for detecting language changes in multi-language videos.

**Fast Mode (Default - Deep Scan OFF):**
- Uses text-based heuristic analysis
- Analyzes the transcription text for language patterns
- Looks for language-specific characters and words
- **Speed:** 10-20x faster than Deep Mode
- **Best for:** Most multi-language content
- **Accuracy:** Very good for languages with distinctive features

**Deep Mode (Deep Scan ON):**
- Uses comprehensive audio segmentation
- Re-analyzes audio chunks for precise language detection
- More thorough analysis of language boundaries
- **Speed:** Slower (≈ +25-40% runtime)
- **Best for:** Highly interwoven code-switching (rapid language changes)
- **Accuracy:** Excellent for very short alternations

**When to enable Deep Scan:**
- Rapid language switching (every few seconds)
- Languages with similar characteristics
- Short interwoven phrases
- When Fast Mode misses some switches

**When to use Fast Mode (default):**
- Most multi-language content
- Longer segments in each language (>30 seconds)
- Speed is important
- Languages with distinctive features (Czech ↔ English)

**To enable:**
1. Click **Settings** tab (⚙️ icon on right side)
2. Click "Deep Scan" button to toggle on
3. Applies to next transcription
4. Disabled by default for speed

---

## Multi-Language Transcription

### How It Works (v1.0.0 Optimized)

FonixFlow uses an intelligent **text-based language detection** system that's 5-10x faster than older methods.

**Process:**
1. **Single transcription pass** with word-level timestamps (no redundant passes)
2. **Instant text-based language detection** using linguistic heuristics:
   - Diacritic patterns (č, ř, š for Czech; é, à for French, etc.)
   - Language-specific stopwords and common words
   - Character set analysis
3. Allowed-language list constrains classification (suppresses outliers)
4. Segments merged → timeline + combined text

**Performance:**
- ✅ No chunk re-transcription (eliminated 75+ subprocess calls)
- ✅ Text analysis completes in <1 second (was 180+ seconds in old system)
- ✅ Audio sampling: 3 strategic samples (was up to 25)
- ✅ Total speedup: **5.2x faster** on typical 5-minute multi-language files

### Language Mode Dialog

**Appears when you:**
- Upload a file for transcription
- Stop a recording

**Two options:**

**1. Single Language**
- Choose ONE language from dropdown
- Faster processing
- Best for: Videos in one language only
- Special option: "Other" - Auto-detects any language

**2. Multi-Language**
- Check multiple languages from list
- Handles code-switching (language changes during video)
- Slower but more accurate
- Best for: Bilingual speakers, international meetings, educational content

**Recommended Selections:**

For **English-only content:**
- Single Language → English

For **Czech ↔ English code-switching:**
- Multi-Language → Check Czech + English

For **Unknown/Multiple languages:**
- Single Language → Other (auto-detect)
- OR Multi-Language → Select all likely languages

### Language Timeline

**What it is:**
A visual representation of when languages change throughout your video.

**Example output:**
```
============================================================
🌍 LANGUAGE TIMELINE:
============================================================

[00:00:00 - 00:00:05] Language: Czech (CS)
[00:00:05 - 00:00:10] Language: English (EN)
[00:00:10 - 00:00:15] Language: Czech (CS)
[00:00:15 - 00:01:30] Language: English (EN)
```

**Appears when:**
- Multiple languages detected in transcription
- Shown at bottom of transcript
- Included in saved TXT files

**Use cases:**
- Verify language detection accuracy
- Understand content structure
- Create separate subtitles per language
- Analyze bilingual speech patterns

### Supported Multi-Language Pairs

**Optimized for these combinations:**
- Czech ↔ English (very common, well-tested)
- Spanish ↔ English
- French ↔ English
- German ↔ English
- Polish ↔ English
- Any language pair with distinctive features

**How to get best results:**
1. Speak clearly with pauses between language switches
2. Avoid extremely rapid switching (< 2 seconds per language)
3. Use Deep Scan for highly interwoven content
4. Select only the languages actually present (improves accuracy)

### Performance Tips

**For fastest processing:**
- Use Single Language mode when possible
- Keep Deep Scan disabled (default)
- Select minimal number of languages
- Use high-quality audio (less re-processing needed)

**For best accuracy:**
- Enable Deep Scan for complex code-switching
- Select all relevant languages
- Use Audio Filters if source is noisy
- Ensure clear speech with pauses

---

## Audio Filters

### What Are Audio Filters?

Professional-grade audio processing inspired by OBS Studio:

**Noise Gate:**
- Removes background noise during silence
- Only lets sound through above a threshold
- Keeps speech, cuts out fans, air conditioning, keyboard typing

**Enhanced Compressor:**
- Balances volume differences
- Makes quiet parts louder, loud parts softer
- Results in more consistent audio levels

**Combined effect:** Cleaner, more consistent audio for better transcription accuracy.

### Technical Details

**Default Settings (Optimized):**
- Noise Gate Threshold: -35 dB
- Noise Gate Attack: 25 ms
- Noise Gate Release: 150 ms
- Compressor Threshold: -18 dB
- Compressor Ratio: 3:1
- Compressor Attack: 5 ms
- Compressor Release: 100 ms

These settings work well for most speech content.

### Memory-Efficient Streaming

**How it works:**
- Files < 3 minutes: Loaded entirely into memory (fast)
- Files > 3 minutes: Processed in 60-second chunks (memory-efficient)
- Uses WAV format for reliability
- Handles videos of any length (even hours-long)

**Memory usage:**
- Old system: 181 MB for 49-minute video (crashed on some systems)
- New system: ~4 MB per 60-second chunk (stable)
- Tested with multi-hour videos: No memory issues

### When Audio Filters Help

**Good use cases:**
✅ Home office recordings (background noise)
✅ Meeting recordings (multiple speakers, varying distances)
✅ Phone recordings (inconsistent levels)
✅ Conference recordings (room echo, air conditioning)
✅ Interview recordings (different microphones)
✅ Podcast recordings (voice processing)

**When to skip:**
❌ Professional studio recordings
❌ High-quality voiceovers
❌ Already-processed audio
❌ Very short clips (overhead not worth it)

### Performance Impact

**Processing time:**
- Short files (<3 min): +5-10% processing time
- Long files (>3 min): +10-30% processing time
- Memory usage: Minimal (4MB chunks)
- Disk usage: Temporary files deleted after transcription

**Quality impact:**
- Noise reduction: Moderate to significant
- Volume consistency: Significant improvement
- Transcription accuracy: 5-15% better on noisy sources
- No impact on already-clean audio

### How to Use

**Enable/Disable:**
1. Click **Settings** tab (⚙️ icon on right side)
2. Click "Enhance Audio" button to toggle
3. Applies to all future transcriptions
4. Existing transcriptions not affected
5. Can toggle anytime

**Disabled by default** - Enable only if you need it.

---

## License System

### Free vs. Premium

**Free Version (No License):**
- ✅ All features available
- ✅ Unlimited recordings
- ✅ Unlimited file uploads
- ⚠️ **Transcription limited to 500 words**
- ✅ All export formats (TXT, SRT, VTT)
- ✅ Multi-language support
- ✅ Audio filters

**Premium Version (With License):**
- ✅ **Unlimited transcription** (no word limit)
- ✅ All free features included
- ✅ Priority support
- ✅ Future updates

**What happens at 500-word limit:**
- Transcription stops at 500 words
- Message appears: "Free version limit is 500 words. Activate a license for unlimited transcription."
- Partial transcript can be saved
- All features still work normally

### How to Activate License

**Step-by-step:**
1. Click **Settings** tab (⚙️ icon on right side)
2. Click **Activate** button
3. Enter your license key in the dialog
4. Click "Activate"
5. Validation occurs (local file or online API)
6. Success message: "✓ License key validated successfully!"
7. Unlimited transcription now enabled

**Validation methods:**
- **Local:** Checks `licenses.txt` file (for testing/offline)
- **Online:** Validates via LemonSqueezy API (for production)
- **Automatic:** App tries local first, then online

**License persistence:**
- Saved to: `~/.fonixflow_config.json`
- Survives app restarts
- Validates on every launch
- Remove file to deactivate

### Where to Get License

**Purchase:**
1. Visit: https://fonixflow.com/#/pricing
2. Choose your plan
3. Complete purchase
4. Receive license key via email
5. Activate in FonixFlow

**Pricing:**
- Check https://fonixflow.com/#/pricing for current pricing
- One-time purchase or subscription (varies)
- Multiple device support (check license terms)

### Test License (Development)

**For testing only:**
- Test key: `fonixflow`
- Add to `licenses.txt` in app folder
- Works offline
- Not for production use

---

## Troubleshooting

### Common Issues

#### "No Audio Devices Found"

**Cause:** Microphone permissions not granted or no microphone connected

**Solution (macOS):**
1. System Settings → Privacy & Security → Microphone
2. Enable FonixFlow
3. Restart FonixFlow

**Solution (Windows):**
1. Settings → Privacy → Microphone
2. Enable "Allow apps to access your microphone"
3. Enable FonixFlow specifically
4. Restart FonixFlow

**Solution (Linux):**
1. Check microphone connected: `arecord -l`
2. Test recording: `arecord test.wav`
3. Configure PulseAudio/ALSA
4. Restart FonixFlow

#### Transcription is Slow

**Normal speed:**
- 1-2 minutes per 10 minutes of audio
- First transcription downloads models (one-time, ~3.1 GB)
- Multi-language content 20-30% slower

**If unusually slow:**
- Check CPU usage: Should be 80-100% during transcription
- Close other applications
- Check disk space (models need 5GB)
- Disable Audio Filters if not needed
- Use Single Language mode instead of Multi-Language

**First transcription:**
- Downloads AI models: ~3.1 GB
- Takes 5-30 minutes (depending on internet speed)
- Progress shown in interface
- Subsequent transcriptions instant (models cached)

#### Wrong Language Detected

**For Single Language mode:**
- Select specific language instead of "Other"
- Check audio quality (background noise affects detection)
- Try enabling Audio Filters for cleaner input

**For Multi-Language mode:**
- Ensure you selected the correct languages
- Enable Deep Scan for better accuracy
- Check that speakers enunciate clearly
- Ensure pauses between language switches

**If language timeline is wrong:**
- Enable Deep Scan (Menu → Settings)
- Select only languages actually present
- Avoid selecting too many languages (reduces accuracy)

#### Application Crashes

**On macOS:**
- Check Console app for crash logs
- Grant all permissions (Microphone, Screen Recording)
- Update to latest macOS version
- Reinstall FonixFlow

**On Windows:**
- Check Event Viewer for errors
- Run as Administrator (right-click → Run as Administrator)
- Update Windows to latest version
- Disable antivirus temporarily (some flag PyInstaller apps)

**On Linux:**
- Check terminal output: `./FonixFlow`
- Install missing dependencies: `ldd FonixFlow`
- Check ALSA/PulseAudio configuration

#### Out of Memory / Crash During Long Video

**Old versions:** Audio filters could crash on long videos
**Version 1.0.0+:** Fixed with streaming processing

**If still happening:**
- Update to FonixFlow 1.0.0 or later
- Disable Audio Filters (Menu → Settings)
- Close other applications
- Add more RAM (8GB minimum, 16GB recommended)

#### Transcription Shows Only Periods (`. . . .`)

**Cause:** Whisper AI hallucinating silence (fixed in v1.0.0)

**Solution:**
- Update to FonixFlow 1.0.0 or later
- Issue fixed with `condition_on_previous_text=False` parameter
- Choose specific language instead of "Other"

#### Export Fails / Cannot Save File

**Causes:**
- No write permission to selected folder
- Disk full
- File already open in another program

**Solutions:**
- Choose different save location
- Free up disk space
- Close file if open in text editor/video player
- Check folder permissions

### Getting Help

**Support Channels:**
- Website: https://fonixflow.com/
- GitHub Issues: Check project repository
- Email: support@fonixflow.com (if available)

**When reporting issues, include:**
- FonixFlow version (Menu → About)
- Operating system and version
- File format and size
- Steps to reproduce
- Error messages (exact text)
- Screenshots if applicable

---

## Technical Information

### AI Model Information

**Whisper AI:**
- Developed by: OpenAI
- Technology: Deep learning speech recognition
- Training: 680,000 hours of multilingual data
- Accuracy: State-of-the-art (better than commercial services)

**Model Sizes:**
- Tiny: 39M parameters, fastest, less accurate
- Base: 74M parameters, **recommended for detection**, good balance
- Small: 244M parameters, good accuracy
- Medium: 769M parameters, **recommended for transcription**, excellent accuracy
- Large: 1550M parameters, best accuracy, slowest

**FonixFlow uses:**
- Detection (Deep Scan): Base model
- Transcription (Multi-language): Large model
- Single language: Base model (faster)

**Model storage:**
- macOS: `~/.cache/whisper/`
- Windows: `%USERPROFILE%\.cache\whisper\`
- Linux: `~/.cache/whisper/`
- Size: ~3.1 GB total
- Downloaded once, reused forever

### Audio Processing Details

**Supported input:**
- Sample rates: 8kHz to 96kHz (automatically resampled to 16kHz)
- Channels: Mono or stereo (converted to mono)
- Bit depth: 8-bit to 32-bit float

**Internal processing:**
- Whisper requires: 16kHz, mono, 16-bit
- FonixFlow handles conversion automatically
- Uses ffmpeg for audio extraction
- Temporary files: WAV format, deleted after transcription

**Audio Filters (when enabled):**
- Noise Gate: Spectral subtraction + threshold
- Compressor: Dynamic range compression
- Format: 32-bit float during processing
- Output: 16-bit WAV for transcription

### File Storage Locations

**Configuration:**
- macOS/Linux: `~/.fonixflow_config.json`
- Windows: `%USERPROFILE%\.fonixflow_config.json`
- Stores: License key, settings, preferences

**Logs:**
- macOS/Linux: `~/.fonixflow/logs/`
- Windows: `%USERPROFILE%\.fonixflow\logs\`
- Files: `fonixflow.log`, `fonixflow.log.1`, etc.
- Rotation: 5MB per file, keeps 3 backups

**Temporary files:**
- macOS/Linux: `~/.fonixflow/temp/`
- Windows: `%USERPROFILE%\.fonixflow\temp\`
- Cleaned up: After transcription or on app exit

**Model cache:**
- macOS/Linux: `~/.cache/whisper/`
- Windows: `%USERPROFILE%\.cache\whisper\`
- Size: ~3.1 GB
- Never deleted by app (manual deletion safe, will re-download)

**Recordings:**
- Default: `~/Music/FonixFlow/` (macOS/Linux) or `%USERPROFILE%\Music\FonixFlow\` (Windows)
- Configurable in Settings
- Format: WAV, 16-bit, 44.1kHz, stereo

### Update System

**Automatic Updates:**
- Checks for updates: 3 seconds after launch (one-time per day)
- Update check throttle: 24 hours minimum
- Platform detection: Automatic (macOS Intel/ARM, Windows, Linux)
- Update method: Download ZIP, verify SHA256, replace app

**Update Channels (Platform-Specific):**
- macOS Intel: `https://storage.googleapis.com/fonixflow-files/updates/macos-intel/manifest.json`
- macOS Apple Silicon: `https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json`
- Windows: `https://storage.googleapis.com/fonixflow-files/updates/windows/manifest.json`
- Linux: `https://storage.googleapis.com/fonixflow-files/updates/linux/manifest.json`

**Update Process:**
1. App checks manifest for new version
2. If update available, shows dialog with release notes
3. User clicks "Update Now"
4. Downloads update ZIP from GCS
5. Verifies SHA256 hash
6. Replaces app bundle
7. Restarts automatically

**Manual Updates:**
- Download from: https://fonixflow.com/
- Install normally (DMG/Installer/AppImage)
- Settings and license preserved

### Privacy & Security

**Data Collection:**
- FonixFlow does NOT send your audio/transcriptions anywhere
- All processing happens locally on your computer
- Internet only used for: Model downloads, license validation, updates

**License Validation:**
- Sends license key to LemonSqueezy API (HTTPS)
- No audio or transcription data transmitted
- Validates only when you activate or on app launch

**Security Features:**
- SHA256 hash verification for updates
- HTTPS-only downloads
- No telemetry or analytics
- No cloud storage or backups

---

## Frequently Asked Questions

### General Questions

**Q: Do I need internet to use FonixFlow?**
**A:** After initial setup, no. First transcription downloads AI models (~3.1 GB), which requires internet. After that, everything works offline. Internet only needed for license validation and updates.

**Q: How accurate is the transcription?**
**A:** Very accurate (90-95%+ for clear audio). Depends on:
- Audio quality (better mic = better results)
- Background noise (use Audio Filters if noisy)
- Speaker clarity (clear speech = better accuracy)
- Language (some languages more accurate than others)
- Whisper AI is state-of-the-art, often better than paid services.

**Q: Can I transcribe multiple files at once?**
**A:** No, one at a time. Process: Transcribe → Save → New Transcription → Repeat.

**Q: What's the maximum file length?**
**A:** Unlimited. Tested with multi-hour videos. Audio Filters use streaming processing for long files.

**Q: Can I edit the transcription before saving?**
**A:** Yes! Click in the text area in Transcript tab and edit directly.

**Q: Does it work offline?**
**A:** Yes, after models are downloaded (first transcription). License validation requires internet once.

### Multi-Language Questions

**Q: What is code-switching?**
**A:** When a speaker switches between languages mid-sentence or mid-video. Example: "Hello, jak se máš?" (English → Czech). FonixFlow handles this automatically.

**Q: How do I transcribe a bilingual video?**
**A:**
1. Choose Multi-Language mode
2. Select both languages (e.g., Czech + English)
3. FonixFlow detects switches and provides language timeline

**Q: Should I use Fast Mode or Deep Scan?**
**A:**
- **Fast Mode (default):** Most videos, 10-20x faster
- **Deep Scan:** Rapid switching every few seconds, more accurate
- Start with Fast Mode; enable Deep Scan if results unsatisfactory

**Q: Can it handle three or more languages?**
**A:** Yes! Select all languages in Multi-Language mode. More languages = slightly slower processing.

**Q: What if I don't know what languages are in the video?**
**A:** Choose Single Language → "Other". The AI will auto-detect.

### Technical Questions

**Q: Which Whisper model does FonixFlow use?**
**A:**
- Single Language: Base model (fast, accurate)
- Multi-Language detection: Base model
- Multi-Language transcription: Large model (best accuracy)

**Q: How much disk space do I need?**
**A:** Minimum 5 GB for AI models. Actual usage: ~3.1 GB for models + temporary files during processing.

**Q: Can I use my GPU to speed up transcription?**
**A:** FonixFlow automatically uses GPU if available (NVIDIA CUDA, Apple Metal). No configuration needed.

**Q: Why is first transcription so slow?**
**A:** Downloading AI models (~3.1 GB). Subsequent transcriptions are fast (models cached locally).

**Q: Where are the AI models stored?**
**A:**
- macOS/Linux: `~/.cache/whisper/`
- Windows: `%USERPROFILE%\.cache\whisper\`
- Safe to delete (will re-download automatically)

### Audio Filter Questions

**Q: Should I enable Audio Filters?**
**A:** Only if your audio is noisy or has inconsistent volume. Most users don't need it.

**Q: Do Audio Filters improve accuracy?**
**A:** For noisy audio, yes (5-15% better). For clean audio, minimal difference.

**Q: Why are Audio Filters disabled by default?**
**A:** They add 10-30% processing time. Most audio doesn't need them.

**Q: Can I customize filter settings?**
**A:** Not in the GUI (advanced users can edit source code). Default settings optimized for speech.

**Q: Will Audio Filters damage my original file?**
**A:** No. FonixFlow creates a temporary processed copy, original unchanged.

### License Questions

**Q: Can I try before buying?**
**A:** Yes! Free version allows 500 words per transcription. Test all features before purchasing.

**Q: What's included in the premium license?**
**A:** Unlimited transcription (no 500-word limit). All other features same as free.

**Q: Do I need separate licenses for multiple computers?**
**A:** Check your license terms from LemonSqueezy. Varies by plan.

**Q: What if my license expires?**
**A:** Returns to free version (500-word limit). Existing transcriptions remain accessible.

**Q: Can I get a refund?**
**A:** Check refund policy at https://fonixflow.com/ or LemonSqueezy terms.

**Q: Where is my license key stored?**
**A:** In `~/.fonixflow_config.json`. Keep this file backed up.

### Troubleshooting Questions

**Q: Why does transcription show only periods (`. . . .`)?**
**A:** Fixed in v1.0.0. Update to latest version. If using older version, select specific language instead of "Other".

**Q: App crashes on long videos (>30 minutes)**
**A:** Fixed in v1.0.0 with streaming processing. Update to latest version.

**Q: Transcription is wrong / nonsensical**
**A:**
- Check audio quality (try Audio Filters)
- Select correct language manually
- Ensure speakers speak clearly
- Check for extreme background noise

**Q: Can't save transcription / "Permission denied"**
**A:** Choose different folder, check disk space, close file if open elsewhere.

**Q: App won't start / crashes immediately**
**A:**
- Grant microphone permission (Settings → Privacy)
- Update OS to latest version
- Reinstall FonixFlow
- Check antivirus (some flag PyInstaller apps)

---

## Version History

### Version 1.0.0 (November 28, 2025)

**New Features:**
- ✨ Deep Scan implementation: Fast Mode vs Deep Mode for language detection
- ✨ Audio Filters with streaming processing (handles hours-long videos)
- ✨ Multi-platform automatic updates (macOS Intel/ARM, Windows, Linux)
- ✨ SHA256 hash verification for secure updates

**Bug Fixes:**
- 🐛 Fixed transcription hallucination with "Other" language mode
- 🐛 Fixed memory crash on long videos with audio filters
- 🐛 Fixed repeat transcription bug (New Transcription now works correctly)

**Performance Improvements:**
- ⚡ Streaming audio filter processing: 4MB chunks vs 181MB full load
- ⚡ Text-based language detection: 5.2x faster than old audio re-transcription
- ⚡ Platform-specific updates reduce download sizes

**Other Changes:**
- 📝 Audio Filters disabled by default (enable in Settings)
- 📝 Comprehensive documentation updates
- 📝 Improved error handling and logging

---

## Support & Resources

**Official Website:**
https://fonixflow.com/

**Documentation:**
- User Guide: This document
- Build Guides: `doc/BUILD_MACOS.md`, `doc/BUILD_WINDOWS.md`
- Release Process: `MULTIPLATFORM_RELEASE.md`

**Contact:**
- Support: support@fonixflow.com (if available)
- Issues: GitHub repository (check website for link)

**Community:**
- Check website for forums, Discord, or community channels

---

**End of FonixFlow User Guide**
**Version 1.0.0 | Last Updated: November 28, 2025**
