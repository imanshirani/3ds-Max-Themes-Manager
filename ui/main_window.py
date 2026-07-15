"""
Main window for the 3ds Max Themes Manager.
Layout: sidebar (preset list) on the left + right panel with Swatches / Sliders toggle.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

from ui.preset_sidebar  import PresetSidebar
from ui.swatch_tab      import SwatchPanel
from ui.slider_tab      import SliderPanel
from ui.settings_dialog import SettingsDialog
import clrx_writer
from theme_engine import generate_color_map


STYLESHEET = """
QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    color: #dcdcdc;
    background: #1c1c1c;
}

/* ── Sidebar ─────────────────────────────────────── */
QFrame#Sidebar {
    background: #1a1a1a;
    border-right: 1px solid #2e2e2e;
}
QLabel#SidebarTitle {
    color: #aaaaaa;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 0;
}
QListWidget#PresetList {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget#PresetList::item {
    padding: 6px 8px;
    border-radius: 4px;
    margin: 1px 2px;
    color: #cccccc;
}
QListWidget#PresetList::item:selected {
    background: #243040;
    color: #ffffff;
}
QListWidget#PresetList::item:hover:!selected {
    background: #252525;
}

/* ── Preview strip ───────────────────────────────── */
QFrame#PreviewStrip {
    background: #222222;
    border: 1px solid #2e2e2e;
    border-radius: 5px;
}
QLabel#DotLabel { color: #777777; font-size: 10px; }

/* ── Toggle buttons (Swatches / Sliders) ─────────── */
QPushButton#ToggleBtn {
    background: #252525;
    color: #888888;
    border: 1px solid #333333;
    border-radius: 3px;
    padding: 4px 0;
    font-size: 12px;
}
QPushButton#ToggleBtn:hover  { color: #cccccc; }
QPushButton#ToggleBtn[active=true] {
    background: #1e2d3d;
    color: #ffffff;
    border-color: #5f8ac1;
}

/* ── Settings button ─────────────────────────────── */
QPushButton#SettingsBtn {
    background: transparent;
    color: #666666;
    border: none;
    padding: 4px 8px;
    font-size: 12px;
}
QPushButton#SettingsBtn:hover { color: #aaaaaa; }

/* ── Settings dialog ─────────────────────────────── */
QGroupBox {
    color: #888888;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid #2e2e2e;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QLabel#DialogProductTitle {
    color: #dddddd;
    font-size: 14px;
    font-weight: 700;
}
QPushButton#GithubBtn {
    background: #24292e;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px 12px;
    font-weight: 600;
}
QPushButton#GithubBtn:hover { background: #2f363d; }
QPushButton#PaypalBtn {
    background: #003087;
    color: #ffffff;
    border: 1px solid #0070ba;
    border-radius: 4px;
    padding: 4px 12px;
    font-weight: 600;
}
QPushButton#PaypalBtn:hover { background: #0070ba; }

/* ── Apply button ────────────────────────────────── */
QPushButton#ApplyButton {
    background: #5f8ac1;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 0 14px;
    font-weight: 600;
}
QPushButton#ApplyButton:hover  { background: #496a93; }
QPushButton#ApplyButton:pressed{ background: #3a5270; }

