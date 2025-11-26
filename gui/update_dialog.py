"""
Update dialog UI components for FonixFlow.

Provides user-friendly dialogs for displaying and handling updates.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)


class UpdateWorker(QThread):
    """
    Background worker for downloading and installing updates.

    Emits signals for progress and completion.
    """

    progress = Signal(int)  # Download progress 0-100
    status = Signal(str)    # Status message
    finished = Signal(bool, str)  # (success, message)

    def __init__(self, download_url: str, file_hash: str, app_version: str):
        super().__init__()
        self.download_url = download_url
        self.file_hash = file_hash
        self.app_version = app_version

        from gui.update_manager import UpdateManager
        self.manager = UpdateManager(app_version)

    def run(self):
        """Execute the update process."""
        try:
            # Download
            self.status.emit("Downloading update...")
            zip_path = self.manager.download_update(
                self.download_url,
                callback=lambda p: self.progress.emit(p)
            )

            if not zip_path:
                self.finished.emit(False, "Download failed")
                return

            # Verify
            self.status.emit("Verifying update integrity...")
            self.progress.emit(0)  # Reset progress

            if not self.manager.verify_update(zip_path, self.file_hash):
                self.finished.emit(False, "Update verification failed (corrupted file)")
                return

            # Install
            self.status.emit("Installing update (the app will restart)...")
            if self.manager.install_update(zip_path):
                self.finished.emit(True, "Update installed successfully")
            else:
                self.finished.emit(False, "Installation failed")

        except Exception as e:
            self.finished.emit(False, f"Unexpected error: {str(e)}")


class UpdateDialog(QDialog):
    """
    Dialog for displaying and handling app updates.

    Shows update information, progress, and handles the installation flow.
    """

    def __init__(self, update_info: dict, app_version: str, parent=None):
        """
        Initialize the update dialog.

        Args:
            update_info: Dict with update details (from UpdateManager.check_for_updates)
            app_version: Current app version
            parent: Parent widget
        """
        super().__init__(parent)
        self.update_info = update_info
        self.app_version = app_version
        self.worker: Optional[UpdateWorker] = None

        self.setWindowTitle("FonixFlow Update")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Build the UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Update Available")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Version info
        version_info = QLabel(
            f"A new version is available!\n\n"
            f"Current version: {self.app_version}\n"
            f"New version: {self.update_info.get('version', 'Unknown')}"
        )
        layout.addWidget(version_info)

        # Release notes
        notes = self.update_info.get('release_notes', 'No release notes available')
        if notes:
            notes_label = QLabel("What's New:")
            notes_font = QFont()
            notes_font.setBold(True)
            notes_label.setFont(notes_font)
            layout.addWidget(notes_label)

            # Create scrollable text area for release notes
            text_edit = QTextEdit()
            text_edit.setText(notes)
            text_edit.setReadOnly(True)
            text_edit.setMaximumHeight(120)
            layout.addWidget(text_edit)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0FD2CC;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Status label (for download/install messages)
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Spacer
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        self.btn_update = QPushButton("Update Now")
        self.btn_later = QPushButton("Update Later")

        # Style buttons
        self.btn_update.setMinimumHeight(36)
        self.btn_later.setMinimumHeight(36)

        self.btn_update.clicked.connect(self.on_update_clicked)
        self.btn_later.clicked.connect(self.reject)

        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_later)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_update_clicked(self):
        """Handle update button click."""
        # Hide buttons and show progress
        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.progress_bar.setValue(0)

        # Start download/install
        self.worker = UpdateWorker(
            self.update_info['download_url'],
            self.update_info['file_hash'],
            self.app_version
        )

        self.worker.progress.connect(self.on_progress)
        self.worker.status.connect(self.on_status)
        self.worker.finished.connect(self.on_update_finished)
        self.worker.start()

    def on_progress(self, percent: int):
        """Update progress bar."""
        self.progress_bar.setValue(percent)

    def on_status(self, message: str):
        """Update status message."""
        self.status_label.setText(message)

    def on_update_finished(self, success: bool, message: str):
        """Handle update completion."""
        if success:
            logger.info("Update installed successfully")

            # Show success message
            self.status_label.setText(
                "Update installed successfully!\n"
                "The application will restart now..."
            )
            self.progress_bar.setValue(100)

            # Restart the app after 2 seconds
            from PySide6.QtCore import QTimer
            QTimer.singleShot(2000, self.restart_app)
        else:
            logger.error(f"Update failed: {message}")

            # Show error and allow retry
            self.status_label.setText(f"Update failed: {message}")
            self.btn_update.setText("Retry")
            self.btn_update.setEnabled(True)
            self.btn_later.setEnabled(True)
            self.progress_bar.setVisible(False)

    def restart_app(self):
        """Restart the application."""
        import subprocess
        import sys

        try:
            # Launch the updated app from Applications
            subprocess.Popen(['/Applications/FonixFlow.app/Contents/MacOS/FonixFlow'])
            # Exit current instance
            from PySide6.QtWidgets import QApplication
            QApplication.quit()
        except Exception as e:
            logger.error(f"Failed to restart app: {e}")
            self.status_label.setText(
                "Please manually restart FonixFlow from /Applications"
            )

    def apply_styling(self):
        """Apply visual styling."""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
                background-color: #f3f4f6;
                color: #1f2937;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
            QLabel {
                color: #1f2937;
            }
            QTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                padding: 8px;
                background-color: #f9fafb;
            }
        """)

        # Style the update button as primary
        self.btn_update.setStyleSheet("""
            QPushButton {
                background-color: #0FD2CC;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #0CBFB3;
            }
            QPushButton:pressed {
                background-color: #0AA99E;
            }
            QPushButton:disabled {
                background-color: #93c5fd;
                color: #dbeafe;
            }
        """)
