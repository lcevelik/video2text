"""
File Manager for FonixFlow application.
Handles file operations including browsing, loading, and folder management.
"""

import os
import logging
import platform
import subprocess
from pathlib import Path
from typing import Callable, Optional
from PySide6.QtWidgets import QFileDialog, QMessageBox, QMainWindow  # type: ignore
from PySide6.QtCore import QTimer  # type: ignore

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file operations for the application."""

    def __init__(self, main_window: QMainWindow):
        """
        Initialize the file manager.

        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window

    def browse_file(self, on_file_selected: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """
        Browse for video/audio file.

        Args:
            on_file_selected: Optional callback when file is selected

        Returns:
            Selected file path or None
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            self.main_window.tr("Select Video or Audio File"),
            "",
            self.main_window.tr("Media Files (*.mp4 *.avi *.mov *.mp3 *.wav *.m4a);;All Files (*.*)")
        )

        if file_path:
            self.load_file(file_path)
            if on_file_selected:
                QTimer.singleShot(150, lambda: on_file_selected(file_path))
            return file_path

        return None

    def load_file(self, file_path: str) -> None:
        """
        Load a video or audio file.

        Args:
            file_path: Path to the media file
        """
        self.main_window.video_path = file_path
        # Reset language mode so dialog appears for each new file
        if hasattr(self.main_window, 'multi_language_mode'):
            self.main_window.multi_language_mode = None
        filename = Path(file_path).name

        # Update UI
        if hasattr(self.main_window, 'drop_zone'):
            self.main_window.drop_zone.set_file(filename)

        self.main_window.statusBar().showMessage(f"File selected: {filename}")
        logger.info(f"Selected file: {file_path}")

    def on_file_dropped(self, file_path: str, on_file_loaded: Optional[Callable[[], None]] = None) -> None:
        """
        Handle file drop - auto-start transcription.

        Args:
            file_path: Path to the dropped file
            on_file_loaded: Optional callback after file is loaded
        """
        self.load_file(file_path)
        if on_file_loaded:
            QTimer.singleShot(150, on_file_loaded)

    def change_recordings_directory(self, settings_manager) -> None:
        """
        Open dialog to change recordings directory.

        Args:
            settings_manager: Settings manager instance
        """
        current_dir = settings_manager.get("recordings_dir", str(Path.home() / "FonixFlow" / "Recordings"))
        new_dir = QFileDialog.getExistingDirectory(
            self.main_window,
            self.main_window.tr("Select Recordings Folder"),
            current_dir,
            QFileDialog.ShowDirsOnly
        )

        if new_dir:
            settings_manager.set("recordings_dir", new_dir)

            # Update display if it exists
            if hasattr(self.main_window, 'recordings_dir_display') and self.main_window.recordings_dir_display is not None:
                try:
                    self.main_window.recordings_dir_display.setText(new_dir)
                except Exception as e:
                    logger.debug(f"Could not update recordings directory display: {e}")

            settings_manager.save_settings()
            logger.info(f"Recordings directory changed to: {new_dir}")
            QMessageBox.information(
                self.main_window,
                self.main_window.tr("Settings Updated"),
                f"Recordings will now be saved to:\n{new_dir}"
            )

    def open_recordings_folder(self, recordings_dir: str) -> None:
        """
        Open the recordings folder in the system file explorer.

        Args:
            recordings_dir: Path to recordings directory
        """
        recordings_path = Path(recordings_dir)

        # Create directory if it doesn't exist
        recordings_path.mkdir(parents=True, exist_ok=True)

        # Open in file explorer (cross-platform)
        try:
            if platform.system() == "Windows":
                os.startfile(str(recordings_path))
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(recordings_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(recordings_path)])

            logger.info(f"Opened recordings folder: {recordings_path}")
        except Exception as e:
            logger.error(f"Could not open recordings folder: {e}")
            QMessageBox.warning(
                self.main_window,
                self.main_window.tr("Could Not Open Folder"),
                f"Please navigate manually to:\n{recordings_path}"
            )
