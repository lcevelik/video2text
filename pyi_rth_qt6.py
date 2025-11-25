"""
Runtime hook for PySide6/Qt6 to set plugin path correctly.
This ensures Qt can find its platform plugins in the bundled application.
"""
import os
import sys

# Set Qt plugin path to the bundled plugins directory
if hasattr(sys, '_MEIPASS'):
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    qt_plugin_path = os.path.join(sys._MEIPASS, 'PySide6', 'Qt', 'plugins')
    if os.path.exists(qt_plugin_path):
        os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
    # Also try the alternative location
    alt_plugin_path = os.path.join(sys._MEIPASS, 'PySide6', 'plugins')
    if os.path.exists(alt_plugin_path):
        if 'QT_PLUGIN_PATH' in os.environ:
            os.environ['QT_PLUGIN_PATH'] = os.pathsep.join([os.environ['QT_PLUGIN_PATH'], alt_plugin_path])
        else:
            os.environ['QT_PLUGIN_PATH'] = alt_plugin_path

