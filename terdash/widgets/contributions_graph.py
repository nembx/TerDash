"""GitHub contributions heatmap widget — 7x52 colored block grid using QPainter."""

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget

from terdash.services.github_service import fetch_contributions_sync
from terdash.theme import CONTRIB_LEVELS

BLOCK_SIZE = 12
BLOCK_GAP = 3
ROWS = 7
COLS = 52


def _level(count: int) -> int:
    """Map contribution count to 0-4 intensity level."""
    if count == 0:
        return 0
    elif count <= 3:
        return 1
    elif count <= 6:
        return 2
    elif count <= 9:
        return 3
    else:
        return 4


class _FetchThread(QThread):
    finished = Signal(dict)

    def run(self):
        data = fetch_contributions_sync()
        self.finished.emit(data)


class ContributionsGraph(QWidget):
    """Renders a GitHub-style contribution heatmap using QPainter."""

    data_fetched = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid: list[list[int]] = []
        self._thread: _FetchThread | None = None
        w = COLS * (BLOCK_SIZE + BLOCK_GAP) + BLOCK_GAP
        h = ROWS * (BLOCK_SIZE + BLOCK_GAP) + BLOCK_GAP
        self.setMinimumSize(w, h)
        self.setFixedHeight(h)

    def start_updates(self):
        self._fetch_data()
        from PySide6.QtCore import QTimer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fetch_data)
        self._timer.start(300_000)

    def _fetch_data(self):
        if self._thread and self._thread.isRunning():
            return
        self._thread = _FetchThread()
        self._thread.finished.connect(self._on_data)
        self._thread.start()

    def _on_data(self, data: dict):
        self._grid = data.get("grid", [])
        self.data_fetched.emit(data)
        self.update()

    def paintEvent(self, event):
        if not self._grid:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for row in range(ROWS):
            if row >= len(self._grid):
                break
            for col in range(COLS):
                if col >= len(self._grid[row]):
                    break
                count = self._grid[row][col]
                level = _level(count)
                color = QColor(CONTRIB_LEVELS[level])

                x = BLOCK_GAP + col * (BLOCK_SIZE + BLOCK_GAP)
                y = BLOCK_GAP + row * (BLOCK_SIZE + BLOCK_GAP)

                painter.setBrush(color)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(x, y, BLOCK_SIZE, BLOCK_SIZE, 2, 2)

        painter.end()
