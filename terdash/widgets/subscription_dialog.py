"""Subscription add dialog — form for manually adding subscriptions."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton,
)

from terdash.theme import BG_PANEL, BG_SURFACE, BG_BORDER, TEXT_PRIMARY, TEXT_DIM, CYAN


class SubscriptionAddDialog(QDialog):
    """A form dialog for adding a new subscription."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加订阅")
        self.setFixedWidth(400)
        self.setStyleSheet(self._build_style())

        self._result_data: dict | None = None
        self._build_ui()

    def _build_style(self) -> str:
        return f"""
            QDialog {{
                background-color: {BG_PANEL};
                border: 1px solid {BG_BORDER};
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLabel#dialog-title {{
                color: {CYAN};
                font-size: 15px;
                font-weight: bold;
                padding-bottom: 6px;
            }}
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BG_BORDER};
                border-radius: 5px;
                padding: 5px 8px;
                font-size: 13px;
                min-height: 24px;
            }}
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus,
            QSpinBox:focus {{
                border: 1px solid {CYAN};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BG_BORDER};
                selection-background-color: {BG_BORDER};
            }}
            QPushButton#btn-confirm {{
                background-color: {CYAN};
                color: #0d1b2a;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
            }}
            QPushButton#btn-confirm:hover {{
                background-color: #7ce0f0;
            }}
            QPushButton#btn-cancel {{
                background-color: transparent;
                color: {TEXT_DIM};
                font-size: 13px;
                border: 1px solid {BG_BORDER};
                border-radius: 6px;
                padding: 8px 24px;
            }}
            QPushButton#btn-cancel:hover {{
                border-color: {TEXT_DIM};
                color: {TEXT_PRIMARY};
            }}
        """

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("添加新订阅")
        title.setObjectName("dialog-title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        # Name
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("例如: Netflix, ChatGPT Plus")
        form.addRow("名称", self._name_input)

        # Category
        self._category_input = QComboBox()
        self._category_input.addItems(["流媒体", "服务器", "API", "工具", "存储", "其他"])
        self._category_input.setEditable(True)
        form.addRow("分类", self._category_input)

        # Amount
        self._amount_input = QDoubleSpinBox()
        self._amount_input.setRange(0.01, 99999.99)
        self._amount_input.setDecimals(2)
        self._amount_input.setValue(9.99)
        form.addRow("金额", self._amount_input)

        # Currency
        self._currency_input = QComboBox()
        self._currency_input.addItems(["USD", "CNY", "JPY", "EUR", "GBP"])
        form.addRow("货币", self._currency_input)

        # Billing cycle
        self._cycle_input = QSpinBox()
        self._cycle_input.setRange(1, 365)
        self._cycle_input.setValue(30)
        self._cycle_input.setSuffix(" 天")
        form.addRow("账单周期", self._cycle_input)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_cancel = QPushButton("取消")
        btn_cancel.setObjectName("btn-cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_layout.addStretch()

        btn_confirm = QPushButton("确认添加")
        btn_confirm.setObjectName("btn-confirm")
        btn_confirm.clicked.connect(self._on_confirm)
        btn_layout.addWidget(btn_confirm)

        layout.addLayout(btn_layout)

    def _on_confirm(self):
        name = self._name_input.text().strip()
        if not name:
            self._name_input.setFocus()
            return

        self._result_data = {
            "name": name,
            "category": self._category_input.currentText().strip() or "其他",
            "amount": self._amount_input.value(),
            "currency": self._currency_input.currentText(),
            "billing_cycle_days": self._cycle_input.value(),
        }
        self.accept()

    def get_data(self) -> dict | None:
        """Return the form data if confirmed, else None."""
        return self._result_data
