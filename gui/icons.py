"""
Feather Icons integration for FonixFlow.
Provides easy access to Feather Icons as QIcon objects with theme support.
"""

import os
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QByteArray

# Icon mapping from emoji to Feather icon names
ICON_MAP = {
    # UI Controls
    '🎚️': 'sliders',
    '🔍': 'search',
    '⚙️': 'settings',

    # Files and Folders
    '📂': 'folder-open',
    '📁': 'folder',
    '📄': 'file',
    '📝': 'file-text',
    '💾': 'save',

    # Audio and Recording
    '🎙️': 'mic',
    '🎤': 'mic',
    '🔊': 'volume-2',

    # Recording Controls
    '🔴': 'circle',
    '⏹️': 'stop-circle',

    # Status Indicators
    '✅': 'check-circle',
    '❌': 'x-circle',
    '⚠️': 'alert-triangle',
    '⬜': 'square',

    # Data and Actions
    '📥': 'download',
    '📱': 'smartphone',
    'ℹ️': 'info',

    # Special
    '🎉': 'award',
    '⏭️': 'skip-forward',
}

# Cache for loaded icons
_icon_cache = {}


def get_icon(name, color='#FFFFFF', size=29):
    """
    Get a Feather Icon as a QIcon.

    Args:
        name: Icon name (e.g., 'mic', 'settings') or emoji that maps to an icon
        color: Icon color as hex string (e.g., '#FFFFFF') or QColor. Default is white.
        size: Icon size in pixels (default: 29, which is 20% bigger than original 24)

    Returns:
        QIcon object
    """
    # Map emoji to icon name if needed
    if name in ICON_MAP:
        name = ICON_MAP[name]

    # Create cache key
    cache_key = f"{name}_{color}_{size}"
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]

    # Get icon path
    from tools.resource_locator import get_resource_path
    icons_dir = get_resource_path('assets/icons')
    icon_path = os.path.join(icons_dir, f'{name}.svg')

    if not os.path.exists(icon_path):
        # Return empty icon if not found
        return QIcon()

    # Load and render SVG with color
    with open(icon_path, 'r') as f:
        svg_data = f.read()

    # Replace stroke color in SVG
    # Feather icons use stroke for drawing
    if isinstance(color, QColor):
        color = color.name()
    svg_data = svg_data.replace('stroke="currentColor"', f'stroke="{color}"')
    svg_data = svg_data.replace('stroke="black"', f'stroke="{color}"')

    # Render SVG to pixmap
    renderer = QSvgRenderer(QByteArray(svg_data.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    icon = QIcon(pixmap)

    # Cache and return
    _icon_cache[cache_key] = icon
    return icon


def get_icon_text(icon_name, text, spacing=" "):
    """
    Get text with icon name prefix for buttons/labels.

    Args:
        icon_name: Icon name or emoji
        text: Button/label text
        spacing: Space between icon reference and text

    Returns:
        Text string (icon will be set separately via setIcon())
    """
    return text


def clear_cache():
    """Clear the icon cache."""
    global _icon_cache
    _icon_cache = {}


# Convenience functions for common icons
def mic_icon(color='#FFFFFF', size=29):
    """Get microphone icon."""
    return get_icon('mic', color, size)


def settings_icon(color='#FFFFFF', size=29):
    """Get settings icon."""
    return get_icon('settings', color, size)


def folder_icon(color='#FFFFFF', size=29):
    """Get folder icon."""
    return get_icon('folder', color, size)


def save_icon(color='#FFFFFF', size=29):
    """Get save icon."""
    return get_icon('save', color, size)


def record_icon(color='#FFFFFF', size=29):
    """Get record (circle) icon."""
    return get_icon('circle', color, size)


def stop_icon(color='#FFFFFF', size=29):
    """Get stop icon."""
    return get_icon('stop-circle', color, size)


def check_icon(color='#FFFFFF', size=29):
    """Get check icon."""
    return get_icon('check-circle', color, size)


def error_icon(color='#FFFFFF', size=29):
    """Get error (X) icon."""
    return get_icon('x-circle', color, size)


def warning_icon(color='#FFFFFF', size=29):
    """Get warning icon."""
    return get_icon('alert-triangle', color, size)


def set_button_icon(button, icon_name, color='#FFFFFF', size=29, spacing=8):
    """
    Set icon on a button with proper sizing and spacing.

    Args:
        button: QPushButton to set icon on
        icon_name: Icon name or emoji
        color: Icon color (default: white)
        size: Icon size in pixels (default: 29)
        spacing: Space between icon and text in pixels (default: 8)
    """
    from PySide6.QtCore import QSize

    button.setIcon(get_icon(icon_name, color, size))
    button.setIconSize(QSize(size, size))

    # Add spacing between icon and text
    style = button.styleSheet()
    if 'padding-left' not in style:
        # Add padding to create space after icon
        current_style = style if style else ""
        button.setStyleSheet(current_style + f" QPushButton {{ padding-left: {spacing}px; }}")
