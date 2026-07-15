"""
Presets tab — grid of preset cards, click to select, Apply to write to Max.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QBrush

import presets as preset_data
from theme_engine import generate_color_map
import clrx_writer


class ColorDot(QWidget):
    def __init__(self, hex_color: str, size=14, parent=None):
        super().__init__(parent)
        self._color = QColor(hex_color)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(1, 1, self.width()-2, self.height()-2)


class PresetCard(QFrame):
    selected = Signal(dict)

    def __init__(self, preset: dict, parent=None):
        super().__init__(parent)
        self._preset = preset
        self._active = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(160, 80)
        self._build()

    def _build(self):
        self.setObjectName("PresetCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(4)

        name = QLabel(self._preset["name"])
        name.setObjectName("CardTitle")
        lay.addWidget(name)

        dots_row = QHBoxLayout()
        dots_row.setSpacing(6)
        dots_row.setAlignment(Qt.AlignLeft)
        for key, label in (("base", "B"), ("accent", "A"), ("highlight", "H")):
            col = self._preset[key]
            dot_wrap = QVBoxLayout()
            dot_wrap.setSpacing(2)
            dot_wrap.setAlignment(Qt.AlignHCenter)
            dot_wrap.addWidget(ColorDot(col, 18))
            lbl = QLabel(label)
            lbl.setObjectName("DotLabel")
            lbl.setAlignment(Qt.AlignHCenter)
            dot_wrap.addWidget(lbl)
            dots_row.addLayout(dot_wrap)
        dots_row.addStretch()
        lay.addLayout(dots_row)

    def set_active(self, active: bool):
        self._active = active
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        self.selected.emit(self._preset)


class PresetTab(QWidget):
    preset_applied = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_preset = preset_data.PRESETS[0]
        self._cards: list[PresetCard] = []
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setSpacing(10)

        for i, preset in enumerate(preset_data.PRESETS):
            card = PresetCard(preset)
            card.selected.connect(self._on_preset_selected)
            self._cards.append(card)
            grid.addWidget(card, i // 3, i % 3)

        scroll.setWidget(container)
        outer.addWidget(scroll)

        # Preview strip
        self._preview = PreviewStrip()
        outer.addWidget(self._preview)

        btn = QPushButton("Apply to 3ds Max")
        btn.setObjectName("ApplyButton")
        btn.setFixedHeight(32)
        btn.clicked.connect(self._apply)
        outer.addWidget(btn)

        self._on_preset_selected(self._current_preset)

    def _on_preset_selected(self, preset: dict):
        self._current_preset = preset
        for card in self._cards:
            card.set_active(card._preset is preset)
        self._preview.update_colors(preset["base"], preset["accent"], preset["highlight"])

    def _apply(self):
        p = self._current_preset
        cmap = generate_color_map(p["base"], p["accent"], p["highlight"])
        clrx_writer.write_clrx(cmap, theme_type=p.get("theme_type", 0))
        clrx_writer.apply_to_max()
        self.preset_applied.emit(p)


class PreviewStrip(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewStrip")
        self.setFixedHeight(48)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(8)

        self._bg   = QWidget(); self._bg.setFixedSize(22, 22);   self._bg.setObjectName("PreviewSwatch")
        self._acc  = QWidget(); self._acc.setFixedSize(22, 22);  self._acc.setObjectName("PreviewSwatch")
        self._hi   = QWidget(); self._hi.setFixedSize(22, 22);   self._hi.setObjectName("PreviewSwatch")
        self._lbl  = QLabel("Base · Accent · Highlight")
        self._lbl.setObjectName("PreviewLabel")

        for w, t in ((self._bg, "Base"), (self._acc, "Accent"), (self._hi, "Highlight")):
            wrap = QVBoxLayout()
            wrap.setSpacing(2)
            wrap.addWidget(w, alignment=Qt.AlignHCenter)
            l = QLabel(t); l.setObjectName("DotLabel")
            wrap.addWidget(l, alignment=Qt.AlignHCenter)
            lay.addLayout(wrap)
        lay.addStretch()

    def update_colors(self, base: str, accent: str, highlight: str):
        for widget, color in ((self._bg, base), (self._acc, accent), (self._hi, highlight)):
            widget.setStyleSheet(
                f"background:{color}; border-radius:3px; border:1px solid rgba(255,255,255,0.15);"
            )
