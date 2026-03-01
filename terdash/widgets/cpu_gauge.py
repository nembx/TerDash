"""CPU usage arc gauge widget — QPainter arc dashboard."""

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import QWidget

from terdash.services.system_service import get_cpu_percent
from terdash.theme import gauge_color, NEON_CYAN, BG_BORDER

START_ANGLE = -225
END_ANGLE = 45
SPAN = START_ANGLE - END_ANGLE  # -270 degrees


class CpuGauge(QWidget):
    """Real-time CPU usage arc gauge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._percent = 0.0
        self.setMinimumSize(130, 120)

    def start_updates(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(1000)
        self._update()

    def _update(self):
        self._percent = get_cpu_percent()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        side = min(w, h) - 20
        cx = w / 2
        cy = h / 2

        rect = QRectF(cx - side / 2, cy - side / 2, side, side)
        arc_width = 14

        # Background arc (track) — uses border color to blend with deep blue bg
        pen = QPen(QColor(BG_BORDER), arc_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, int(START_ANGLE * 16), int(SPAN * 16))

        # Foreground arc (value)
        color = QColor(gauge_color(self._percent))
        value_span = SPAN * (self._percent / 100.0)
        pen = QPen(color, arc_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, int(START_ANGLE * 16), int(value_span * 16))

        # Center text — percentage
        painter.setPen(QColor(color))
        font = QFont("Segoe UI", 24)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{self._percent:.0f}%")

        # Label below
        painter.setPen(QColor(NEON_CYAN))
        label_font = QFont("Segoe UI", 10)
        label_font.setBold(True)
        painter.setFont(label_font)
        label_rect = QRectF(cx - side / 2, cy + side * 0.25, side, 30)
        painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, "CPU")

        painter.end()
