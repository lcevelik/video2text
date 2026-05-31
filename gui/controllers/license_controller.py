"""
License management mixin for FonixFlow main window.

Extracted from main_window.py to reduce God class size.
Handles: license validation, prompting, activation, update checks.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import QDialog, QMessageBox

from gui.dialogs import LicenseKeyDialog, LicenseLimitationsDialog
from gui.update_dialog import UpdateDialog
from app.version import __version__

logger = logging.getLogger(__name__)


class LicenseController:
    """Mixin providing license validation and update check methods."""

    def _load_encoded_licenses(self, filepath):
        """
        Decode an encoded license file.

        Args:
            filepath: Path to encoded licenses.dat file

        Returns:
            List of valid license keys
        """
        import base64

        with open(filepath, 'rb') as f:
            encoded = f.read()

        xor_bytes = base64.b64decode(encoded)

        from app.transcriber import LICENSE_XOR_KEY
        key = LICENSE_XOR_KEY
        content_bytes = bytearray()
        for i, byte in enumerate(xor_bytes):
            content_bytes.append(byte ^ key[i % len(key)])

        content = bytes(content_bytes).decode('utf-8')
        return [line.strip() for line in content.split('\n') if line.strip()]

    def check_license_key_on_startup(self):
        """Check license key validity on startup."""
        logger.info(f"check_license_key_on_startup: key={self.license_key}")
        if self.license_key:
            self.license_valid = self.validate_license_key(self.license_key)
            logger.info(f"License key checked: valid={self.license_valid}")
        else:
            self.license_valid = False
            logger.info("No license key found on startup.")
        self.update_window_title()

    def update_window_title(self):
        """Update window title to reflect license status."""
        if hasattr(self, 'license_valid') and self.license_valid:
            self.setWindowTitle(self.tr("FonixFlow - Whisper Transcription"))
        else:
            self.setWindowTitle(self.tr("FonixFlow Free - Whisper Transcription"))

    def show_license_limitations_dialog(self):
        """Show dialog explaining limitations for unlicensed users."""
        logger.info("Showing license limitations dialog")
        dialog = LicenseLimitationsDialog(self)
        dialog.exec()

    def validate_license_key(self, key):
        """Validate license key using local file first, then LemonSqueezy API.

        Local checks are synchronous (fast). API check is async if local fails.
        Returns True/False for local matches. For API, returns False immediately
        and triggers async validation (result handled via _on_api_license_result).
        """
        from pathlib import Path
        import base64

        fonixflow_dir = Path.home() / ".fonixflow"
        license_file_encoded = fonixflow_dir / "licenses.dat"
        license_file_plain = fonixflow_dir / "licenses.txt"

        if license_file_encoded.exists():
            logger.info(f"validate_license_key: checking key={key[:8]}... in {license_file_encoded} (encoded)")
            try:
                valid_keys = self._load_encoded_licenses(license_file_encoded)
                if key.strip() in valid_keys:
                    logger.info("License key valid (encoded file)")
                    return True
            except Exception as e:
                logger.error(f"Error reading encoded license file: {e}")

        if license_file_plain.exists():
            logger.info(f"validate_license_key: checking key={key[:8]}... in {license_file_plain}")
            try:
                with open(license_file_plain, "r") as f:
                    valid_keys = [line.strip() for line in f if line.strip()]
                if key.strip() in valid_keys:
                    logger.info("License key valid (plaintext file)")
                    return True
            except Exception as e:
                logger.error(f"Error reading plaintext license file: {e}")

        # Not found locally — validate async via API
        logger.info("License not found locally, starting async API validation...")
        self._start_async_license_validation(key)
        return False  # Assume invalid until API confirms

    def _start_async_license_validation(self, key):
        """Start async license validation via LemonSqueezy API in background thread."""
        from PySide6.QtCore import QThread, Signal

        class _LicenseApiWorker(QThread):
            result_ready = Signal(bool, str)  # (is_valid, key)

            def __init__(self, api_key):
                super().__init__()
                self.api_key = api_key

            def run(self):
                try:
                    import requests
                    url = "https://api.lemonsqueezy.com/v1/licenses/validate"
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    data = {"license_key": self.api_key}
                    resp = requests.post(url, headers=headers, data=data, timeout=10)
                    result = resp.json()
                    logger.info(f"License API response: {result}")
                    is_valid = result.get("status") == "active"
                    self.result_ready.emit(is_valid, self.api_key)
                except Exception as e:
                    logger.error(f"Async license validation error: {e}")
                    self.result_ready.emit(False, self.api_key)

        self._license_worker = _LicenseApiWorker(key)
        self._license_worker.result_ready.connect(self._on_api_license_result)
        self._license_worker.start()

    def _on_api_license_result(self, is_valid, key):
        """Handle async license API validation result."""
        if is_valid:
            logger.info(f"License key validated via API: {key[:8]}...")
            self.license_key = key
            self.license_valid = True
            self.settings_manager.save_settings(license_key=key)
            self.update_window_title()
        else:
            logger.info(f"License key invalid via API: {key[:8]}...")

    def prompt_for_license_key(self, force=False):
        """Prompt user for license key and validate.

        Args:
            force: If True, allow prompting even during transcription (default: False)
        """
        import traceback

        if not force and hasattr(self, 'transcription_worker') and self.transcription_worker and self.transcription_worker.isRunning():
            logger.warning("License dialog blocked: Transcription is in progress")
            return False

        logger.info("Prompting for license key dialog...")
        try:
            stack = traceback.extract_stack()
            logger.info("=== CALL STACK ===")
            for frame in stack[-8:-1]:
                logger.info(f"  File: {frame.filename}, Line: {frame.lineno}, Function: {frame.name}, Code: {frame.line}")
            logger.info("==================")
        except Exception as e:
            logger.error(f"Error getting call stack: {e}")

        dlg = LicenseKeyDialog(self, current_key=self.license_key)
        result = dlg.exec()
        logger.info(f"License dialog result: {result}, valid={dlg.valid}, key={dlg.license_key}")
        if result == QDialog.Accepted and dlg.valid:
            self.license_key = dlg.license_key
            self.license_valid = True
            self.settings_manager.save_settings(license_key=self.license_key)
            logger.info("License key accepted and saved.")
            self.update_window_title()
            return True
        else:
            if self.license_valid and self.license_key:
                logger.info(f"License dialog cancelled - preserving existing valid license (key: {self.license_key})")
            else:
                logger.info("License dialog cancelled or key not validated - no existing license to preserve.")
            return False

    def show_activation_dialog(self):
        """Show activation dialog for entering license key."""
        logger.info("Activate button clicked - showing activation dialog")
        result = self.prompt_for_license_key(force=True)
        if result:
            self.check_license_key_on_startup()
            QMessageBox.information(
                self,
                self.tr("Activation Successful"),
                self.tr("Your license key has been activated successfully! More features are now available.")
            )
        return result

    def is_license_active(self):
        """Check if license is currently active and valid."""
        return self.license_valid and self.license_key is not None

    def show_logs_dialog(self):
        """Show the logs dialog."""
        logger.info("Opening logs dialog")
        from gui.dialogs import LogsDialog
        dialog = LogsDialog(self)
        dialog.exec()

    def check_for_updates(self):
        """Check for app updates asynchronously."""
        if not self.update_scheduler.should_check_for_updates():
            logger.debug("Skipping update check (checked recently)")
            return

        from PySide6.QtCore import QThread, Signal

        class _UpdateCheckWorker(QThread):
            result_ready = Signal(dict)

            def __init__(self, scheduler):
                super().__init__()
                self.scheduler = scheduler

            def run(self):
                try:
                    result = self.scheduler.manager.check_for_updates()
                    self.scheduler.mark_check_complete()
                    self.result_ready.emit(result)
                except Exception as e:
                    logger.warning(f"Async update check failed: {e}")
                    self.result_ready.emit({})

        self._update_worker = _UpdateCheckWorker(self.update_scheduler)
        self._update_worker.result_ready.connect(self._on_update_check_result)
        self._update_worker.start()

    def _on_update_check_result(self, result):
        """Handle async update check result."""
        if result.get('available'):
            logger.info(f"Update available: {result.get('version')}")
            dialog = UpdateDialog(result, __version__, self)
            dialog.exec()
        else:
            logger.info("No updates available")
