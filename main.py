
import sys
import os
import importlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# ── Hot-reload: drop all cached modules from this project ──────────────────
_MODULES_TO_CLEAR = [
    "constants",
    "theme_engine",
    "clrx_writer",
    "presets",
    "ui",
    "ui.main_window",
    "ui.preset_sidebar",
    "ui.swatch_tab",
    "ui.slider_tab",
    "ui.settings_dialog",
]
for _mod in _MODULES_TO_CLEAR:
    if _mod in sys.modules:
        del sys.modules[_mod]

from PySide6.QtWidgets import QDockWidget, QApplication
from PySide6.QtCore import Qt

from ui.main_window import ThemeMainWindow

_dock_ref = None  # keep alive


def show_theme_customizer():
    global _dock_ref

    # Close existing window if open
    if _dock_ref is not None:
        try:
            _dock_ref.close()
        except Exception:
            pass
        _dock_ref = None

    try:
        from qtmax import GetQMaxMainWindow
        main_win = GetQMaxMainWindow()
        if main_win:
            dock = QDockWidget("3ds Max Themes Manager", main_win)
            dock.setObjectName("MaxThemesManager_dock")
            dock.setAllowedAreas(Qt.AllDockWidgetAreas)
            widget = ThemeMainWindow()
            dock.setWidget(widget)
            main_win.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.setFloating(True)
            dock.resize(540, 580)
            dock.show()
            _dock_ref = dock
            return dock
    except ImportError:
        pass

    # Fallback: standalone window (for testing outside Max)
    app = QApplication.instance() or QApplication(sys.argv)
    win = ThemeMainWindow()
    win.show()
    _dock_ref = win
    return win


if __name__ == "__main__":
    show_theme_customizer()
