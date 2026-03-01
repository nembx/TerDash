"""Network speed display widget — QLabel with upload/download speeds."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from terdash.services.network_service import NetworkSpeedTracker, format_speed
from terdash.theme import NEON_GREEN, NEON_PINK, TEXT_DIM


class NetworkSpeed(QWidget):
    """Real-time network upload/download speed display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracker = NetworkSpeedTracker()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(12)

        self._down_label = QLabel()
        self._down_label.setTextFormat(Qt.RichText)
        self._up_label = QLabel()
        self._up_label.setTextFormat(Qt.RichText)

        layout.addWidget(self._down_label)
        layout.addWidget(self._up_label)
        layout.addStretch()

        self._render_speeds(0, 0)

    def start_updates(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(1000)

    def _update(self):
        speed = self._tracker.get_speed()
        self._render_speeds(speed["down_bps"], speed["up_bps"])

    def _render_speeds(self, down_bps: float, up_bps: float):
        self._down_label.setText(
            f'<span style="color:{NEON_GREEN};font-weight:bold;">&#x25BC;</span>'
            f'<span style="color:{TEXT_DIM};"> 下载 </span>'
            f'<span style="color:{NEON_GREEN};font-weight:bold;">{format_speed(down_bps)}</span>'
        )
        self._up_label.setText(
            f'<span style="color:{NEON_PINK};font-weight:bold;">&#x25B2;</span>'
            f'<span style="color:{TEXT_DIM};"> 上传 </span>'
            f'<span style="color:{NEON_PINK};font-weight:bold;">{format_speed(up_bps)}</span>'
        )
