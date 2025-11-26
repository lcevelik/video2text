"""
Theme Manager for FonixFlow application.
Handles theme detection, application, and mode switching.
"""

import logging
from typing import Optional, List
from PySide6.QtWidgets import QApplication, QMainWindow  # type: ignore
from PySide6.QtGui import QPalette  # type: ignore

from gui.theme import Theme
from gui.widgets import Card

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application theme and styling."""

    def __init__(self, main_window: QMainWindow, theme_mode: str = "dark"):
        """
        Initialize the theme manager.

        Args:
            main_window: Reference to the main window
            theme_mode: Initial theme mode ('auto', 'light', or 'dark')
        """
        self.main_window = main_window
        self.theme_mode = theme_mode
        self.is_dark_mode = self.get_effective_theme()

    def detect_system_theme(self) -> bool:
        """
        Detect if system is in dark mode.

        Returns:
            True if dark mode, False otherwise
        """
        try:
            # Use Qt's palette to detect system theme
            palette = QApplication.palette()
            # Updated for PySide6: use QPalette.ColorRole.Window instead of deprecated attribute
            bg_color = palette.color(QPalette.ColorRole.Window)
            # If background is dark (luminance < 128), system is in dark mode
            is_dark = bg_color.lightness() < 128
            return is_dark
        except Exception as e:
            logger.warning(f"Could not detect system theme: {e}")
            return False  # Default to light

    def get_effective_theme(self) -> bool:
        """
        Get the effective theme based on mode setting.

        Returns:
            True if dark mode should be used, False otherwise
        """
        # Always return dark mode (as per original logic)
        return True

    def set_theme_mode(self, mode: str) -> None:
        """
        Set theme mode and apply it.

        Args:
            mode: Theme mode ('auto', 'light', or 'dark')
        """
        self.theme_mode = mode
        self.is_dark_mode = self.get_effective_theme()
        self.apply_theme()
        logger.info(f"Theme mode set to: {mode} (effective: {'dark' if self.is_dark_mode else 'light'})")

    def apply_theme(self) -> None:
        """Apply the current theme to all UI elements."""
        # Get theme colors
        bg = Theme.get('bg_primary', self.is_dark_mode)
        text = Theme.get('text_primary', self.is_dark_mode)
        border = Theme.get('border', self.is_dark_mode)
        accent = Theme.get('accent', self.is_dark_mode)

        # Main window stylesheet
        self.main_window.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg};
                color: {text};
            }}
            QWidget {{
                background-color: {bg};
                color: {text};
            }}
            QLabel {{
                color: {text};
            }}
            QPushButton {{
                background-color: {Theme.get('button_bg', self.is_dark_mode)};
                color: {Theme.get('button_text', self.is_dark_mode)};
                border: 2px solid {border};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {accent};
                background-color: {Theme.get('bg_secondary', self.is_dark_mode)};
            }}
            QTextEdit {{
                background-color: {Theme.get('input_bg', self.is_dark_mode)};
                color: {text};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QProgressBar {{
                border: 2px solid {border};
                border-radius: 8px;
                text-align: center;
                background-color: {Theme.get('bg_secondary', self.is_dark_mode)};
                color: {text};
            }}
            QProgressBar::chunk {{
                background-color: {accent};
                border-radius: 6px;
            }}
            QComboBox {{
                background-color: {Theme.get('input_bg', self.is_dark_mode)};
                color: {text};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 5px;
            }}
            QRadioButton {{
                color: {text};
            }}
        """)

        # Update sidebar if it exists (old)
        if hasattr(self.main_window, 'basic_sidebar'):
            self.update_sidebar_theme(self.main_window.basic_sidebar)

        # Update vertical tab bar theme
        if hasattr(self.main_window, 'tab_bar') and hasattr(self.main_window, 'tab_buttons'):
            self.update_vertical_tab_styles()

        # Update CollapsibleSidebar theme
        if hasattr(self.main_window, 'collapsible_sidebar'):
            self.main_window.collapsible_sidebar.update_theme(self.is_dark_mode)

        # Update settings section button styles
        if hasattr(self.main_window, 'settings_section_btn'):
            self.main_window.settings_section_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Theme.get('text_primary', self.is_dark_mode)};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
                }}
            """)

        # Update DropZone theme
        if hasattr(self.main_window, 'drop_zone'):
            self.main_window.drop_zone.set_theme(self.is_dark_mode)

        # Update all Card widgets
        self.update_all_cards_theme()

        logger.info(f"Applied {'dark' if self.is_dark_mode else 'light'} theme")

    def update_sidebar_theme(self, sidebar) -> None:
        """
        Update sidebar theme colors.

        Args:
            sidebar: Sidebar widget to update
        """
        sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {Theme.get('bg_secondary', self.is_dark_mode)};
                border: none;
                border-right: 1px solid {Theme.get('border', self.is_dark_mode)};
                padding: 10px;
                outline: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                color: {Theme.get('text_primary', self.is_dark_mode)};
                border-radius: 8px;
                padding: 12px 15px;
                margin: 2px 0px;
                font-size: 14px;
                font-weight: 500;
            }}
            QListWidget::item:hover {{
                background-color: {Theme.get('bg_tertiary', self.is_dark_mode)};
            }}
            QListWidget::item:selected {{
                background-color: {Theme.get('accent', self.is_dark_mode)};
                color: white;
            }}
        """)

    def update_vertical_tab_styles(self) -> None:
        """Update styling for vertical tab buttons."""
        if not hasattr(self.main_window, 'tab_buttons') or not hasattr(self.main_window, 'current_tab_index'):
            return

        for i, btn in enumerate(self.main_window.tab_buttons):
            is_active = (i == self.main_window.current_tab_index)

            # Align icon 20px from left, text 20px from icon
            # Use left padding for button, and set icon size and spacing
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'transparent' if not is_active else Theme.get('accent', self.is_dark_mode)};
                    color: {'white' if is_active else Theme.get('text_primary', self.is_dark_mode)};
                    border: {'none' if is_active else '2px solid ' + Theme.get('border', self.is_dark_mode)};
                    border-radius: 12px;
                    padding-left: 20px;
                    padding-right: 10px;
                    font-size: 13px;
                    font-weight: {'bold' if is_active else 'normal'};
                    text-align: left;
                }}
                QPushButton::icon {{
                    margin-left: 0px;
                    margin-right: 20px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.get('accent', self.is_dark_mode) if is_active else Theme.get('bg_tertiary', self.is_dark_mode)};
                    border-color: {Theme.get('accent', self.is_dark_mode)};
                }}
            """)

    def update_all_cards_theme(self) -> None:
        """Update theme for all Card widgets."""
        for widget in self.main_window.findChildren(Card):
            widget.update_theme(self.is_dark_mode)
