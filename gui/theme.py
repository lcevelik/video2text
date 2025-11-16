"""
Theme management for the GUI.
"""


class Theme:
    """Theme colors for light and dark modes."""

    LIGHT = {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F5F5F5',
        'bg_tertiary': '#FAFAFA',
        'text_primary': '#333333',
        'text_secondary': '#555555',
        'text_disabled': '#999999',
        'border': '#E0E0E0',
        'accent': '#2196F3',
        'accent_hover': '#1976D2',
        'success': '#4CAF50',
        'success_hover': '#45a049',
        'error': '#F44336',
        'warning': '#FF9800',
        'info': '#2196F3',
        'card_bg': '#FFFFFF',
        'card_border': '#E0E0E0',
        'input_bg': '#FAFAFA',
        'button_bg': '#FFFFFF',
        'button_text': '#333333',
        'dropzone_bg': '#FAFAFA',
        'dropzone_border': '#E0E0E0',
        'dropzone_hover_bg': '#E3F2FD',
        'dropzone_hover_border': '#2196F3',
        'selected_bg': '#E8F5E9',
        'selected_border': '#4CAF50',
        'selected_text': '#2E7D32',
    }

    DARK = {
        'bg_primary': '#1E1E1E',
        'bg_secondary': '#252525',
        'bg_tertiary': '#2D2D2D',
        'text_primary': '#E0E0E0',
        'text_secondary': '#B0B0B0',
        'text_disabled': '#666666',
        'border': '#404040',
        'accent': '#42A5F5',
        'accent_hover': '#64B5F6',
        'success': '#66BB6A',
        'success_hover': '#81C784',
        'error': '#EF5350',
        'warning': '#FFA726',
        'info': '#42A5F5',
        'card_bg': '#252525',
        'card_border': '#404040',
        'input_bg': '#2D2D2D',
        'button_bg': '#303030',
        'button_text': '#E0E0E0',
        'dropzone_bg': '#2D2D2D',
        'dropzone_border': '#404040',
        'dropzone_hover_bg': '#1E3A5F',
        'dropzone_hover_border': '#42A5F5',
        'selected_bg': '#1B3A2F',
        'selected_border': '#66BB6A',
        'selected_text': '#81C784',
    }

    @staticmethod
    def get(key, is_dark=False):
        """Get theme color by key."""
        theme = Theme.DARK if is_dark else Theme.LIGHT
        return theme.get(key, '#000000')

