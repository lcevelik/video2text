"""
Controllers for FonixFlow main window.

These are mixin classes that provide logical groupings of methods
to reduce the size of the main window class.
"""

from gui.controllers.license_controller import LicenseController
from gui.controllers.recording_controller import RecordingController
from gui.controllers.transcription_controller import TranscriptionController

__all__ = ['LicenseController', 'RecordingController', 'TranscriptionController']
