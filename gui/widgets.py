"""
Custom GUI widgets.
"""

from PySide6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from gui.theme import Theme


class ModernButton(QPushButton):
    """Modern styled button with hover effects."""

    def __init__(self, text, primary=False):
        super().__init__(text)
        self.primary = primary
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()

    def apply_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #333;
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    border-color: #2196F3;
                    background-color: #F5F5F5;
                }
                QPushButton:pressed {
                    background-color: #EEEEEE;
                }
                QPushButton:disabled {
                    background-color: #F5F5F5;
                    color: #BDBDBD;
                }
            """)


class Card(QFrame):
    """Modern card widget with shadow effect."""

    def __init__(self, title="", is_dark_mode=False):
        super().__init__()
        self.is_dark_mode = is_dark_mode
        self.title = title
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        if title:
            self.title_label = QLabel(title)
            layout.addWidget(self.title_label)
        else:
            self.title_label = None

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        self.setLayout(layout)
        self.update_theme(is_dark_mode)

    def update_theme(self, is_dark_mode):
        """Update card theme."""
        self.is_dark_mode = is_dark_mode
        self.setStyleSheet(f"""
            Card {{
                background-color: {Theme.get('card_bg', is_dark_mode)};
                border-radius: 12px;
                border: 1px solid {Theme.get('card_border', is_dark_mode)};
            }}
        """)

        if self.title_label:
            self.title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Theme.get('text_primary', is_dark_mode)};")


class DropZone(QFrame):
    """Drag and drop zone for files."""

    file_dropped = Signal(str)
    clicked = Signal()  # Signal emitted when user clicks the drop zone

    def __init__(self, is_dark_mode=False):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)
        self.has_file = False
        self.is_dark_mode = is_dark_mode
        self.setCursor(Qt.PointingHandCursor)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # Just text label, no icon
        self.text_label = QLabel("Drag and drop video/audio file")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet(f"font-size: 14px; color: {Theme.get('text_secondary', self.is_dark_mode)};")

        self.layout.addWidget(self.text_label)

        self.setLayout(self.layout)
        self.update_style()

    def set_theme(self, is_dark_mode):
        """Update theme colors."""
        self.is_dark_mode = is_dark_mode
        self.update_style()
        if not self.has_file:
            self.text_label.setStyleSheet(f"font-size: 14px; color: {Theme.get('text_secondary', self.is_dark_mode)};")

    def update_style(self, hovering=False):
        # Background always matches main background (no separate color)
        bg = Theme.get('bg_primary', self.is_dark_mode)

        if self.has_file:
            color = Theme.get('accent', self.is_dark_mode)
        elif hovering:
            color = Theme.get('accent', self.is_dark_mode)
        else:
            color = Theme.get('border', self.is_dark_mode)

        self.setStyleSheet(f"""
            DropZone {{
                background-color: {bg};
                border: 2px dashed {color};
                border-radius: 8px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.update_style(hovering=True)

    def dragLeaveEvent(self, event):
        self.update_style(hovering=False)

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.file_dropped.emit(files[0])
        self.update_style(hovering=False)

    def set_file(self, filename):
        self.has_file = True
        self.text_label.setText(f"✓ {filename}")
        self.text_label.setStyleSheet(f"font-size: 14px; color: {Theme.get('accent', self.is_dark_mode)}; font-weight: 600;")
        self.update_style()

    def clear_file(self):
        self.has_file = False
        self.text_label.setText("Drag and drop video/audio file")
        self.text_label.setStyleSheet(f"font-size: 14px; color: {Theme.get('text_secondary', self.is_dark_mode)};")
        self.update_style()

    def mousePressEvent(self, event):
        """Handle mouse click - emit signal instead of navigating parent chain."""
        self.clicked.emit()

