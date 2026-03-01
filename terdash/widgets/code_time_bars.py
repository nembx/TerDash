"""Code time progress bars widget — multi-language daily breakdown using QPainter."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget

from terdash.services.code_time_service import get_code_time
from terdash.theme import NEON_CYAN, TEXT_DIM

BAR_HEIGHT = 20
ROW_HEIGHT = 28
LABEL_WIDTH = 100
HOURS_WIDTH = 50
BAR_MAX_WIDTH = 200


class CodeTimeBars(QWidget):
    """Displays coding time per language as colored progress bars."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[dict] = []
        self._load_data()

    def start_updates(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._load_data)
        self._timer.start(60_000)

    def _load_data(self):
        self._data = get_code_time()
        h = max(len(self._data) * ROW_HEIGHT + 8, 40)
        self.setMinimumHeight(h)
        self.setFixedHeight(h)
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        max_hours = max(item["hours"] for item in self._data)

        label_font = QFont("Segoe UI", 11)
        label_font.setBold(True)
        hours_font = QFont("Segoe UI", 10)

        for i, item in enumerate(self._data):
            y = i * ROW_HEIGHT + 4
            lang = item["language"]
            hours = item["hours"]
            color = QColor(item["color"])

            bar_len = int((hours / max_hours) * BAR_MAX_WIDTH) if max_hours > 0 else 0
            bar_len = max(bar_len, 4)

            # Language label
            painter.setFont(label_font)
            painter.setPen(QColor(NEON_CYAN))
            painter.drawText(4, y, LABEL_WIDTH, BAR_HEIGHT, Qt.AlignLeft | Qt.AlignVCenter, lang)

            # Progress bar
            bar_x = LABEL_WIDTH + 8
            bar_y = y + (BAR_HEIGHT - 12) // 2
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(bar_x, bar_y, bar_len, 12, 3, 3)

            # Hours text
            painter.setFont(hours_font)
            painter.setPen(QColor(TEXT_DIM))
            painter.drawText(
                bar_x + bar_len + 6, y, HOURS_WIDTH, BAR_HEIGHT,
                Qt.AlignLeft | Qt.AlignVCenter, f"{hours:.1f}h"
            )

        painter.end()