/* ── Generic buttons ─────────────────────────────── */
QPushButton {
    background: #2e2e2e;
    color: #cccccc;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    padding: 3px 10px;
}
QPushButton:hover  { background: #383838; color: #ffffff; }
QPushButton:pressed{ background: #252525; }

/* ── Scrollbars ──────────────────────────────────── */
QScrollArea { background: transparent; border: none; }
QScrollBar:vertical {
    background: #1c1c1c; width: 7px; border: none;
}
QScrollBar::handle:vertical {
    background: #3e3e3e; border-radius: 3px; min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Color picker row ────────────────────────────── */
QFrame#PickerFrame   { background: #222222; border: 1px solid #2e2e2e; border-radius: 5px; }
QFrame#ColorPickerRow{ background: transparent; }
QLabel#PickerLabel   { color: #aaaaaa; font-size: 12px; }
QLabel#HexLabel      { color: #666666; font-size: 11px; font-family: "Consolas", monospace; }

/* ── Read-only swatches ──────────────────────────── */
QFrame#SwatchGroup {
    background: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
}
QLabel#GroupTitle  { color: #888888; font-size: 11px; font-weight: 600; }
QLabel#SwatchLabel { color: #666666; font-size: 9px; }
QLabel#SectionLabel{ color: #666666; font-size: 11px; font-weight: 600; margin-top: 4px; }

/* ── MiniPreview ─────────────────────────────────── */
QFrame#MiniPreview { border-radius: 5px; border: 1px solid #2e2e2e; }

/* ── OKLCH sliders ───────────────────────────────── */
QFrame#ColorRow {
    background: #1e1e1e;
    border: 1px solid #2e2e2e;
    border-radius: 5px;
}
QLabel#RowTitle   { color: #dcdcdc; font-weight: 600; font-size: 13px; }
QLabel#SliderLabel{ color: #888888; font-size: 11px; min-width: 62px; }
QLabel#SliderValue{ color: #666666; font-size: 11px; }
QSlider::groove:horizontal {
    height: 4px; background: #333333; border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #cccccc; border: 1px solid #777777;
    width: 12px; height: 12px; margin: -4px 0; border-radius: 6px;
}
QSlider::handle:horizontal:hover { background: #ffffff; }
"""


class ThemeMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3ds Max Themes Manager")
        self.setMinimumSize(640, 540)
        self.setStyleSheet(STYLESHEET)
        self._current_colors = ("#1c1c1c", "#5f8ac1", "#ffb100")
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left sidebar ────────────────────────────────────
        self._sidebar = PresetSidebar()
        self._sidebar.setObjectName("Sidebar")
        self._sidebar.setFixedWidth(200)
        self._sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self._sidebar.preset_selected.connect(self._on_preset_selected)
        self._sidebar.preset_applied.connect(self._on_preset_applied)
        self._sidebar.save_requested.connect(self._on_save_requested)
        root.addWidget(self._sidebar)

        # ── Right panel ─────────────────────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        # Mode toggle bar
        toggle_bar = QWidget()
        toggle_bar.setObjectName("ToggleBar")
        toggle_bar.setFixedHeight(36)
        toggle_bar.setStyleSheet(
            "#ToggleBar { background:#181818; border-bottom:1px solid #2a2a2a; }"
        )
        tbl = QHBoxLayout(toggle_bar)
        tbl.setContentsMargins(10, 5, 10, 5)
        tbl.setSpacing(6)

        self._btn_swatch = QPushButton("Swatches")
        self._btn_slider = QPushButton("Sliders")
        for btn in (self._btn_swatch, self._btn_slider):
            btn.setObjectName("ToggleBtn")
            btn.setFixedHeight(26)
            tbl.addWidget(btn)
        tbl.addStretch()

        self._btn_settings = QPushButton("⚙ Settings")
        self._btn_settings.setObjectName("SettingsBtn")
        self._btn_settings.setFixedHeight(26)
        tbl.addWidget(self._btn_settings)
        right_lay.addWidget(toggle_bar)

        # Stacked panels
        self._stack = QStackedWidget()
        self._swatch_panel = SwatchPanel()
        self._slider_panel = SliderPanel()
        self._stack.addWidget(self._swatch_panel)   # index 0
        self._stack.addWidget(self._slider_panel)   # index 1
        right_lay.addWidget(self._stack, stretch=1)

        root.addWidget(right, stretch=1)

        # Signals
        self._swatch_panel.colors_changed.connect(self._on_colors_changed)
        self._slider_panel.colors_changed.connect(self._on_colors_changed)
        self._btn_swatch.clicked.connect(lambda: self._switch_panel(0))
        self._btn_slider.clicked.connect(lambda: self._switch_panel(1))
        self._btn_settings.clicked.connect(lambda: SettingsDialog(self).exec())

        self._switch_panel(0)

    # ── Panel switch ─────────────────────────────────────────
    def _switch_panel(self, index: int):
        self._stack.setCurrentIndex(index)
        self._btn_swatch.setProperty("active", index == 0)
        self._btn_slider.setProperty("active", index == 1)
        for btn in (self._btn_swatch, self._btn_slider):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Color change from either panel ───────────────────────
    def _on_colors_changed(self, base: str, accent: str, highlight: str):
        self._current_colors = (base, accent, highlight)
        self._sidebar._preview.update_colors(base, accent, highlight)

    # ── Preset list → load into active panel ─────────────────
    def _on_preset_selected(self, preset: dict):
        b, a, h = preset["base"], preset["accent"], preset["highlight"]
        self._current_colors = (b, a, h)
        self._swatch_panel.set_base_colors(b, a, h)
        self._slider_panel.set_base_colors(b, a, h)

    # ── Apply from sidebar ────────────────────────────────────
    def _on_preset_applied(self, preset: dict):
        b, a, h = preset["base"], preset["accent"], preset["highlight"]
        cmap = generate_color_map(b, a, h)
        clrx_writer.write_clrx(cmap, theme_type=preset.get("theme_type", 0))
        clrx_writer.apply_to_max()

    # ── Save current colors as new preset ────────────────────
    def _on_save_requested(self, name: str):
        b, a, h = self._current_colors
        self._sidebar.do_save(name, b, a, h, theme_type=0)
