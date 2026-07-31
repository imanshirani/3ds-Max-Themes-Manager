# 3ds Max Themes Manager

[![Donate ❤️](https://img.shields.io/badge/Donate-PayPal-00457C?style=flat-square&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4)
![3dsmax](https://img.shields.io/badge/Autodesk-3ds%20Max-0696D7?style=flat-square&logo=autodesk)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat-square&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

A Python + PySide6 tool for **3ds Max 2025–2027** that lets you create and apply fully custom UI color themes — no manual XML editing required.

Pick just **3 colors** (Base, Accent, Highlight) and the tool automatically derives all UI color IDs using perceptually-uniform **OKLCH color math**, then writes them directly to your `MaxStartUI.clrx` and reloads the theme live — no restart needed.

![screenshot](etc/screen.png)

---

## ✨ Features

- **3-color workflow** — choose Base, Accent, and Highlight; everything else is calculated automatically
- **Live preview** — see a mock UI preview update in real time as you pick colors
- **Two editing modes** — Color Swatches (click-to-pick) or OKLCH Sliders (Hue / Chroma / Lightness)
- **Built-in presets** — Max Dark, Dark Blue, Dark Warm, Slate, Midnight Purple + 5 Light themes
- **User presets** — save, name, and reuse your own themes (persisted to `%APPDATA%`)
- **Apply live** — writes to `.clrx` and calls `colorMan.repaintUI()` inside running Max — no restart
- **Ribbon theming** — updates `CustomRibbonTheme.xaml` via admin elevation (restart required)
- **MAXScript Editor** — syntax highlighting colors adapt to your theme via `MXS_EditorUser.properties`
- **Listener colors** — MacroRecorder and Scripting Listener backgrounds match your theme
- **Title bar** — all Max window title bars colored via Windows 11 DWM API
- **Startup persistence** — all extra colors (title bar, listener) auto-restore on Max launch
- **Bundle install** — ships as a `.bundle` package; appears under the **MYARTSBOX** menu automatically
- **Adaptive UI** — the tool's own interface adapts its colors to the active theme

---

## Requirements

| | |
|---|---|
| **3ds Max** | 2025 – 2027 |
| **OS** | Windows 10/11 64-bit |
| **Python** | 3.11 (bundled with Max — no separate install) |
| **PySide6** | 6.5.x (bundled with Max — no separate install) |

> **Note:** Title bar coloring requires Windows 11 21H2 or later. On Windows 10 it is silently skipped.

---

## 📦 Installation

1. Download the latest release and extract it.
2. Copy `MABThemsManger.bundle` to:
   - `C:\ProgramData\Autodesk\ApplicationPlugins\` *(all users)*
3. Restart 3ds Max.
4. Go to the **MYARTSBOX** menu → click **3ds Max Themes Manager**.

---

## Usage

### Swatches Panel
Click any of the three color squares to open a color picker dialog. The read-only swatch grid below updates live to show all generated UI colors.

### Sliders Panel
Fine-tune each color using individual **Hue**, **Chroma**, and **Lightness** sliders in OKLCH space — giving smooth, perceptually accurate adjustments.

### Presets Sidebar
- **Click** a preset to preview it in both panels
- **Apply to Max** — writes and reloads the selected preset immediately
- **Save as Preset...** — saves your current colors as a named preset
- Right-click a user preset to **Delete** it

### Settings
Click **⚙ Settings** in the top bar to view version info and links.

### Apply to Max
Clicking **Apply to 3ds Max** does the following in one shot:

1. Writes all ~40+ color IDs to `MaxStartUI.clrx` and reloads via `colorMan`
2. Sets MAXScript Listener and MacroRecorder background/text colors
3. Saves a startup script so listener colors restore on next Max launch
4. Updates syntax highlighting in `MXS_EditorUser.properties` (re-open Script Editor to apply)
5. Colors all Max window title bars via Windows 11 DWM API
6. Updates `CustomRibbonTheme.xaml` via admin elevation prompt — **restart Max to apply ribbon changes**

---

## How It Works

Instead of requiring users to know 40+ color IDs, the tool derives them all from 3 seed colors using **OKLCH** (a perceptually uniform color space). Shifts in lightness, chroma, and hue are applied in the correct direction for both dark and light themes, so the result is always readable and harmonious across the entire Max interface.

The tool covers:
- Appearance (backgrounds, buttons, borders, text, tooltips)
- Trackbar and time slider
- Viewports
- Rollup panels
- Tabs and ribbon
- MAXScript Editor syntax highlighting
- Scripting Listener / MacroRecorder
- Slate Material Editor
- Scene Explorer rows

---

## Project Structure

```
MABThemsManger.bundle/
└── Contents/
    ├── main.py                   # entry point
    ├── theme_engine.py           # OKLCH color derivation
    ├── clrx_writer.py            # clrx, ribbon XAML, editor properties, listener
    ├── presets.py                # built-in + user preset management
    ├── constants.py              # product metadata
    ├── mab.ThemesManager.mcr     # Max macroScript
    ├── mab.ThemesManager.ms      # MAXScript launcher
    ├── mab.ThemesManager.mnx     # menu registration
    └── ui/
        ├── main_window.py        # adaptive main window
        ├── swatch_tab.py         # color picker panel
        ├── slider_tab.py         # OKLCH slider panel
        ├── preset_sidebar.py     # preset list sidebar
        └── settings_dialog.py    # about / settings dialog
```

---

## License

MIT License — free to use, modify, and distribute.

---

## Support

If this tool saves you time, consider supporting its development:

[![PayPal](https://img.shields.io/badge/Donate-PayPal-0070ba?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4)

---

Developed by **Iman Shirani** — [MYARTSBOX](https://github.com/imanshirani)
