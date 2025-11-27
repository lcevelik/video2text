"""
Path Manager for FonixFlow

Centralized path management for all user data files.
All files are stored in ~/.fonixflow/ directory structure.
"""

import os
import shutil
from pathlib import Path
from typing import Optional


class PathManager:
    """Manages all application paths in a centralized location."""
    
    _base_dir: Optional[Path] = None
    
    @classmethod
    def get_base_dir(cls) -> Path:
        """
        Get the base directory for all FonixFlow user data.
        
        Returns:
            Path to ~/.fonixflow/
        """
        if cls._base_dir is None:
            cls._base_dir = Path.home() / ".fonixflow"
            cls._base_dir.mkdir(parents=True, exist_ok=True)
        return cls._base_dir
    
    @classmethod
    def get_config_file(cls) -> Path:
        """
        Get the path to the configuration file.
        
        Returns:
            Path to ~/.fonixflow/config.json
        """
        return cls.get_base_dir() / "config.json"
    
    @classmethod
    def get_logs_dir(cls) -> Path:
        """
        Get the directory for log files.
        
        Returns:
            Path to ~/.fonixflow/logs/
        """
        logs_dir = cls.get_base_dir() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    @classmethod
    def get_recordings_dir(cls) -> Path:
        """
        Get the default directory for recordings.
        
        Returns:
            Path to ~/.fonixflow/recordings/
        """
        recordings_dir = cls.get_base_dir() / "recordings"
        recordings_dir.mkdir(parents=True, exist_ok=True)
        return recordings_dir
    
    @classmethod
    def get_updates_dir(cls) -> Path:
        """
        Get the directory for update cache.
        
        Returns:
            Path to ~/.fonixflow/updates/
        """
        updates_dir = cls.get_base_dir() / "updates"
        updates_dir.mkdir(parents=True, exist_ok=True)
        return updates_dir
    
    @classmethod
    def migrate_old_files(cls) -> None:
        """
        Migrate old files from their previous locations to the new .fonixflow structure.
        This is a one-time migration that runs on app startup.
        """
        base_dir = cls.get_base_dir()
        old_config = Path.home() / ".fonixflow_config.json"
        new_config = cls.get_config_file()
        
        # Migrate old config file
        if old_config.exists() and not new_config.exists():
            try:
                shutil.move(str(old_config), str(new_config))
                print(f"Migrated config file from {old_config} to {new_config}")
            except Exception as e:
                print(f"Warning: Could not migrate config file: {e}")
        
        # Migrate old recordings directory (if default location was used)
        old_recordings = Path.home() / "FonixFlow" / "Recordings"
        new_recordings = cls.get_recordings_dir()
        
        if old_recordings.exists() and old_recordings.is_dir():
            # Only migrate if new directory is empty or doesn't exist
            if not new_recordings.exists() or not any(new_recordings.iterdir()):
                try:
                    # Move all files from old to new location
                    for item in old_recordings.iterdir():
                        dest = new_recordings / item.name
                        if item.is_dir():
                            if dest.exists():
                                # Merge directories
                                for subitem in item.rglob('*'):
                                    rel_path = subitem.relative_to(item)
                                    dest_subitem = dest / rel_path
                                    if not dest_subitem.exists():
                                        dest_subitem.parent.mkdir(parents=True, exist_ok=True)
                                        shutil.move(str(subitem), str(dest_subitem))
                            else:
                                shutil.move(str(item), str(dest))
                        else:
                            if not dest.exists():
                                shutil.move(str(item), str(dest))
                    print(f"Migrated recordings from {old_recordings} to {new_recordings}")
                except Exception as e:
                    print(f"Warning: Could not migrate recordings directory: {e}")
