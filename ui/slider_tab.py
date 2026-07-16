"""
Slider tab — pick Base / Accent / Highlight via OKLCH sliders (Hue, Chroma, Lightness).
Live preview updates as sliders move. Apply writes to Max.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel,
    QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QBrush, QPen

from theme_engine import generate_color_map, hex_to_oklch, oklch_to_hex
import clrx_writer


class GradientSlider(QSlider):
    """Horizontal slider painted with a color gradient."""
    def __init__(self, min_val=0, max_val=100, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setRange(min_val, max_val)
        self._stops: list[tuple[float, str]] = []

    def set_gradient(self, stops: list[tuple[float, str]]):
        self._stops = stops
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._stops:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        groove_h = 4
        y = (self.height() - groove_h) // 2
        grad = QLinearGradient(0, y, self.width(), y)
        for pos, color in self._stops:
            grad.setColorAt(pos, QColor(color))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(0, y, self.width(), groove_h, 2, 2)


class ColorRowWidget(QFrame):
    """One row: label + H/C/L sliders + live hex preview."""
    changed = Signal(str, str)  # (role, hex_color)

    def __init__(self, role: str, initial_hex: str, parent=None):
        super().__init__(parent)
        self._role = role
        self.setObjectName("ColorRow")
        L, C, H = hex_to_oklch(initial_hex)
        self._L = L
        self._C = C
        self._H = H
        self._build()
        self._refresh_preview()

    def _build(self):
        lay = QGridLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(6)

        title = QLabel(self._role)
        title.setObjectName("RowTitle")
        lay.addWidget(title, 0, 0, 1, 3)

        # Hue
        h_lbl = QLabel("Hue")
        h_lbl.setObjectName("SliderLabel")
        self._h_slider = GradientSlider(0, 360)
        self._h_slider.setValue(int(self._H))
        self._h_val = QLabel(f"{int(self._H)}°")
        self._h_val.setObjectName("SliderValue")
        self._h_val.setFixedWidth(38)
        lay.addWidget(h_lbl,         1, 0)
        lay.addWidget(self._h_slider, 1, 1)
        lay.addWidget(self._h_val,   1, 2)

        # Chroma
        c_lbl = QLabel("Chroma")
        c_lbl.setObjectName("SliderLabel")
        self._c_slider = GradientSlider(0, 40)  # OKLCH chroma ×100
        self._c_slider.setValue(int(self._C * 100))
        self._c_val = QLabel(f"{self._C:.2f}")
        self._c_val.setObjectName("SliderValue")
        self._c_val.setFixedWidth(38)
        lay.addWidget(c_lbl,         2, 0)
        lay.addWidget(self._c_slider, 2, 1)
        lay.addWidget(self._c_val,   2, 2)

        # Lightness
        l_lbl = QLabel("Lightness")
        l_lbl.setObjectName("SliderLabel")
        self._l_slider = GradientSlider(0, 100)
        self._l_slider.setValue(int(self._L * 100))
        self._l_val = QLabel(f"{self._L:.2f}")
        self._l_val.setObjectName("SliderValue")
        self._l_val.setFixedWidth(38)
        lay.addWidget(l_lbl,         3, 0)
        lay.addWidget(self._l_slider, 3, 1)
        lay.addWidget(self._l_val,   3, 2)

        # Preview swatch
        self._preview = QWidget()
        self._preview.setFixedSize(48, 48)
        self._preview.setObjectName("SwatchColor")
        lay.addWidget(self._preview, 0, 3, 4, 1, Qt.AlignRight | Qt.AlignVCenter)

        lay.setColumnStretch(1, 1)

        self._h_slider.valueChanged.connect(self._on_h)
        self._c_slider.valueChanged.connect(self._on_c)
        self._l_slider.valueChanged.connect(self._on_l)
        self._update_hue_gradient()

    def _on_h(self, v):
        self._H = float(v)
        self._h_val.setText(f"{v}°")
        self._update_hue_gradient()
        self._refresh_preview()

    def _on_c(self, v):
        self._C = v / 100.0
        self._c_val.setText(f"{self._C:.2f}")
        self._refresh_preview()

    def _on_l(self, v):
        self._L = v / 100.0
        self._l_val.setText(f"{self._L:.2f}")
        self._refresh_preview()

    def _update_hue_gradient(self):
        stops = [(i / 360, oklch_to_hex(0.65, 0.2, i)) for i in range(0, 361, 10)]
        self._h_slider.set_gradient(stops)

    def _refresh_preview(self):
        hex_val = oklch_to_hex(self._L, self._C, self._H)
        self._preview.setStyleSheet(
            f"background:{hex_val}; border-radius:4px;"
            " border:1px solid rgba(255,255,255,0.15);"
        )
        self.changed.emit(self._role, hex_val)

    def current_hex(self) -> str:
        return oklch_to_hex(self._L, self._C, self._H)

    def set_hex(self, hex_color: str):
        L, C, H = hex_to_oklch(hex_color)
        self._L, self._C, self._H = L, C, H
        self._h_slider.blockSignals(True)
        self._c_slider.blockSignals(True)
        self._l_slider.blockSignals(True)
        self._h_slider.setValue(int(H))
        self._c_slider.setValue(int(C * 100))
        self._l_slider.setValue(int(L * 100))
        self._h_val.setText(f"{int(H)}°")
        self._c_val.setText(f"{C:.2f}")
        self._l_val.setText(f"{L:.2f}")
        self._h_slider.blockSignals(False)
        self._c_slider.blockSignals(False)
        self._l_slider.blockSignals(False)
        self._refresh_preview()
        self._update_hue_gradient()


class MiniPreview(QFrame):
    """Small fake UI preview showing base/accent/highlight as mock buttons."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MiniPreview")
        self.setFixedHeight(64)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)
        self._bg_lbl  = QLabel("Background")
        self._btn_lbl = QPushButton("Button")
        self._hi_lbl  = QLabel("Highlight")
        for w in (self._bg_lbl, self._btn_lbl, self._hi_lbl):
            lay.addWidget(w)
        lay.addStretch()

    def update(self, base: str, accent: str, highlight: str):
        from theme_engine import _contrast_text
        bg_text  = _contrast_text(base)
        btn_text = _contrast_text(accent)
        self._bg_lbl.setStyleSheet(f"color:{bg_text}; padding: 4px 8px;")
        self.setStyleSheet(f"#MiniPreview {{ background:{base}; border-radius:4px; }}")
        self._btn_lbl.setStyleSheet(
            f"QPushButton {{ background:{accent}; color:{btn_text};"
            " border:none; padding:4px 12px; border-radius:3px; }}"
        )
        self._hi_lbl.setStyleSheet(f"color:{highlight}; padding: 4px 8px;")


