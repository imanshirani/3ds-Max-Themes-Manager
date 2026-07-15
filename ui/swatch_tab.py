"""
Swatches panel — 3 simple color pickers (Base/Accent/Highlight) + MiniPreview + read-only swatches.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QColorDialog, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from theme_engine import generate_color_map, _shift, _is_dark
import clrx_writer


SWATCH_GROUPS = [
    ("Background", [111, 112, 129, 130]),
    ("Buttons",    [113, 114, 25]),
    ("Borders",    [116, 117, 5, 6]),
    ("Text",       [1, 11, 20]),
    ("Accent",     [4, 13, 14, 34]),
    ("Highlight",  [9, 24, 136]),
    ("Trackbar",   [18, 19, 26]),
    ("Viewport",   [27, 28]),
    ("Status",     [135, 134, 118]),
]

COLOR_NAMES = {
    111: "BG",     112: "BG Alt", 129: "Row",    130: "Row Alt",
    113: "Button", 114: "Btn Txt", 25: "Pressed",
    116: "Focus",  117: "Border",  5: "Hilight",  6: "Shadow",
    1:   "Text",   11:  "Sel Txt", 20: "TB Txt",
    4:   "Active", 13:  "Hilight", 14: "Sub-Obj", 34: "Modifier",
    9:   "Tip BG", 24:  "Cursor",  136: "Search",
    18:  "TB BG",  19:  "TB Sel",  26: "Time BG",
    27:  "VP Bdr", 28:  "VP Act",
    135: "Error",  134: "Warning", 118: "Anim",
}


class ColorPickerRow(QFrame):
    """Label + colored rect (click = QColorDialog) + hex value."""
    color_changed = Signal(str, str)   # (role, hex)

    def __init__(self, role: str, initial_hex: str, parent=None):
        super().__init__(parent)
        self._role = role
        self._hex  = initial_hex
        self.setObjectName("ColorPickerRow")
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(10)

        lbl = QLabel(self._role)
        lbl.setObjectName("PickerLabel")
        lbl.setFixedWidth(70)
        lay.addWidget(lbl)

        self._swatch = QWidget()
        self._swatch.setFixedSize(36, 24)
        self._swatch.setCursor(Qt.PointingHandCursor)
        self._swatch.setObjectName("PickerSwatch")
        self._swatch.mousePressEvent = self._open_dialog
        lay.addWidget(self._swatch)

        self._hex_lbl = QLabel(self._hex)
        self._hex_lbl.setObjectName("HexLabel")
        lay.addWidget(self._hex_lbl)
        lay.addStretch()

        self._apply_color()

    def _apply_color(self):
        self._swatch.setStyleSheet(
            f"background:{self._hex}; border-radius:3px;"
            " border:1px solid rgba(255,255,255,0.2);"
        )
        self._hex_lbl.setText(self._hex)

    def _open_dialog(self, _event):
        dlg = QColorDialog(QColor(self._hex), self)
        if dlg.exec():
            self.set_hex(dlg.selectedColor().name())

    def set_hex(self, hex_color: str):
        self._hex = hex_color
        self._apply_color()
        self.color_changed.emit(self._role, hex_color)

    def current_hex(self) -> str:
        return self._hex


class ReadOnlySwatch(QWidget):
    """Non-interactive color chip with a label — just for display."""
    def __init__(self, color_id: int, hex_color: str, parent=None):
        super().__init__(parent)
        self._id = color_id
        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 4)
        lay.setSpacing(2)
        self._rect = QWidget()
        self._rect.setFixedHeight(22)
        self._rect.setMinimumWidth(36)
        lay.addWidget(self._rect)
        lbl = QLabel(COLOR_NAMES.get(color_id, str(color_id)))
        lbl.setObjectName("SwatchLabel")
        lbl.setAlignment(Qt.AlignHCenter)
        lbl.setWordWrap(True)
        lay.addWidget(lbl)
        self.set_color(hex_color)

    def set_color(self, hex_color: str):
        self._rect.setStyleSheet(
            f"background:{hex_color}; border-radius:3px;"
            " border:1px solid rgba(255,255,255,0.10);"
        )


class MiniPreview(QFrame):
    """Mock UI preview: background / button / highlight text."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MiniPreview")
        self.setFixedHeight(56)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)
        self._bg_lbl  = QLabel("Background")
        self._btn     = QPushButton("Button")
        self._hi_lbl  = QLabel("Highlight")
        for w in (self._bg_lbl, self._btn, self._hi_lbl):
            lay.addWidget(w)
        lay.addStretch()

    def update(self, base: str, accent: str, highlight: str):
        text = _shift(base, dL=0.65 if _is_dark(base) else -0.65, scaleC=0.05)
        self.setStyleSheet(f"#MiniPreview {{ background:{base}; border-radius:4px; }}")
        self._bg_lbl.setStyleSheet(f"color:{text}; padding:2px 6px;")
        self._btn.setStyleSheet(
            f"QPushButton {{ background:{accent}; color:{text};"
            " border:none; padding:3px 10px; border-radius:3px; }}"
        )
        self._hi_lbl.setStyleSheet(f"color:{highlight}; padding:2px 6px;")


