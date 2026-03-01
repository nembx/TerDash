"""Service health status widget — shows service ports and runtime environments."""

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from terdash.services.port_checker import check_port, get_runtime_version
from terdash.config.settings import MONITORED_SERVICES, MONITORED_RUNTIMES
from terdash.theme import STATUS_OK, STATUS_DOWN, TEXT_DIM, TEXT_PRIMARY, CYAN


class _CheckThread(QThread):
    """Background thread that checks all services and runtimes."""

    finished = Signal(dict)

    def run(self):
        services = []
        for name, host, port in MONITORED_SERVICES:
            alive = check_port(host, port)
            services.append({"name": name, "port": port, "alive": alive})

        runtimes = []
        for name, cmd in MONITORED_RUNTIMES:
            version = get_runtime_version(cmd)
            runtimes.append({"name": name, "version": version})

        self.finished.emit({"services": services, "runtimes": runtimes})


class ServiceHealth(QWidget):
    """Monitors local services and runtime environments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: _CheckThread | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._content = QLabel()
        self._content.setTextFormat(Qt.RichText)
        self._content.setWordWrap(False)
        self._content.setText(
            f'<span style="color:{TEXT_DIM};">检测中...</span>'
        )
        layout.addWidget(self._content)

    def start_updates(self):
        self._fetch()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fetch)
        self._timer.start(10_000)

    def _fetch(self):
        if self._thread and self._thread.isRunning():
            return
        self._thread = _CheckThread()
        self._thread.finished.connect(self._on_data)
        self._thread.start()

    def _on_data(self, data: dict):
        rows = []

        # ── Services ──
        rows.append(self._section_header("服务"))
        for s in data["services"]:
            color = STATUS_OK if s["alive"] else STATUS_DOWN
            status = "运行中" if s["alive"] else "已停止"
            rows.append(self._row(
                color=color,
                name=s["name"],
                detail=f':{s["port"]}',
                badge=status,
                badge_color=color,
            ))

        # ── Runtimes ──
        rows.append(self._section_header("运行环境"))
        for r in data["runtimes"]:
            if r["version"]:
                color = STATUS_OK
                detail = f'v{r["version"]}'
                badge = "可用"
            else:
                color = STATUS_DOWN
                detail = "—"
                badge = "未安装"
            rows.append(self._row(
                color=color,
                name=r["name"],
                detail=detail,
                badge=badge,
                badge_color=color,
            ))

        table = (
            '<table cellspacing="0" cellpadding="2" style="margin:0;">'
            + "".join(rows)
            + '</table>'
        )
        self._content.setText(table)

    @staticmethod
    def _section_header(title: str) -> str:
        return (
            f'<tr><td colspan="4" style="padding:4px 0 2px 0;">'
            f'<span style="color:{TEXT_DIM};font-size:11px;">'
            f'── {title} ──</span></td></tr>'
        )

    @staticmethod
    def _row(color: str, name: str, detail: str, badge: str, badge_color: str) -> str:
        return (
            f'<tr>'
            f'<td style="padding:1px 4px 1px 0;width:14px;">'
            f'  <span style="color:{color};font-size:14px;">&#x25CF;</span></td>'
            f'<td style="padding:1px 6px 1px 0;white-space:nowrap;">'
            f'  <span style="color:{TEXT_PRIMARY};">{name}</span></td>'
            f'<td style="padding:1px 8px 1px 0;white-space:nowrap;">'
            f'  <span style="color:{TEXT_DIM};font-size:11px;">{detail}</span></td>'
            f'<td style="padding:1px 0;white-space:nowrap;">'
            f'  <span style="color:{badge_color};font-size:11px;">{badge}</span></td>'
            f'</tr>'
        )