class SliderPanel(QWidget):
    colors_changed = Signal(str, str, str)   # base, accent, highlight

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        self._base_row      = ColorRowWidget("Base",      "#1c1c1c")
        self._accent_row    = ColorRowWidget("Accent",    "#5f8ac1")
        self._highlight_row = ColorRowWidget("Highlight", "#ffb100")

        for row in (self._base_row, self._accent_row, self._highlight_row):
            row.changed.connect(self._on_changed)
            outer.addWidget(row)

        self._preview = MiniPreview()
        outer.addWidget(self._preview)
        outer.addStretch()

        btn = QPushButton("Apply to 3ds Max")
        btn.setObjectName("ApplyButton")
        btn.setFixedHeight(32)
        btn.clicked.connect(self._apply)
        outer.addWidget(btn)

        self._refresh_preview()

    def _on_changed(self, *_):
        self._refresh_preview()

    def _refresh_preview(self):
        b = self._base_row.current_hex()
        a = self._accent_row.current_hex()
        h = self._highlight_row.current_hex()
        self._preview.update(b, a, h)
        self.colors_changed.emit(b, a, h)

    def set_base_colors(self, base: str, accent: str, highlight: str):
        for row, val in (
            (self._base_row, base),
            (self._accent_row, accent),
            (self._highlight_row, highlight),
        ):
            row.changed.disconnect(self._on_changed)
            row.set_hex(val)
            row.changed.connect(self._on_changed)
        self._refresh_preview()

    def current_colors(self) -> tuple[str, str, str]:
        return (
            self._base_row.current_hex(),
            self._accent_row.current_hex(),
            self._highlight_row.current_hex(),
        )

    def _apply(self):
        base, accent, highlight = self.current_colors()
        cmap = generate_color_map(base, accent, highlight)
        clrx_writer.write_clrx(cmap)
        clrx_writer.apply_to_max()


# Keep old name as alias for backward compat
SliderTab = SliderPanel
