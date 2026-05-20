"""
Update dialog UI components for FonixFlow.

Provides user-friendly dialogs for displaying and handling updates.
"""

import logging
import sys
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from gui.theme import Theme

logger = logging.getLogger(__name__)


class UpdateWorker(QThread):
    """Background worker for downloading and installing updates."""

    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool, str)

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
            self.status.emit("Downloading update...")
            zip_path = self.manager.download_update(
                self.download_url,
                callback=lambda p: self.progress.emit(p)
            )

            if not zip_path:
                self.finished.emit(False, "Download failed")
                return

            self.status.emit("Verifying update integrity...")
            self.progress.emit(0)

            if not self.manager.verify_update(zip_path, self.file_hash):
                self.finished.emit(False, "Update verification failed (corrupted file)")
                return

            self.status.emit("Installing update...")
            result = self.manager.install_update(zip_path)
            if result:
                self.finished.emit(True, result)
            else:
                self.finished.emit(False, "Installation failed")

        except Exception as e:
            self.finished.emit(False, f"Unexpected error: {str(e)}")


class UpdateDialog(QDialog):
    """Dialog for displaying and handling app updates."""

    def __init__(self, update_info: dict, app_version: str, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.app_version = app_version
        self.worker: Optional[UpdateWorker] = None

        # Detect dark mode from parent's theme manager or fall back to palette
        self.is_dark = False
        if parent and hasattr(parent, 'theme_manager'):
            self.is_dark = parent.theme_manager.is_dark_mode
        else:
            try:
                from PySide6.QtWidgets import QApplication
                from PySide6.QtGui import QPalette
                bg = QApplication.palette().color(QPalette.ColorRole.Window)
                self.is_dark = bg.lightness() < 128
            except Exception:
                pass

        self.setWindowTitle("FonixFlow Update")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)

        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Update Available")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        version_info = QLabel(
            f"A new version is available!\n\n"
            f"Current version: {self.app_version}\n"
            f"New version: {self.update_info.get('version', 'Unknown')}"
        )
        layout.addWidget(version_info)

        notes = self.update_info.get('release_notes', '')
        if notes:
            notes_label = QLabel("What's New:")
            notes_font = QFont()
            notes_font.setBold(True)
            notes_label.setFont(notes_font)
            layout.addWidget(notes_label)

            text_edit = QTextEdit()
            text_edit.setText(notes)
            text_edit.setReadOnly(True)
            text_edit.setMaximumHeight(120)
            layout.addWidget(text_edit)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch()

        button_layout = QHBoxLayout()

        self.btn_update = QPushButton("Update Now")
        self.btn_later = QPushButton("Later")
        self.btn_update.setMinimumHeight(36)
        self.btn_later.setMinimumHeight(36)
        self.btn_update.clicked.connect(self.on_update_clicked)
        self.btn_later.clicked.connect(self.reject)

        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_later)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_update_clicked(self):
        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.progress_bar.setValue(0)

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
        self.progress_bar.setValue(percent)

    def on_status(self, message: str):
        self.status_label.setText(message)

    def on_update_finished(self, success: bool, message: str):
        if success:
            self.status_label.setText(message)
            self.progress_bar.setValue(100)
            self.btn_later.setText("Close")
            self.btn_later.setEnabled(True)
        else:
            logger.error(f"Update failed: {message}")
            self.status_label.setText(f"Update failed: {message}")
            self.btn_update.setText("Retry")
            self.btn_update.setEnabled(True)
            self.btn_later.setEnabled(True)
            self.progress_bar.setVisible(False)

    def apply_styling(self):
        d = self.is_dark
        bg = Theme.get('bg_primary', d)
        bg2 = Theme.get('bg_secondary', d)
        text = Theme.get('text_primary', d)
        border = Theme.get('border', d)
        accent = Theme.get('accent', d)
        btn_bg = Theme.get('button_bg', d)
        btn_text = Theme.get('button_text', d)
        input_bg = Theme.get('input_bg', d)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg};
            }}
            QLabel {{
                color: {text};
            }}
            QPushButton {{
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid {border};
                background-color: {btn_bg};
                color: {btn_text};
            }}
            QPushButton:hover {{
                background-color: {bg2};
                border-color: {accent};
            }}
            QPushButton:disabled {{
                opacity: 0.5;
            }}
            QTextEdit {{
                border: 1px solid {border};
                border-radius: 6px;
                padding: 8px;
                background-color: {input_bg};
                color: {text};
            }}
            QProgressBar {{
                border: 1px solid {border};
                border-radius: 6px;
                text-align: center;
                background-color: {bg2};
                color: {text};
            }}
            QProgressBar::chunk {{
                background-color: {accent};
                border-radius: 5px;
            }}
        """)

        self.btn_update.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: #ffffff;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('accent_hover', d)};
            }}
            QPushButton:disabled {{
                opacity: 0.5;
            }}
        """)
