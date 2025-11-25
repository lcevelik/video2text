# FonixFlow License Requirements and Features

## Overview

FonixFlow uses a license key system to unlock premium transcription features. This document outlines which features require a license and which are available for free.

---

## 🔓 Features Available WITHOUT License

These features work completely without any license key:

### 1. **Audio Recording** ✅
- Start and stop audio recording
- Record from microphone
- Record system audio (speaker output)
- Record both microphone and system audio simultaneously
- Save recordings to disk
- View recording duration and status
- Access all recording controls

### 2. **File Upload** ✅
- Drag and drop audio/video files
- Browse and select files from your computer
- Load files into the application
- View file information
- Support for multiple audio/video formats

### 3. **Settings & Configuration** ✅
- Change theme (Dark/Light/Auto)
- Change recording directory
- Toggle "Enhance Audio" setting
- Toggle "Deep Scan" setting
- Access all application settings
- Configure audio processing options

### 4. **User Interface** ✅
- Navigate between tabs (Record, Upload, Transcript, Settings)
- View all interface elements
- Use all UI controls and buttons
- Access help and documentation

---

## 🔒 Features That REQUIRE License Key

These features require a valid license key to function:

### 1. **Transcription** 🔑
- **Transcribing audio/video files** - Convert speech to text from uploaded files
- **Transcribing recordings** - Convert recorded audio to text
- **Multi-language transcription** - Transcribe content in multiple languages
- **Language detection** - Automatic detection of spoken languages
- **Timestamps and segments** - Generate time-stamped transcription segments

**What happens without license:**
- When you try to transcribe, you'll see: "A valid license key is required to use transcription"
- You'll be prompted to enter your license key
- Option to visit the pricing page to purchase a license

### 2. **Saving Transcription Results** 🔑
- **Save as TXT** - Plain text format
- **Save as SRT** - Subtitle format
- **Save as VTT** - WebVTT subtitle format
- **Export transcription data** - All export formats

**Note:** Saving requires transcription to complete first, which needs a license.

---

## 🔑 License Activation

### How to Activate

1. **Open Settings Tab**
   - Click on the "Settings" tab in the right sidebar

2. **Click "Activate" Button**
   - Find the "Activation" section
   - Click the "Activate" button

3. **Enter License Key**
   - A dialog will open
   - Enter your license key
   - Click "Activate"

4. **Validation**
   - The app validates your key against:
     - Local `licenses.txt` file (for offline validation)
     - LemonSqueezy API (for online validation)

5. **Success**
   - If valid, you'll see: "✓ License key validated successfully! Saving..."
   - The key is saved to `~/.fonixflow_config.json`
   - Premium features are now unlocked

### License Key Storage

- **Location:** `~/.fonixflow_config.json`
- **Persistence:** License key persists across app restarts
- **Automatic Validation:** License is validated on app startup

---

## 🧪 Testing License System

### For Development/Testing

A test license key is available in `licenses.txt`:
- **Test Key:** `fonixflow`
- Add this key to test the activation flow
- Works for offline validation during development

### License Validation Methods

1. **Local Validation (Offline)**
   - Checks `licenses.txt` file in project root
   - One license key per line
   - Useful for development and testing

2. **Online Validation (Production)**
   - Validates via LemonSqueezy API
   - Checks license status: `active`, `inactive`, `expired`
   - Requires internet connection

---

## 📋 Feature Comparison Table

| Feature | Free (No License) | Premium (With License) |
|---------|-------------------|----------------------|
| **Audio Recording** | ✅ Full Access | ✅ Full Access |
| **File Upload** | ✅ Full Access | ✅ Full Access |
| **Settings** | ✅ Full Access | ✅ Full Access |
| **Transcription** | ❌ Blocked | ✅ Full Access |
| **Save Results** | ❌ Blocked* | ✅ Full Access |
| **Multi-Language** | ❌ Blocked | ✅ Full Access |
| **Language Detection** | ❌ Blocked | ✅ Full Access |

*Saving requires transcription, which needs a license

---

## 🔧 Technical Implementation

### License Check Location

The license validation occurs in:
- **File:** `gui/main_window.py`
- **Function:** `start_transcription()` (line ~1741)
- **Check:** `if not self.license_valid:`

### License State Variables

- `self.license_key` - Stores the license key string
- `self.license_valid` - Boolean flag indicating if license is valid
- `self.is_license_active()` - Helper method to check license status

### Code Example

```python
# Check if license is active
if self.is_license_active():
    # Enable premium features
    enable_transcription()
else:
    # Show activation prompt
    show_license_required_message()
```

---

## 🛒 Purchasing a License

If you don't have a license key:

1. Click "Activate" button in Settings
2. When prompted, click "Buy License"
3. You'll be redirected to: https://fonixflow.com/
4. Purchase a license and receive your key
5. Return to the app and activate with your key

---

## ❓ Frequently Asked Questions

### Q: Can I use the app without a license?
**A:** Yes! You can record audio, upload files, and use all settings. Only transcription requires a license.

### Q: Do I need internet to activate?
**A:** For production licenses, yes (LemonSqueezy API). For testing, you can use local `licenses.txt` file.

### Q: Does the license expire?
**A:** License validity is checked via the LemonSqueezy API. Expired licenses will be rejected.

### Q: Can I use multiple devices?
**A:** This depends on your license type from LemonSqueezy. Check your license terms.

### Q: Where is my license key stored?
**A:** In `~/.fonixflow_config.json` on your computer. It's automatically loaded on app startup.

### Q: What if I lose my license key?
**A:** Contact support or check your LemonSqueezy account to retrieve your license key.

---

## 📝 Summary

- **Free Features:** Recording, file upload, settings, UI navigation
- **Premium Features:** Transcription, saving results, multi-language support
- **Activation:** Settings tab → Activate button → Enter license key
- **Storage:** License saved to `~/.fonixflow_config.json`
- **Validation:** Local file or LemonSqueezy API

For questions or support, visit: https://fonixflow.com/
