"""
Preset sidebar — vertical list of presets (built-in + user).
Selecting a preset fires preview; Apply writes to Max; Save As persists a new preset.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QFrame, QInputDialog, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QBrush, QIcon, QPixmap

import presets as preset_data


def _make_dot_icon(colors: list[str], size=20) -> QIcon:
    """Create a small icon with 3 color circles side by side."""
    px = QPixmap(size * 3 + 4, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    for i, c in enumerate(colors):
        p.setBrush(QBrush(QColor(c)))
        p.setPen(Qt.NoPen)
        p.drawEllipse(i * (size + 2), 1, size - 2, size - 2)
    p.end()
    return QIcon(px)


class PreviewStrip(QFrame):
    """Shows 3 color swatches (Base/Accent/Highlight) for the selected preset."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewStrip")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(8)

        self._swatches = {}
        for key, label in (("base", "Base"), ("accent", "Accent"), ("highlight", "Highlight")):
            wrap = QVBoxLayout()
            wrap.setSpacing(3)
            swatch = QWidget()
            swatch.setFixedSize(24, 24)
            swatch.setObjectName("PreviewSwatch")
            wrap.addWidget(swatch, alignment=Qt.AlignHCenter)
            lbl = QLabel(label)
            lbl.setObjectName("DotLabel")
            lbl.setAlignment(Qt.AlignHCenter)
            wrap.addWidget(lbl)
            lay.addLayout(wrap)
            self._swatches[key] = swatch
        lay.addStretch()

    def update_colors(self, base: str, accent: str, highlight: str):
        data = {"base": base, "accent": accent, "highlight": highlight}
        for key, widget in self._swatches.items():
            c = data[key]
            widget.setStyleSheet(
                f"background:{c}; border-radius:3px;"
                " border:1px solid rgba(255,255,255,0.15);"
            )


class PresetSidebar(QWidget):
    """
    Left-side preset list.
    preset_selected(dict)  — emitted when user clicks a preset (for live preview in right panel)
    preset_applied(dict)   — emitted when Apply is clicked
    """
    preset_selected = Signal(dict)
    preset_applied  = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._presets: list[dict] = []
        self._current: dict | None = None
        self._build()
        self._refresh_list()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 10, 8, 10)
        lay.setSpacing(8)

        title = QLabel("Presets")
        title.setObjectName("SidebarTitle")
        lay.addWidget(title)

        self._list = QListWidget()
        self._list.setObjectName("PresetList")
        self._list.setIconSize(QSize(62, 16))
        self._list.setSpacing(2)
        self._list.currentRowChanged.connect(self._on_row_changed)
        self._list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        lay.addWidget(self._list, stretch=1)

        self._preview = PreviewStrip()
        lay.addWidget(self._preview)

        apply_btn = QPushButton("Apply to Max")
        apply_btn.setObjectName("ApplyButton")
        apply_btn.setFixedHeight(30)
        apply_btn.clicked.connect(self._apply)
        lay.addWidget(apply_btn)

        save_btn = QPushButton("Save as Preset...")
        save_btn.setFixedHeight(28)
        save_btn.clicked.connect(self._save_as)
        lay.addWidget(save_btn)

    def _refresh_list(self):
        self._presets = preset_data.load_all_presets()
        prev_name = self._current["name"] if self._current else None
        self._list.blockSignals(True)
        self._list.clear()
        for p in self._presets:
            icon = _make_dot_icon([p["base"], p["accent"], p["highlight"]])
            item = QListWidgetItem(icon, p["name"])
            if p.get("user"):
                item.setForeground(QColor("#aaaadd"))
            self._list.addItem(item)
        self._list.blockSignals(False)

        # Re-select previously selected
        target_row = 0
        if prev_name:
            for i, p in enumerate(self._presets):
                if p["name"] == prev_name:
                    target_row = i
                    break
        self._list.setCurrentRow(target_row)

    def _on_row_changed(self, row: int):
        if row < 0 or row >= len(self._presets):
            return
        self._current = self._presets[row]
        p = self._current
        self._preview.update_colors(p["base"], p["accent"], p["highlight"])
        self.preset_selected.emit(p)

    def _apply(self):
        if self._current:
            self.preset_applied.emit(self._current)

    def _save_as(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        # get current colors from parent window via signal chain
        self.save_requested.emit(name)

    def _on_context_menu(self, pos):
        item = self._list.itemAt(pos)
        if not item:
            return
        row = self._list.row(item)
        p = self._presets[row]
        if not p.get("user"):
            return
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Preset")
        action = menu.exec(self._list.mapToGlobal(pos))
        if action == delete_action:
            reply = QMessageBox.question(
                self, "Delete", f'Delete preset "{p["name"]}"?',
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                preset_data.delete_user_preset(p["name"])
                self._refresh_list()

    # Extra signal — main_window connects this to provide current colors
    save_requested = Signal(str)

    def do_save(self, name: str, base: str, accent: str, highlight: str, theme_type: int = 0):
        """Called by main_window after providing current colors."""
        preset_data.save_user_preset(name, base, accent, highlight, theme_type)
        self._refresh_list()