class SwatchPanel(QWidget):
    colors_changed = Signal(str, str, str)   # base, accent, highlight

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ro_swatches: dict[int, ReadOnlySwatch] = {}
        self._build()
        self._on_any_changed()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        # ── Color pickers ──
        picker_frame = QFrame()
        picker_frame.setObjectName("PickerFrame")
        pf_lay = QVBoxLayout(picker_frame)
        pf_lay.setContentsMargins(0, 4, 0, 4)
        pf_lay.setSpacing(2)

        self._base_row      = ColorPickerRow("Base",      "#1c1c1c")
        self._accent_row    = ColorPickerRow("Accent",    "#5f8ac1")
        self._highlight_row = ColorPickerRow("Highlight", "#ffb100")

        for row in (self._base_row, self._accent_row, self._highlight_row):
            row.color_changed.connect(self._on_any_changed)
            pf_lay.addWidget(row)

        outer.addWidget(picker_frame)

        # ── MiniPreview ──
        self._preview = MiniPreview()
        outer.addWidget(self._preview)

        # ── Read-only swatches ──
        ro_lbl = QLabel("Generated colors")
        ro_lbl.setObjectName("SectionLabel")
        outer.addWidget(ro_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        groups_lay = QVBoxLayout(container)
        groups_lay.setContentsMargins(0, 0, 0, 0)
        groups_lay.setSpacing(10)

        initial_map = generate_color_map("#1c1c1c", "#5f8ac1", "#ffb100")
        for group_name, ids in SWATCH_GROUPS:
            g_frame = QFrame()
            g_frame.setObjectName("SwatchGroup")
            g_lay = QVBoxLayout(g_frame)
            g_lay.setContentsMargins(8, 5, 8, 5)
            g_lay.setSpacing(4)
            g_lbl = QLabel(group_name)
            g_lbl.setObjectName("GroupTitle")
            g_lay.addWidget(g_lbl)
            row = QHBoxLayout()
            row.setSpacing(4)
            row.setAlignment(Qt.AlignLeft)
            for cid in ids:
                sw = ReadOnlySwatch(cid, initial_map.get(cid, "#444"))
                self._ro_swatches[cid] = sw
                row.addWidget(sw)
            row.addStretch()
            g_lay.addLayout(row)
            groups_lay.addWidget(g_frame)
        groups_lay.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll, stretch=1)

        # ── Apply ──
        btn = QPushButton("Apply to 3ds Max")
        btn.setObjectName("ApplyButton")
        btn.setFixedHeight(32)
        btn.clicked.connect(self._apply)
        outer.addWidget(btn)

    def _on_any_changed(self, *_):
        b = self._base_row.current_hex()
        a = self._accent_row.current_hex()
        h = self._highlight_row.current_hex()
        self._preview.update(b, a, h)
        cmap = generate_color_map(b, a, h)
        for cid, sw in self._ro_swatches.items():
            if cid in cmap:
                sw.set_color(cmap[cid])
        self.colors_changed.emit(b, a, h)

    def set_base_colors(self, base: str, accent: str, highlight: str):
        for row, val in (
            (self._base_row, base),
            (self._accent_row, accent),
            (self._highlight_row, highlight),
        ):
            row.color_changed.disconnect(self._on_any_changed)
            row.set_hex(val)
            row.color_changed.connect(self._on_any_changed)
        self._on_any_changed()

    def current_colors(self) -> tuple[str, str, str]:
        return (
            self._base_row.current_hex(),
            self._accent_row.current_hex(),
            self._highlight_row.current_hex(),
        )

    def _apply(self):
        b, a, h = self.current_colors()
        cmap = generate_color_map(b, a, h)
        clrx_writer.write_clrx(cmap)
        clrx_writer.apply_to_max()
