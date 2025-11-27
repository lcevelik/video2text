# FonixFlow Logging System

## Overview

FonixFlow now includes a comprehensive logging system that records all application activity, even when installed from DMG (not running from source). Logs are saved to the user's computer and can be easily shared for troubleshooting.

## Log File Location

**Location:** `~/.fonixflow/logs/`

- **macOS/Linux:** `/Users/username/.fonixflow/logs/`
- **Windows:** `C:\Users\username\.fonixflow\logs\`

**File Naming:** Each app run creates a new log file with a timestamp:
- Format: `fonixflow_YYYYMMDD_HHMMSS.log`
- Example: `fonixflow_20241126_143022.log` (November 26, 2024 at 14:30:22)

The log directory is automatically created when the app starts.

## Features

### 1. **New Log File Per Session**
- Each app run creates a new timestamped log file
- Format: `fonixflow_YYYYMMDD_HHMMSS.log`
- Makes it easy to identify logs from specific app sessions
- All log files are kept in the same directory

### 2. **Automatic Log Rotation (Within Session)**
- If a single session generates a very large log (>10MB), it will rotate
- Keeps up to 5 backup files per session (fonixflow_TIMESTAMP.log.1, etc.)
- Prevents individual log files from growing too large

### 3. **Persistent Logging**
- Logs are saved even when the app crashes
- Works in both development and installed/bundled modes
- Each app session has its own log file

### 4. **Comprehensive Logging**
- All application events are logged
- Includes timestamps, log levels, and module names
- Logs errors, warnings, info messages, and debug information

### 5. **Easy Access**
- **View Logs Button** in Settings tab
- **Logs Dialog** with full functionality:
  - View recent logs (last 500 lines)
  - Refresh logs
  - Open log folder in file explorer
  - Copy logs to clipboard
  - Save logs to a file
  - Clear logs (with confirmation)

## Using the Logs Dialog

### Accessing Logs

1. Open the app
2. Go to **Settings** tab
3. Click **"View Logs"** button
4. The Logs Dialog will open showing recent log entries

### Logs Dialog Features

- **Refresh**: Reload the latest logs from the file
- **Open Log Folder**: Opens the log directory in your file explorer
- **Copy to Clipboard**: Copies all visible logs to clipboard for easy sharing
- **Save As...**: Save logs to a specific location (useful for sharing)
- **Clear Logs**: Archive current logs and start fresh (with confirmation)

## Log Format

Each log entry includes:
- **Timestamp**: `YYYY-MM-DD HH:MM:SS`
- **Module Name**: Which part of the app logged the message
- **Log Level**: INFO, WARNING, ERROR, DEBUG
- **Message**: The actual log message

Example:
```
2025-11-26 00:15:23 - gui.main_window - INFO - Opening logs dialog
2025-11-26 00:15:23 - gui.workers - INFO - Starting transcription...
2025-11-26 00:15:24 - app.transcriber - INFO - Loading Whisper model: base
```

## Sharing Logs for Support

If you need to share logs for troubleshooting:

1. **Option 1: Use the Logs Dialog**
   - Open Settings → View Logs
   - Click "Save As..." and save to Desktop
   - Share the saved file

2. **Option 2: Copy from Dialog**
   - Open Settings → View Logs
   - Click "Copy to Clipboard"
   - Paste into an email or support ticket

3. **Option 3: Direct File Access**
   - Open Settings → View Logs
   - Click "Open Log Folder"
   - Share the current session's log file (e.g., `fonixflow_20241126_143022.log`)
   - Or share any previous session's log file from the folder

## Log File Information

The Logs Dialog shows:
- **Log file path**: Full path to the log file
- **File size**: Current size in MB
- **Last modified**: When the log was last updated

## Technical Details

### Log Manager

The logging system is managed by `LogManager` class in `gui/managers/log_manager.py`:

- **Initialization**: Called at app startup in `app/fonixflow_qt.py`
- **Log Rotation**: Uses Python's `RotatingFileHandler`
- **File Location**: Always in user's home directory (`~/.fonixflow/logs/`)
- **Encoding**: UTF-8 for international character support

### Integration

- **Main App**: `app/fonixflow_qt.py` initializes logging
- **All Modules**: Use standard Python `logging` module
- **Settings Tab**: "View Logs" button opens `LogsDialog`
- **Logs Dialog**: `gui/dialogs.py` contains `LogsDialog` class

## Log Levels

- **DEBUG**: Detailed diagnostic information (usually only for development)
- **INFO**: General informational messages (normal operation)
- **WARNING**: Warning messages (something unexpected but not critical)
- **ERROR**: Error messages (something went wrong)

## Best Practices

1. **For Users:**
   - Check logs if you encounter errors
   - Share logs when reporting bugs
   - Clear logs periodically if they get too large

2. **For Developers:**
   - Use appropriate log levels
   - Include context in log messages
   - Don't log sensitive information (passwords, keys)

## Troubleshooting

### Logs Not Appearing

If logs aren't being written:
1. Check if `~/.fonixflow/logs/` directory exists
2. Check file permissions (should be writable)
3. Check disk space
4. Look for errors in console output

### Log File Too Large

- Logs automatically rotate at 10MB
- Old logs are archived (up to 5 backups)
- You can manually clear logs via the Logs Dialog

### Can't Find Log File

- Use "Open Log Folder" button in Logs Dialog
- Or navigate to: `~/.fonixflow/logs/`
- Look for files named `fonixflow_YYYYMMDD_HHMMSS.log`

## Summary

- **Location**: `~/.fonixflow/logs/`
- **File Format**: `fonixflow_YYYYMMDD_HHMMSS.log` (new file per app run)
- **Access**: Settings tab → "View Logs" button
- **Features**: View, copy, save, clear logs
- **Rotation**: Automatic at 10MB per session (keeps 5 backups)
- **Works**: Both development and installed/bundled apps
- **Benefits**: Easy to identify and share logs from specific app sessions
