"""TerDash — 开发者仪表盘应用."""

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QScrollArea,
)

from terdash.widgets.contributions_graph import ContributionsGraph
from terdash.widgets.commit_streak import CommitStreak
from terdash.widgets.code_time_bars import CodeTimeBars
from terdash.widgets.cpu_gauge import CpuGauge
from terdash.widgets.memory_gauge import MemoryGauge
from terdash.widgets.network_speed import NetworkSpeed
from terdash.widgets.service_health import ServiceHealth
from terdash.widgets.subscription_radar import SubscriptionRadar
from terdash.theme import PANEL_ACCENTS


class PanelBox(QFrame):
    """A styled panel container with a title, content widget, and colored left border."""

    _id_counter = 0

    def __init__(self, title: str, content: QWidget, accent_color: str = None, parent=None):
        super().__init__(parent)
        # Unique object name so per-instance stylesheet doesn't bleed
        PanelBox._id_counter += 1
        uid = f"panel-box-{PanelBox._id_counter}"
        self.setObjectName(uid)
        self.setProperty("class", "panel-box")

        if accent_color:
            self.setStyleSheet(
                f"QFrame#{uid} {{ border-left: 3px solid {accent_color}; }}"
            )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setProperty("class", "panel-title")
        title_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(title_label)

        layout.addWidget(content)


class TerDashWindow(QMainWindow):
    """Main TerDash desktop window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TerDash // 开发者仪表盘")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        self._load_stylesheet()
        self._build_ui()
        self._start_all_updates()

    def _load_stylesheet(self):
        qss_path = Path(__file__).parent / "styles" / "terdash.qss"
        if qss_path.exists():
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header bar ──
        header = QFrame()
        header.setObjectName("header-bar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 4, 12, 4)

        header_title = QLabel("TerDash")
        header_title.setObjectName("header-title")
        header_layout.addWidget(header_title)

        header_layout.addStretch()

        self._clock_label = QLabel()
        self._clock_label.setObjectName("header-clock")
        header_layout.addWidget(self._clock_label)
        self._update_clock()

        root_layout.addWidget(header)

        # ── Scrollable content area ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("main-scroll")

        content_area = QWidget()
        content_area.setObjectName("central")
        main_layout = QHBoxLayout(content_area)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ── Left column — Developer Stats ──
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self._contrib_graph = ContributionsGraph()
        left_layout.addWidget(
            PanelBox("GitHub 贡献热力图", self._contrib_graph,
                     accent_color=PANEL_ACCENTS["contrib"])
        )

        self._commit_streak = CommitStreak()
        left_layout.addWidget(
            PanelBox("连续提交", self._commit_streak,
                     accent_color=PANEL_ACCENTS["streak"])
        )

        self._code_time = CodeTimeBars()
        left_layout.addWidget(
            PanelBox("今日编码时长", self._code_time,
                     accent_color=PANEL_ACCENTS["codetime"])
        )

        left_layout.addStretch()

        # ── Right column — System & Finance ──
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # CPU + Memory side by side
        gauge_row = QWidget()
        gauge_layout = QHBoxLayout(gauge_row)
        gauge_layout.setContentsMargins(0, 0, 0, 0)
        gauge_layout.setSpacing(6)

        self._cpu_gauge = CpuGauge()
        gauge_layout.addWidget(
            PanelBox("CPU", self._cpu_gauge,
                     accent_color=PANEL_ACCENTS["cpu"])
        )

        self._mem_gauge = MemoryGauge()
        gauge_layout.addWidget(
            PanelBox("内存", self._mem_gauge,
                     accent_color=PANEL_ACCENTS["memory"])
        )

        right_layout.addWidget(gauge_row)

        self._net_speed = NetworkSpeed()
        right_layout.addWidget(
            PanelBox("网络速度", self._net_speed,
                     accent_color=PANEL_ACCENTS["network"])
        )

        self._svc_health = ServiceHealth()
        right_layout.addWidget(
            PanelBox("服务 & 运行环境", self._svc_health,
                     accent_color=PANEL_ACCENTS["services"])
        )

        self._sub_radar = SubscriptionRadar()
        right_layout.addWidget(
            PanelBox("订阅雷达", self._sub_radar,
                     accent_color=PANEL_ACCENTS["subscriptions"])
        )

        right_layout.addStretch()

        # 55-45 split
        main_layout.addWidget(left, stretch=11)
        main_layout.addWidget(right, stretch=9)

        scroll.setWidget(content_area)
        root_layout.addWidget(scroll, stretch=1)

    def _update_clock(self):
        now = datetime.now()
        self._clock_label.setText(now.strftime("%Y-%m-%d  %H:%M:%S"))

    def _start_all_updates(self):
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

        self._contrib_graph.data_fetched.connect(self._on_contrib_data)

        self._contrib_graph.start_updates()
        self._code_time.start_updates()
        self._cpu_gauge.start_updates()
        self._mem_gauge.start_updates()
        self._net_speed.start_updates()
        self._svc_health.start_updates()
        self._sub_radar.start_updates()

    def _on_contrib_data(self, data: dict):
        self._commit_streak.update_data(
            data.get("current_streak", 0),
            data.get("yearly_total", 0),
        )
