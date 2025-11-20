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
                    background-color: #0FD2CC;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0CBFB3;
                }
                QPushButton:pressed {
                    background-color: #0AA99E;
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
                    border-color: #0FD2CC;
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


class VUMeter(QFrame):
    """Audio level meter widget."""

    def __init__(self, label="Audio", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.level = 0.0
        self.smoothed_level = 0.0  # For smoothing
        self.smoothing_factor = 0.3  # Lower = smoother but slower response
        self.setMinimumWidth(200)
        self.setMinimumHeight(50)
        self.setMaximumHeight(80)
        self.setup_ui()

    def setup_ui(self):
        from PySide6.QtWidgets import QProgressBar, QHBoxLayout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # Label
        self.label = QLabel(self.label_text)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(self.label)

        # Horizontal layout for progress bar and level label
        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)

        # Progress bar (horizontal)
        self.progress = QProgressBar()
        self.progress.setOrientation(Qt.Horizontal)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setMinimumHeight(20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A5C74C, stop:1.0 #0FD2CC);
                border-radius: 3px;
            }
        """)
        h_layout.addWidget(self.progress, 1)

        # Level label - HIDDEN (user requested removal of percentile)
        self.level_label = QLabel("0%")
        self.level_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.level_label.setStyleSheet("font-size: 11px; font-weight: bold; min-width: 40px;")
        self.level_label.hide()  # Hide the percentage label
        # h_layout.addWidget(self.level_label)  # Don't add to layout

        layout.addLayout(h_layout)
        self.setLayout(layout)

    def set_level(self, level: float):
        """Set audio level (0.0 to 1.0) with smoothing."""
        self.level = max(0.0, min(1.0, level))
        # Apply exponential smoothing for smoother transitions
        self.smoothed_level = (self.smoothing_factor * self.level +
                              (1 - self.smoothing_factor) * self.smoothed_level)
        percent = int(self.smoothed_level * 100)
        self.progress.setValue(percent)
        self.level_label.setText(f"{percent}%")


class ModernTabBar(QFrame):
    """Modern horizontal tab bar with pill-style tabs."""

    tab_changed = Signal(int)

    def __init__(self, tabs, is_dark_mode=False):
        """
        Initialize tab bar.

        Args:
            tabs: List of tuples (icon, label, index) e.g. [("🎙️", "Record", 0), ...]
            is_dark_mode: Whether to use dark mode styling
        """
        super().__init__()
        from PySide6.QtWidgets import QHBoxLayout, QPushButton

        self.tabs = tabs
        self.is_dark_mode = is_dark_mode
        self.current_index = 0
        self.tab_buttons = []

        self.setFrameShape(QFrame.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(8)

        # Create tab buttons
        for icon, label, index in tabs:
            btn = QPushButton(f"{icon} {label}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.setProperty("tab_index", index)
            btn.clicked.connect(lambda checked=False, idx=index: self.switch_to_tab(idx))
            self.tab_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        self.update_theme(is_dark_mode)
        self.update_tab_styles()

    def update_theme(self, is_dark_mode):
        """Update theme colors."""
        self.is_dark_mode = is_dark_mode
        bg = Theme.get('bg_primary', is_dark_mode)

        self.setStyleSheet(f"""
            ModernTabBar {{
                background-color: {bg};
                border-bottom: 1px solid {Theme.get('border', is_dark_mode)};
            }}
        """)
        self.update_tab_styles()

    def update_tab_styles(self):
        """Update styling for all tab buttons."""
        for i, btn in enumerate(self.tab_buttons):
            is_active = (i == self.current_index)

            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Theme.get('accent', self.is_dark_mode)};
                        color: white;
                        border: none;
                        border-radius: 20px;
                        padding: 10px 20px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.get('accent', self.is_dark_mode)};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {Theme.get('text_primary', self.is_dark_mode)};
                        border: 2px solid {Theme.get('border', self.is_dark_mode)};
                        border-radius: 20px;
                        padding: 10px 20px;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                        border-color: {Theme.get('accent', self.is_dark_mode)};
                    }}
                """)

    def switch_to_tab(self, index):
        """Switch to the specified tab."""
        if index != self.current_index:
            self.current_index = index
            self.update_tab_styles()
            self.tab_changed.emit(index)

    def set_current_index(self, index):
        """Programmatically set the current tab."""
        self.switch_to_tab(index)


