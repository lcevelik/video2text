"""
Update management system for FonixFlow.

Handles checking for updates, downloading, verifying, and installing them.
Designed to work with PyInstaller .app bundles on macOS.
"""

import json
import requests
import hashlib
import logging
import subprocess
import shutil
import zipfile
from pathlib import Path
from typing import Dict, Optional, Callable
from packaging import version
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UpdateManager:
    """Manages update checking and installation for FonixFlow."""

    def __init__(self, app_version: str, app_name: str = "FonixFlow"):
        """
        Initialize the UpdateManager.

        Args:
            app_version: Current version string (e.g., "1.0.0")
            app_name: Application name for file references
        """
        self.app_version = version.parse(app_version)
        self.app_name = app_name

        # Configure your update server URL here
        # TODO: Replace with your actual CDN/server URL
        self.update_server = "https://cdn.fonixflow.com/updates"
        self.manifest_url = f"{self.update_server}/manifest.json"

        # Cache directory for updates
        self.cache_dir = Path.home() / ".fonixflow" / "updates"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def check_for_updates(self, timeout: int = 5) -> Dict:
        """
        Check if an update is available.

        Makes a request to the update server to fetch the latest version info.

        Returns:
            Dict with keys:
                - available (bool): Whether an update is available
                - version (str): New version if available
                - download_url (str): URL to download the update
                - release_notes (str): What's new in this version
                - force_update (bool): Whether the update is mandatory
                - file_hash (str): SHA256 hash for verification
                - error (str): Error message if check failed
        """
        try:
            logger.info(f"Checking for updates from {self.manifest_url}")

            response = requests.get(self.manifest_url, timeout=timeout)
            response.raise_for_status()
            manifest = response.json()

            latest_version = version.parse(manifest.get('latest_version', '0.0.0'))

            logger.info(f"Latest version available: {latest_version}, current: {self.app_version}")

            if latest_version > self.app_version:
                return {
                    'available': True,
                    'version': str(latest_version),
                    'download_url': manifest.get('download_url', ''),
                    'release_notes': manifest.get('release_notes', ''),
                    'force_update': manifest.get('force_update', False),
                    'file_hash': manifest.get('file_hash', ''),
                    'minimum_version': manifest.get('minimum_version'),
                }

            return {'available': False}

        except requests.RequestException as e:
            logger.error(f"Failed to check for updates: {e}")
            return {
                'available': False,
                'error': f"Update check failed: {str(e)}"
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid manifest JSON: {e}")
            return {
                'available': False,
                'error': "Invalid update manifest"
            }
        except Exception as e:
            logger.error(f"Unexpected error checking for updates: {e}")
            return {
                'available': False,
                'error': str(e)
            }

    def download_update(self, download_url: str,
                       callback: Optional[Callable[[int], None]] = None) -> Optional[str]:
        """
        Download an update package.

        Args:
            download_url: URL to download the update from
            callback: Optional callback function(progress_percent) for progress tracking

        Returns:
            Path to downloaded file, or None if download failed
        """
        try:
            logger.info(f"Downloading update from {download_url}")

            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            download_path = self.cache_dir / "FonixFlow_update.zip"

            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if callback and total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            callback(progress)

            logger.info(f"Update downloaded successfully: {download_path}")
            return str(download_path)

        except requests.RequestException as e:
            logger.error(f"Download failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during download: {e}")
            return None

    def verify_update(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify update file integrity.

        Args:
            file_path: Path to the downloaded file
            expected_hash: Expected SHA256 hash

        Returns:
            True if hash matches, False otherwise
        """
        try:
            logger.info(f"Verifying update file: {file_path}")

            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(chunk)

            computed_hash = sha256_hash.hexdigest()
            is_valid = computed_hash == expected_hash

            if is_valid:
                logger.info("Update file verification successful")
            else:
                logger.error(f"Hash mismatch. Expected: {expected_hash}, got: {computed_hash}")

            return is_valid

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

    def install_update(self, zip_path: str) -> bool:
        """
        Install the update by replacing the .app bundle.

        Args:
            zip_path: Path to the update .zip file

        Returns:
            True if installation successful, False otherwise
        """
        try:
            logger.info(f"Installing update from {zip_path}")

            # Extract to temporary location
            extract_path = self.cache_dir / "extracted"
            if extract_path.exists():
                shutil.rmtree(extract_path)
            extract_path.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            logger.info(f"Update extracted to {extract_path}")

            # Find the .app bundle in the extracted contents
            app_bundle = None
            for item in extract_path.rglob(f"{self.app_name}.app"):
                app_bundle = item
                break

            if not app_bundle or not app_bundle.exists():
                logger.error(f"Could not find {self.app_name}.app in extracted update")
                return False

            # Replace the old app bundle
            apps_folder = Path("/Applications") / f"{self.app_name}.app"

            if apps_folder.exists():
                logger.info(f"Removing old app: {apps_folder}")
                shutil.rmtree(apps_folder)

            logger.info(f"Moving new app from {app_bundle} to {apps_folder}")
            shutil.move(str(app_bundle), str(apps_folder))

            # Clean up
            shutil.rmtree(extract_path)
            Path(zip_path).unlink()

            logger.info("Update installed successfully")
            return True

        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False


class UpdateScheduler:
    """
    Manages periodic update checking.

    Prevents checking too frequently and integrates with the Qt event loop.
    """

    def __init__(self, app_version: str):
        """Initialize the scheduler."""
        self.app_version = app_version
        self.manager = UpdateManager(app_version)
        self.config_path = Path.home() / ".fonixflow" / "update_config.json"

    def should_check_for_updates(self) -> bool:
        """
        Determine if we should check for updates.

        Returns False if we checked within the last 24 hours.
        """
        config = self.load_config()
        last_check = config.get('last_check_time')

        if last_check:
            try:
                last_check_dt = datetime.fromisoformat(last_check)
                if datetime.now() - last_check_dt < timedelta(hours=24):
                    logger.debug("Update check throttled (24h minimum)")
                    return False
            except ValueError:
                pass

        return True

    def mark_check_complete(self):
        """Record that we just checked for updates."""
        config = self.load_config()
        config['last_check_time'] = datetime.now().isoformat()
        self.save_config(config)

    def load_config(self) -> Dict:
        """Load the update configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load update config: {e}")
        return {}

    def save_config(self, config: Dict):
        """Save the update configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save update config: {e}")
