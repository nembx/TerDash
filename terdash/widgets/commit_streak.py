"""Commit streak and yearly total widget — QLabel rich text."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from terdash.theme import NEON_GREEN, NEON_CYAN, NEON_YELLOW, TEXT_DIM


class CommitStreak(QLabel):
    """Displays current commit streak and yearly contribution total."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setTextFormat(Qt.RichText)
        self._refresh_display(0, 0)

    def update_data(self, streak: int, yearly: int):
        self._refresh_display(streak, yearly)

    def _refresh_display(self, streak: int, yearly: int):
        html = (
            f'<span style="color:{NEON_CYAN}; font-weight:bold;">连续提交: </span>'
            f'<span style="color:{NEON_GREEN}; font-weight:bold; font-size:16px;">{streak}</span>'
            f'<span style="color:{TEXT_DIM};"> 天</span>'
            f'<span style="color:{TEXT_DIM};">  |  </span>'
            f'<span style="color:{NEON_CYAN}; font-weight:bold;">年度: </span>'
            f'<span style="color:{NEON_YELLOW}; font-weight:bold; font-size:16px;">{yearly}</span>'
            f'<span style="color:{TEXT_DIM};"> 次提交</span>'
        )
        self.setText(html)
