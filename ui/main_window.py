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
from theme_engine import generate_color_map, _shift, _is_dark, _contrast_text


def build_stylesheet(base: str, accent: str, highlight: str) -> str:
    """Generate a fully adaptive QSS that works for both dark and light themes."""
    dark = _is_dark(base)
    s = 1 if dark else -1   # sign: positive shifts go lighter in dark, darker in light

    text        = _contrast_text(base)
    text_muted  = _shift(base, dL=s*0.28, scaleC=0.04)
    text_subtle = _shift(base, dL=s*0.18, scaleC=0.02)

    sidebar_bg  = _shift(base, dL=s*(-0.02))
    sidebar_bdr = _shift(base, dL=s*0.09)

    item_hover  = _shift(base, dL=s*0.07)
    sel_bg      = _shift(accent, dL=-0.28 if dark else 0.32, scaleC=0.3)
    sel_text    = _contrast_text(sel_bg)

    strip_bg    = _shift(base, dL=s*0.05)
    strip_bdr   = _shift(base, dL=s*0.10)

    bar_bg      = _shift(base, dL=s*(-0.06))
    bar_bdr     = _shift(base, dL=s*0.08)

    tog_bg      = _shift(base, dL=s*(-0.03))
    tog_bdr     = _shift(base, dL=s*0.10)
    tog_act     = _shift(accent, dL=-0.25 if dark else 0.30, scaleC=0.32)
    tog_act_t   = _contrast_text(tog_act)

    frame_bg    = _shift(base, dL=s*0.04)
    frame_bdr   = _shift(base, dL=s*0.09)
    group_bg    = _shift(base, dL=s*0.02)

    groove      = _shift(base, dL=s*0.13)
    handle      = _shift(base, dL=s*0.38, scaleC=0.04)

    sc_h        = _shift(base, dL=s*0.22, scaleC=0.0)
    sc_hov      = _shift(base, dL=s*0.36, scaleC=0.0)

    gen_bg      = _shift(base, dL=s*0.07)
    gen_hvr     = _shift(base, dL=s*0.13)
    gen_prs     = _shift(base, dL=s*0.02)
    gen_bdr     = _shift(base, dL=s*0.11)

    apply_txt   = _contrast_text(accent)
    apply_hvr   = _shift(accent, dL=-0.08)
    apply_prs   = _shift(accent, dL=-0.16)

    prev_bdr    = _shift(base, dL=s*0.12)

    return f"""
QWidget {{
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    color: {text};
    background: {base};
}}

/* ── Sidebar ─────────────────────────────────────── */
QWidget#Sidebar {{
    background: {sidebar_bg};
    border-right: 1px solid {sidebar_bdr};
}}
QLabel#SidebarTitle {{
    color: {text_subtle};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 0;
}}
QListWidget#PresetList {{
    background: transparent;
    border: none;
    outline: none;
    color: {text};
}}
QListWidget#PresetList::item {{
    padding: 6px 8px;
    border-radius: 4px;
    margin: 1px 2px;
    color: {text_muted};
}}
QListWidget#PresetList::item:selected {{
    background: {sel_bg};
    color: {sel_text};
}}
QListWidget#PresetList::item:hover:!selected {{
    background: {item_hover};
}}

/* ── Preview strip ───────────────────────────────── */
QFrame#PreviewStrip {{
    background: {strip_bg};
    border: 1px solid {strip_bdr};
    border-radius: 5px;
}}
QLabel#DotLabel {{ color: {text_subtle}; font-size: 10px; }}

/* ── Toggle bar ──────────────────────────────────── */
QWidget#ToggleBar {{
    background: {bar_bg};
    border-bottom: 1px solid {bar_bdr};
}}

/* ── Toggle buttons ──────────────────────────────── */
QPushButton#ToggleBtn {{
    background: {tog_bg};
    color: {text_subtle};
    border: 1px solid {tog_bdr};
    border-radius: 3px;
    padding: 4px 0;
    font-size: 12px;
}}
QPushButton#ToggleBtn:hover {{ color: {text}; }}
QPushButton#ToggleBtn[active=true] {{
    background: {tog_act};
    color: {tog_act_t};
    border-color: {accent};
}}

/* ── Settings button ─────────────────────────────── */
QPushButton#SettingsBtn {{
    background: transparent;
    color: {text_subtle};
    border: none;
    padding: 4px 8px;
    font-size: 12px;
}}
QPushButton#SettingsBtn:hover {{ color: {text_muted}; }}

/* ── Settings dialog ─────────────────────────────── */
QGroupBox {{
    color: {text_subtle};
    font-size: 11px;
    font-weight: 600;
    border: 1px solid {frame_bdr};
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 6px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}
QLabel#DialogProductTitle {{
    color: {text};
    font-size: 14px;
    font-weight: 700;
}}
QPushButton#GithubBtn {{
    background: #24292e;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px 12px;
    font-weight: 600;
}}
QPushButton#GithubBtn:hover {{ background: #2f363d; }}
QPushButton#PaypalBtn {{
    background: #003087;
    color: #ffffff;
    border: 1px solid #0070ba;
    border-radius: 4px;
    padding: 4px 12px;
    font-weight: 600;
}}
QPushButton#PaypalBtn:hover {{ background: #0070ba; }}

/* ── Apply button ────────────────────────────────── */
QPushButton#ApplyButton {{
    background: {accent};
    color: {apply_txt};
    border: none;
    border-radius: 4px;
    padding: 0 14px;
    font-weight: 600;
}}
QPushButton#ApplyButton:hover  {{ background: {apply_hvr}; }}
QPushButton#ApplyButton:pressed{{ background: {apply_prs}; }}

/* ── Generic buttons ─────────────────────────────── */
QPushButton {{
    background: {gen_bg};
    color: {text_muted};
    border: 1px solid {gen_bdr};
    border-radius: 3px;
    padding: 3px 10px;
}}
QPushButton:hover  {{ background: {gen_hvr}; color: {text}; }}
QPushButton:pressed{{ background: {gen_prs}; }}

/* ── Scrollbars ──────────────────────────────────── */
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{
    background: transparent; width: 8px; border: none; margin: 2px 0;
}}
QScrollBar::handle:vertical {{
    background: {sc_h}; border-radius: 4px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {sc_hov}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

/* ── Color picker row ────────────────────────────── */
QFrame#PickerFrame   {{ background: {frame_bg}; border: 1px solid {frame_bdr}; border-radius: 5px; }}
QFrame#ColorPickerRow{{ background: transparent; }}
QLabel#PickerLabel   {{ color: {text_muted}; font-size: 12px; }}
QLabel#HexLabel      {{ color: {text_subtle}; font-size: 11px; font-family: "Consolas", monospace; }}

/* ── Read-only swatches ──────────────────────────── */
QFrame#SwatchGroup {{
    background: {group_bg};
    border: 1px solid {frame_bdr};
    border-radius: 4px;
}}
QLabel#GroupTitle  {{ color: {text_subtle}; font-size: 11px; font-weight: 600; }}
QLabel#SwatchLabel {{ color: {text_subtle}; font-size: 9px; }}
QLabel#SectionLabel{{ color: {text_subtle}; font-size: 11px; font-weight: 600; margin-top: 4px; }}

/* ── MiniPreview ─────────────────────────────────── */
QFrame#MiniPreview {{ border-radius: 5px; border: 1px solid {prev_bdr}; }}

/* ── OKLCH sliders ───────────────────────────────── */
QFrame#ColorRow {{
    background: {group_bg};
    border: 1px solid {frame_bdr};
    border-radius: 5px;
}}
QLabel#RowTitle   {{ color: {text}; font-weight: 600; font-size: 13px; }}
QLabel#SliderLabel{{ color: {text_subtle}; font-size: 11px; min-width: 62px; }}
QLabel#SliderValue{{ color: {text_subtle}; font-size: 11px; }}
QSlider::groove:horizontal {{
    height: 4px; background: {groove}; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {handle}; border: 1px solid {text_subtle};
    width: 12px; height: 12px; margin: -4px 0; border-radius: 6px;
}}
QSlider::handle:horizontal:hover {{ background: {text}; }}
"""


class ThemeMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3ds Max Themes Manager")
        self.setMinimumSize(640, 540)
        self._current_colors = ("#1c1c1c", "#5f8ac1", "#ffb100")
        self._current_stylesheet = ""
        self._apply_stylesheet()
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
        self._btn_settings.clicked.connect(self._open_settings)

        self._switch_panel(0)

    def _apply_stylesheet(self):
        b, a, h = self._current_colors
        self._current_stylesheet = build_stylesheet(b, a, h)
        self.setStyleSheet(self._current_stylesheet)

    def _open_settings(self):
        SettingsDialog(self, stylesheet=self._current_stylesheet).exec()

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
        self._apply_stylesheet()
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
