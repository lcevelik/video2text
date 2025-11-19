"""
Theme management for the GUI.
"""


class Theme:
    """Theme colors for light and dark modes."""

    LIGHT = {
        'bg_primary': '#C0C0C0',      # 50% reduced brightness from white
        'bg_secondary': '#B0B0B0',    # Darker gray
        'bg_tertiary': '#C8C8C8',     # Slightly lighter for hover
        'text_primary': '#000000',    # Pure black for best contrast
        'text_secondary': '#303030',
        'text_disabled': '#707070',
        'border': '#A0A0A0',          # Darker border
        'accent': '#2196F3',
        'accent_hover': '#1976D2',
        'success': '#4CAF50',
        'success_hover': '#45a049',
        'error': '#F44336',
        'warning': '#FF9800',
        'info': '#2196F3',
        'card_bg': '#C0C0C0',         # 50% reduced brightness
        'card_border': '#A0A0A0',     # Darker border
        'input_bg': '#C8C8C8',        # Slightly lighter for inputs
        'button_bg': '#C8C8C8',       # Slightly lighter for buttons
        'button_text': '#000000',
        'dropzone_bg': '#C8C8C8',     # Slightly lighter
        'dropzone_border': '#A0A0A0',
        'dropzone_hover_bg': '#B3D9F2',  # Adjusted hover color
        'dropzone_hover_border': '#2196F3',
        'selected_bg': '#B8E6BD',     # Adjusted selection color
        'selected_border': '#4CAF50',
        'selected_text': '#1B5E20',   # Darker green for contrast
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

