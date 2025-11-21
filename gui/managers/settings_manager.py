"""
Settings Manager for FonixFlow application.
Handles loading, saving, and managing application settings.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages application settings and configuration."""

    def __init__(self, config_file: Path):
        """
        Initialize the settings manager.

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.default_settings = {
            "recordings_dir": str(Path.home() / "FonixFlow" / "Recordings"),
            "theme_mode": "dark",  # auto, light, dark (default: dark)
            "enable_audio_filters": True,  # Audio processing filters (default ON)
            "enable_deep_scan": False  # Deep scan for transcription (default OFF)
        }
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from config file.

        Returns:
            Dictionary containing settings
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    # Migrate old dark_mode setting to theme_mode
                    if "dark_mode" in settings and "theme_mode" not in settings:
                        settings["theme_mode"] = "dark" if settings["dark_mode"] else "light"
                        del settings["dark_mode"]
                    # Merge with defaults for any missing keys
                    return {**self.default_settings, **settings}
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")

        return self.default_settings.copy()

    def save_settings(self, **kwargs) -> bool:
        """
        Save settings to config file.

        Args:
            **kwargs: Settings to update before saving

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update settings dict with provided values
            self.settings.update(kwargs)

            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Settings saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Could not save settings: {e}")
            return False

    def get(self, key: str, default=None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value

    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.

        Returns:
            Dictionary containing all settings
        """
        return self.settings.copy()
