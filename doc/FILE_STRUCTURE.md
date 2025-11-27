# FonixFlow File Structure

## Overview

All user data files are now consolidated in the `~/.fonixflow/` directory for better organization and easier management.

## Directory Structure

```
~/.fonixflow/
├── config.json              # Application settings and license key
├── logs/                    # Application logs
│   ├── fonixflow_YYYYMMDD_HHMMSS.log
│   └── ...
├── recordings/              # Default recordings directory
│   └── ...
└── updates/                 # Update cache
    └── ...
```

## File Locations

### Configuration File
- **New Location**: `~/.fonixflow/config.json`
- **Old Location**: `~/.fonixflow_config.json` (migrated automatically)
- **Contains**: Settings, license key, theme preferences, etc.

### Log Files
- **Location**: `~/.fonixflow/logs/`
- **Format**: `fonixflow_YYYYMMDD_HHMMSS.log` (one file per app session)
- **Rotation**: Automatic at 10MB per session

### Recordings
- **Default Location**: `~/.fonixflow/recordings/`
- **Old Location**: `~/FonixFlow/Recordings/` (migrated automatically if empty)
- **Customizable**: Users can change this location in Settings

### Update Cache
- **Location**: `~/.fonixflow/updates/`
- **Contains**: Downloaded update files and update configuration

## Migration

The app automatically migrates old files on first run:

1. **Config File Migration**:
   - If `~/.fonixflow_config.json` exists, it's moved to `~/.fonixflow/config.json`
   - Old file is removed after successful migration

2. **Recordings Migration**:
   - If `~/FonixFlow/Recordings/` exists and contains files
   - And `~/.fonixflow/recordings/` is empty or doesn't exist
   - Files are moved to the new location
   - Old directory structure is preserved

## PathManager

All paths are managed centrally through `PathManager` class:

```python
from gui.managers.path_manager import PathManager

# Get base directory
base_dir = PathManager.get_base_dir()  # ~/.fonixflow/

# Get specific directories
config_file = PathManager.get_config_file()  # ~/.fonixflow/config.json
logs_dir = PathManager.get_logs_dir()         # ~/.fonixflow/logs/
recordings_dir = PathManager.get_recordings_dir()  # ~/.fonixflow/recordings/
updates_dir = PathManager.get_updates_dir()   # ~/.fonixflow/updates/
```

## Benefits

1. **Centralized Location**: All user data in one place
2. **Easy Backup**: Users can backup entire `~/.fonixflow/` directory
3. **Clean Home Directory**: No scattered files in home directory
4. **Cross-Platform**: Works consistently on macOS, Windows, and Linux
5. **Automatic Migration**: Old files are automatically moved

## Platform-Specific Paths

- **macOS/Linux**: `~/.fonixflow/` (e.g., `/Users/username/.fonixflow/`)
- **Windows**: `%USERPROFILE%\.fonixflow\` (e.g., `C:\Users\username\.fonixflow\`)

## Accessing Files

### Via Application
- **Settings Tab**: View and change recordings directory
- **View Logs Button**: Access logs dialog
- **Open Folder Buttons**: Open directories in file explorer

### Via File System
- Navigate to `~/.fonixflow/` in your file explorer
- All files are in standard locations

## Notes

- The `.fonixflow` directory is hidden (starts with a dot)
- On macOS/Linux, use `ls -la` or enable "Show Hidden Files" to see it
- On Windows, enable "Show Hidden Files" in File Explorer
- Migration only happens once on first run after update
- Old files are preserved if migration fails
