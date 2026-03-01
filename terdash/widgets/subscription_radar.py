"""Subscription radar widget — shows recurring billing services with color-coded urgency."""

from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)

from terdash.services.subscription_service import (
    get_subscriptions, add_subscription, delete_subscription,
)
from terdash.services.exchange_rate_service import convert, get_rate
from terdash.config.settings import REFRESH_SLOW
from terdash.theme import (
    STATUS_OK, STATUS_WARN, STATUS_CRITICAL, ORANGE,
    TEXT_DIM, TEXT_PRIMARY, CYAN, BG_SURFACE, BG_BORDER,
)


_CURRENCY_SYMBOLS = {"USD": "$", "CNY": "¥", "EUR": "€", "JPY": "¥", "GBP": "£"}


def _color_for_days(days_left: int) -> str:
    if days_left <= 3:
        return STATUS_CRITICAL
    elif days_left <= 7:
        return ORANGE
    elif days_left <= 14:
        return STATUS_WARN
    else:
        return STATUS_OK


class _FetchThread(QThread):
    finished = Signal(dict)

    def run(self):
        subs = get_subscriptions()
        total_jpy = 0.0
        for s in subs:
            total_jpy += convert(s["amount"], s["currency"], "JPY")
        usd_jpy = get_rate("USD", "JPY")
        cny_jpy = get_rate("CNY", "JPY")
        self.finished.emit({
            "subscriptions": subs,
            "total_jpy": total_jpy,
            "usd_jpy": usd_jpy,
            "cny_jpy": cny_jpy,
        })


class SubscriptionRadar(QWidget):
    """Displays recurring subscriptions with color-coded urgency indicators."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: _FetchThread | None = None
        self._subs_cache: list[dict] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # ── Top bar with add button ──
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.addStretch()

        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(20, 20)
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.setToolTip("添加订阅")
        self._add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_SURFACE};
                color: {CYAN};
                border: 1px solid {BG_BORDER};
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CYAN};
                color: #0d1b2a;
            }}
        """)
        self._add_btn.clicked.connect(self._on_add_clicked)
        top_bar.addWidget(self._add_btn)
        layout.addLayout(top_bar)

        # ── Content label ──
        self._content_label = QLabel()
        self._content_label.setTextFormat(Qt.RichText)
        self._content_label.setWordWrap(False)
        self._content_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self._content_label.linkActivated.connect(self._on_link_clicked)
        self._content_label.setText(
            f'<span style="color:{TEXT_DIM};">暂无订阅，点击 + 添加</span>'
        )
        layout.addWidget(self._content_label)

    def start_updates(self):
        self._fetch_data()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fetch_data)
        self._timer.start(REFRESH_SLOW * 1000)

    def _fetch_data(self):
        if self._thread and self._thread.isRunning():
            return
        self._thread = _FetchThread()
        self._thread.finished.connect(self._on_data)
        self._thread.start()

    def _on_data(self, data: dict):
        subs = data.get("subscriptions", [])
        total_jpy = data.get("total_jpy", 0.0)
        usd_jpy = data.get("usd_jpy", 0.0)
        cny_jpy = data.get("cny_jpy", 0.0)
        self._subs_cache = subs

        if not subs:
            self._content_label.setText(
                f'<span style="color:{TEXT_DIM};">暂无订阅，点击 + 添加</span>'
            )
            return

        rows = []
        for s in subs:
            color = _color_for_days(s["days_left"])
            sym = _CURRENCY_SYMBOLS.get(s["currency"], "")
            icon = "⚡ " if s["days_left"] <= 3 else ""
            sub_id = s.get("id", "")

            rows.append(
                f'<tr>'
                # dot
                f'<td style="padding:1px 4px 1px 0;width:14px;">'
                f'  <span style="color:{color};font-size:14px;">&#x25CF;</span></td>'
                # name
                f'<td style="padding:1px 8px 1px 0;white-space:nowrap;">'
                f'  <span style="color:{TEXT_PRIMARY};">{s["name"]}</span></td>'
                # amount
                f'<td style="padding:1px 8px 1px 0;white-space:nowrap;text-align:right;">'
                f'  <span style="color:{TEXT_PRIMARY};">{sym}{s["amount"]:.2f}</span>'
                f'  <span style="color:{TEXT_DIM};font-size:11px;">{s["currency"]}</span></td>'
                # days
                f'<td style="padding:1px 6px 1px 0;white-space:nowrap;text-align:right;">'
                f'  <span style="color:{color};">{icon}{s["days_left"]}天</span></td>'
                # delete
                f'<td style="padding:1px 0;width:18px;">'
                f'  <a href="delete:{sub_id}" style="color:{TEXT_DIM};text-decoration:none;'
                f'font-size:11px;">[x]</a></td>'
                f'</tr>'
            )

        # Footer: total + rates
        footer = (
            f'<tr><td colspan="5" style="padding:6px 0 2px 0;">'
            f'<span style="color:{TEXT_DIM};">{"─" * 36}</span></td></tr>'
            f'<tr><td colspan="5" style="padding:1px 0;">'
            f'<span style="color:{TEXT_PRIMARY};">月度总计 ≈ ¥{total_jpy:,.0f} JPY</span>'
            f'</td></tr>'
            f'<tr><td colspan="5" style="padding:1px 0;">'
            f'<span style="color:{TEXT_DIM};font-size:11px;">'
            f'USD→JPY {usd_jpy:.2f}  |  CNY→JPY {cny_jpy:.2f}</span>'
            f'</td></tr>'
        )

        html = (
            '<table cellspacing="0" cellpadding="0" style="margin:0;">'
            + "".join(rows) + footer + '</table>'
        )
        self._content_label.setText(html)

    def _on_add_clicked(self):
        from terdash.widgets.subscription_dialog import SubscriptionAddDialog
        dialog = SubscriptionAddDialog(self)
        if dialog.exec() == SubscriptionAddDialog.Accepted:
            data = dialog.get_data()
            if data:
                add_subscription(**data)
                self._fetch_data()

    def _on_link_clicked(self, link: str):
        if link.startswith("delete:"):
            try:
                sub_id = int(link.split(":")[1])
            except (ValueError, IndexError):
                return
            name = next(
                (s["name"] for s in self._subs_cache if s.get("id") == sub_id), ""
            )
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "删除订阅", f'确定删除「{name}」？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                delete_subscription(sub_id)
                self._fetch_data()
