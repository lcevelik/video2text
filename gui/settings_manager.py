"""
Settings Manager Module

This module handles configuration file loading, saving, and settings management
for the Video2Text application.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manager for application settings and configuration."""

    def __init__(self, config_file: Path = None):
        """
        Initialize the settings manager.

        Args:
            config_file: Path to config file (defaults to ~/.video2text_config.json)
        """
        self.config_file = config_file or (Path.home() / ".video2text_config.json")
        self.settings = self.load_settings()

    def get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings dictionary.

        Returns:
            Dictionary with default settings
        """
        return {
            "recordings_dir": str(Path.home() / "Video2Text" / "Recordings"),
            "theme_mode": "auto"  # auto, light, dark
        }

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from config file.

        Returns:
            Settings dictionary
        """
        default_settings = self.get_default_settings()

        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    # Migrate old dark_mode setting to theme_mode
                    if "dark_mode" in settings and "theme_mode" not in settings:
                        settings["theme_mode"] = "dark" if settings["dark_mode"] else "light"
                        del settings["dark_mode"]
                    # Merge with defaults for any missing keys
                    return {**default_settings, **settings}
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")

        return default_settings

    def save_settings(self):
        """Save settings to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Settings saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Could not save settings: {e}")

    def get(self, key: str, default=None):
        """
        Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set a setting value and save.

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self.save_settings()

    def update(self, updates: Dict[str, Any]):
        """
        Update multiple settings and save.

        Args:
            updates: Dictionary of settings to update
        """
        self.settings.update(updates)
        self.save_settings()