class CollapsibleSidebar(QFrame):
    """Collapsible sidebar with icons and optional labels."""

    def __init__(self, is_dark_mode=False, side='left'):
        super().__init__()
        from PySide6.QtWidgets import QHBoxLayout, QPushButton, QScrollArea, QWidget as QWid

        self.is_dark_mode = is_dark_mode
        self.is_collapsed = False
        self.collapsed_width = 60
        self.expanded_width = 200
        self.side = side  # 'left' or 'right'

        self.setFrameShape(QFrame.NoFrame)
        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toggle button at top - arrow direction depends on side
        initial_arrow = "▶" if side == 'right' else "◀"
        self.toggle_btn = QPushButton(initial_arrow)
        self.toggle_btn.setMinimumHeight(40)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        main_layout.addWidget(self.toggle_btn)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content_widget = QWid()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        self.content_layout.addStretch()

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll, 1)

        self.update_theme(is_dark_mode)

    def update_theme(self, is_dark_mode):
        """Update theme colors."""
        self.is_dark_mode = is_dark_mode

        self.setStyleSheet(f"""
            CollapsibleSidebar {{
                background-color: {Theme.get('bg_secondary', is_dark_mode)};
                border-right: 1px solid {Theme.get('border', is_dark_mode)};
            }}
        """)

        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.get('text_primary', is_dark_mode)};
                border: none;
                border-bottom: 1px solid {Theme.get('border', is_dark_mode)};
                font-size: 16px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', is_dark_mode)};
            }}
        """)

    def toggle_collapse(self):
        """Toggle sidebar collapsed state with smooth animation."""
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve

        self.is_collapsed = not self.is_collapsed

        # Create animation for width
        self.anim = QPropertyAnimation(self, b"maximumWidth")
        self.anim.setDuration(250)  # 250ms animation
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        if self.is_collapsed:
            # Set minimum width BEFORE animation to avoid jump
            self.setMinimumWidth(self.collapsed_width)
            self.anim.setStartValue(self.expanded_width)
            self.anim.setEndValue(self.collapsed_width)
            # Arrow direction depends on side: left sidebar shows ▶, right sidebar shows ◀
            self.toggle_btn.setText("◀" if self.side == 'right' else "▶")
            # Hide content widget
            self.content_widget.hide()
        else:
            # Set minimum width BEFORE animation to avoid jump
            self.setMinimumWidth(self.expanded_width)
            self.anim.setStartValue(self.collapsed_width)
            self.anim.setEndValue(self.expanded_width)
            # Arrow direction depends on side: left sidebar shows ◀, right sidebar shows ▶
            self.toggle_btn.setText("▶" if self.side == 'right' else "◀")
            # Show content widget
            self.content_widget.show()

        self.anim.start()

    def add_action(self, icon, text, callback):
        """Add an action button to the sidebar."""
        from PySide6.QtWidgets import QPushButton

        btn = QPushButton(f"{icon} {text}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(36)
        btn.clicked.connect(callback)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.get('text_primary', self.is_dark_mode)};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                text-align: left;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
        """)

        # Insert before the stretch
        self.content_layout.insertWidget(self.content_layout.count() - 1, btn)
        return btn

    def add_separator(self):
        """Add a separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {Theme.get('border', self.is_dark_mode)};")
        separator.setMaximumHeight(1)
        self.content_layout.insertWidget(self.content_layout.count() - 1, separator)

