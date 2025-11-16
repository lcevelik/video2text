"""
VU Meter widget for visualizing audio levels.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient


class VUMeter(QWidget):
    """Visual audio level meter widget."""

    def __init__(self, label="Audio", parent=None):
        super().__init__(parent)
        self.label = label
        self.level = 0.0  # 0.0 to 1.0
        self.peak_level = 0.0
        self.peak_hold_time = 0

        # Minimum size for the widget
        self.setMinimumHeight(30)
        self.setMinimumWidth(200)

        # Timer for peak decay
        self.decay_timer = QTimer()
        self.decay_timer.timeout.connect(self._decay_peak)
        self.decay_timer.start(50)  # 50ms decay interval

    def set_level(self, level):
        """Set the current audio level (0.0 to 1.0)."""
        self.level = max(0.0, min(1.0, level))

        # Update peak hold
        if self.level > self.peak_level:
            self.peak_level = self.level
            self.peak_hold_time = 20  # Hold for 1 second (20 * 50ms)

        self.update()  # Trigger repaint

    def _decay_peak(self):
        """Decay the peak indicator."""
        if self.peak_hold_time > 0:
            self.peak_hold_time -= 1
        else:
            # Decay peak slowly
            if self.peak_level > self.level:
                self.peak_level = max(self.level, self.peak_level - 0.01)

        if self.peak_level != self.level:
            self.update()

    def paintEvent(self, event):
        """Paint the VU meter."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Calculate meter area (leave space for label)
        label_width = 80
        meter_x = label_width
        meter_width = width - label_width - 10
        meter_height = height - 10
        meter_y = 5

        # Draw label
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(5, 5, label_width - 10, meter_height,
                        Qt.AlignLeft | Qt.AlignVCenter, self.label)

        # Draw background
        painter.fillRect(meter_x, meter_y, meter_width, meter_height,
                        QColor(40, 40, 40))

        # Draw border
        painter.setPen(QColor(80, 80, 80))
        painter.drawRect(meter_x, meter_y, meter_width, meter_height)

        # Draw level bar with gradient
        if self.level > 0:
            level_width = int(meter_width * self.level)

            # Create gradient: green -> yellow -> red
            gradient = QLinearGradient(meter_x, 0, meter_x + meter_width, 0)
            gradient.setColorAt(0.0, QColor(0, 200, 0))      # Green
            gradient.setColorAt(0.6, QColor(200, 200, 0))    # Yellow
            gradient.setColorAt(0.85, QColor(255, 150, 0))   # Orange
            gradient.setColorAt(1.0, QColor(255, 0, 0))      # Red

            painter.fillRect(meter_x + 2, meter_y + 2, level_width - 4,
                           meter_height - 4, gradient)

        # Draw peak indicator
        if self.peak_level > 0.05:  # Only show if above threshold
            peak_x = meter_x + int(meter_width * self.peak_level)
            painter.setPen(QColor(255, 255, 255, 200))
            painter.drawLine(peak_x, meter_y, peak_x, meter_y + meter_height)

        # Draw scale marks
        painter.setPen(QColor(100, 100, 100))
        for i in range(0, 11):  # 0%, 10%, 20%, ..., 100%
            mark_x = meter_x + int(meter_width * i / 10)
            mark_height = 3 if i % 2 == 0 else 2
            painter.drawLine(mark_x, meter_y + meter_height - mark_height,
                           mark_x, meter_y + meter_height)

    def reset(self):
        """Reset the meter to zero."""
        self.level = 0.0
        self.peak_level = 0.0
        self.peak_hold_time = 0
        self.update()
