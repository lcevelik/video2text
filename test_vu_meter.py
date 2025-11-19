#!/usr/bin/env python3
"""
Simple test for VU meter widget.
This creates a window with two VU meters and simulates audio levels.
"""

import sys
import math
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
from gui.vu_meter import VUMeter


class VUMeterTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VU Meter Test")
        self.setGeometry(100, 100, 600, 300)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Create VU meters
        self.mic_meter = VUMeter("🎤 Microphone")
        self.speaker_meter = VUMeter("🔊 Speaker")

        layout.addWidget(self.mic_meter)
        layout.addWidget(self.speaker_meter)

        # Timer to simulate audio levels
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_levels)
        self.timer.start(50)  # Update every 50ms

        self.counter = 0

    def update_levels(self):
        """Simulate varying audio levels."""
        self.counter += 1

        # Simulate mic level - sine wave pattern
        mic_level = abs(math.sin(self.counter * 0.1)) * 0.8

        # Simulate speaker level - different frequency
        speaker_level = abs(math.sin(self.counter * 0.05)) * 0.6 + abs(math.sin(self.counter * 0.3)) * 0.3

        self.mic_meter.set_level(mic_level)
        self.speaker_meter.set_level(speaker_level)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VUMeterTestWindow()
    window.show()
    sys.exit(app.exec())
