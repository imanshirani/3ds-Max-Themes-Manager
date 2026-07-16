"""
Settings / About dialog for 3ds Max Themes Manager.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont

import constants


class SettingsDialog(QDialog):
    def __init__(self, parent=None, stylesheet: str = ""):
        super().__init__(parent)
        self.setWindowTitle(f"Settings — {constants.PRODUCT_NAME}")
        self.setFixedWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        if stylesheet:
            self.setStyleSheet(stylesheet)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        # ── Product info ──────────────────────────────────────
        info_group = QGroupBox("Product Information")
        info_lay = QVBoxLayout(info_group)
        info_lay.setContentsMargins(14, 20, 14, 14)
        info_lay.setSpacing(8)

        title_lbl = QLabel(constants.PRODUCT_NAME)
        title_lbl.setObjectName("DialogProductTitle")
        info_lay.addWidget(title_lbl)

        meta_lbl = QLabel(
            f"Version: {constants.VERSION}<br>{constants.DEVELOPER_TAG}"
        )
        meta_lbl.setStyleSheet("font-size: 11px;")
        info_lay.addWidget(meta_lbl)

        info_lay.addSpacing(6)

        # GitHub + PayPal buttons
        link_row = QHBoxLayout()
        link_row.setSpacing(8)

        self._btn_github = QPushButton("  GitHub")
        self._btn_github.setObjectName("GithubBtn")
        self._btn_github.setFixedHeight(30)
        self._btn_github.setCursor(Qt.PointingHandCursor)
        self._btn_github.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(constants.GITHUB_URL))
        )

        self._btn_paypal = QPushButton("  Support (PayPal)")
        self._btn_paypal.setObjectName("PaypalBtn")
        self._btn_paypal.setFixedHeight(30)
        self._btn_paypal.setCursor(Qt.PointingHandCursor)
        self._btn_paypal.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(constants.DONATION_LINK))
        )

        link_row.addWidget(self._btn_github)
        link_row.addWidget(self._btn_paypal)
        info_lay.addLayout(link_row)
        lay.addWidget(info_group)

        # ── Separator ────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #2e2e2e;")
        lay.addWidget(sep)

        # ── Close ────────────────────────────────────────────
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(30)
        close_btn.clicked.connect(self.accept)
        lay.addWidget(close_btn, alignment=Qt.AlignRight)
