# Changelog

All notable changes to 3ds Max Themes Manager are documented here.

---

##  [0.0.3] - 07-31-2026 public release

### Added
- `get_max_enu_dir()` in `clrx_writer.py` — detects the ENU appdata path of the currently running Max version via `pymxs.pathConfig`
- Per-version data isolation: `last_applied.json` and `user_presets.json` are now saved inside each Max version's own ENU folder (`...\3dsMax\<VERSION>\ENU\MaxThemesManager\`), 
- Shared fallback path (`%APPDATA%\MaxThemesManager`) is still used when running outside of Max (standalone / testing)

### Fixed
- `clrx_writer.py` — replaced unsafe `tempfile.mktemp()` (race condition) with `tempfile.mkstemp()` for both the temp XAML and the elevated helper script
- `clrx_writer.py` — paths in the admin helper script are now escaped with `json.dumps()` instead of raw f-string interpolation, preventing code injection when paths contain quotes or backslashes
- `clrx_writer.apply_editor_properties()` — no longer writes to all installed Max versions; writes only to the currently running version
- `theme_engine.py` — cube root in OKLCH conversion changed from `** 0.3333333` to `** (1/3)` for full floating-point precision
- `theme_engine.py` — removed duplicate assignment of `m[17408]` (Unselected Tabs) that was overriding the correct value with an incorrect one
- `ui/main_window.py` — `theme_type` is now read from the active preset instead of being hardcoded to `0`, so light themes restore correctly on next Max launch
- `ui/swatch_tab.py` — `write_clrx()` now passes the correct `theme_type` (derived from base color luminance) instead of using the default `0`
- `ui/slider_tab.py` — same fix as swatch tab; also removed the unused `SliderTab` alias

---

## [0.0.2] - Initial public release

### Added
- OKLCH-based color engine (`theme_engine.py`) with full sRGB ↔ OKLCH conversion (no external dependencies)
- `generate_color_map()` — derives all 3ds Max UI color IDs from three base colors (base, accent, highlight), supporting both dark and light themes
- `clrx_writer.py` — reads, merges, and writes `MaxStartUI.clrx`; applies theme live via `colorMan` MAXScript API
- `clrx_writer.apply_listener_colors()` — sets MAXScript Listener and MacroRecorder colors via `pymxs` globals
- `clrx_writer.apply_editor_properties()` — merges syntax highlight colors into `MXS_EditorUser.properties` (Python and MAXScript lexers)
- `clrx_writer.apply_ribbon_theme()` — patches `CustomRibbonTheme.xaml` via regex; uses UAC elevation for write access to Program Files
- `clrx_writer.save_listener_startup_script()` — generates a `.ms` startup script so listener and title bar colors are restored on Max relaunch
- Windows 11 DWM title bar coloring (`ui/main_window.py`) — sets caption and text color on all visible Max windows via `DwmSetWindowAttribute`
- Swatches panel (`ui/swatch_tab.py`) — three color pickers (Base / Accent / Highlight) with live-updating read-only color swatches grouped by UI area
- Sliders panel (`ui/slider_tab.py`) — OKLCH H/C/L sliders with gradient-painted tracks and live hex preview
- Preset sidebar (`ui/preset_sidebar.py`) — built-in and user preset list with dot icons, preview strip, Apply and Save As buttons, right-click delete for user presets
- Settings dialog (`ui/settings_dialog.py`)
- 10 built-in presets: Max Dark, Dark Blue, Dark Warm, Slate, Light, Light Silver, Light Sand, Light Mint, Light Lavender, Midnight Purple
- Hot-reload support in `main.py` — clears all cached modules before reimport
- Dockable `QDockWidget` integration when running inside 3ds Max via `qtmax`; falls back to standalone window for testing
- `MABThemsManger.bundle` package structure with `PackageContents.xml`, MCR macro, and startup script for automatic loading
