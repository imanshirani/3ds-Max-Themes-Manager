
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def _hover_of(hex_val: str) -> str:
    """Derive a hover color: slightly lighter for dark colors, slightly darker for light ones."""
    from theme_engine import _is_dark, _shift
    dL = 0.06 if _is_dark(hex_val) else -0.06
    return _shift(hex_val, dL=dL)

def get_max_enu_dir() -> str:
    """Return the ENU appdata dir for the currently running Max version.

    Example: C:\\Users\\...\\AppData\\Local\\Autodesk\\3dsMax\\2024 - 64bit\\ENU
    Returns empty string when not running inside Max.
    """
    try:
        from pymxs import runtime as rt
        startup = rt.pathConfig.GetDir(rt.Name("userStartupScripts"))
        # startup: ...3dsMax\<VERSION>\ENU\scripts\startup
        parts = startup.replace("/", "\\").split("\\")
        idx = next((i for i, p in enumerate(parts) if p.lower() == "3dsmax"), -1)
        if idx >= 0 and idx + 2 < len(parts):
            return "\\".join(parts[: idx + 3])   # up to ENU
    except Exception:
        pass
    return ""


def _find_clrx_path() -> str:
    """Find MaxStartUI.clrx for the running Max version dynamically."""
    try:
        from pymxs import runtime as rt
        max_data = rt.pathConfig.GetDir(rt.Name("maxData"))
        candidate = os.path.join(max_data, "en-US", "UI", "MaxStartUI.clrx")
        if os.path.isfile(candidate):
            return candidate
    except Exception:
        pass
    # Fallback: scan local appdata for any installed version
    local = os.environ.get("LOCALAPPDATA", "")
    max_root = os.path.join(local, "Autodesk", "3dsMax")
    if os.path.isdir(max_root):
        for entry in sorted(os.listdir(max_root), reverse=True):
            candidate = os.path.join(max_root, entry, "ENU", "en-US", "UI", "MaxStartUI.clrx")
            if os.path.isfile(candidate):
                return candidate
    return ""


CLRX_PATH = _find_clrx_path()


def read_clrx(path: str = CLRX_PATH) -> dict:
    """Returns {color_id: {value, name, disabled?, hover?}}"""
    if not os.path.isfile(path):
        return {}
    tree = ET.parse(path)
    root = tree.getroot()
    colors = {}
    for cat in root.iter("category"):
        for el in cat.iter("color"):
            cid = int(el.get("id", "0"))
            colors[cid] = {
                "name": el.get("name", ""),
                "value": el.get("value", "#000000"),
                "disabled": el.get("disabled"),
                "hover": el.get("hover"),
            }
    return colors


def write_clrx(color_map: dict, path: str = CLRX_PATH, theme_type: int = 0):
    """
    Merge color_map into the existing clrx file and save.
    color_map: {color_id: hex_string}
    """
    if not os.path.isfile(path):
        _write_minimal_clrx(color_map, path, theme_type)
        return

    tree = ET.parse(path)
    root = tree.getroot()

    # Update appFrameColorTheme
    icon_scales = root.find("IconImageScales")
    if icon_scales is not None:
        theme_el = icon_scales.find("appFrameColorTheme")
        if theme_el is not None:
            theme_el.set("value", str(theme_type))

    # Build lookup of existing elements
    existing: dict[int, ET.Element] = {}
    for el in root.iter("color"):
        try:
            existing[int(el.get("id", ""))] = el
        except ValueError:
            pass

    for cid, hex_val in color_map.items():
        if cid in existing:
            el = existing[cid]
            el.set("value", hex_val)
            # Update hover attribute only if it already exists in the file
            if el.get("hover") is not None:
                el.set("hover", _hover_of(hex_val))

    # Pretty-print
    raw = ET.tostring(root, encoding="unicode")
    pretty = minidom.parseString(raw).toprettyxml(indent="    ")
    # Remove the extra <?xml...?> line minidom adds
    lines = pretty.split("\n")
    if lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="utf-8" ?>'
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _write_minimal_clrx(color_map: dict, path: str, theme_type: int):
    """Create a minimal .clrx from scratch when none exists."""
    lines = ['<?xml version="1.0" encoding="utf-8" ?>', "<ADSK_CLR>"]
    lines += [
        "    <IconImageScales>",
        f'        <appFrameColorTheme value="{theme_type}" />',
        "    </IconImageScales>",
        '    <CustomColors>',
        '        <category name="Appearance">',
    ]
    for cid, val in color_map.items():
        lines.append(f'            <color id="{cid}" value="{val}" name="Custom" />')
    lines += ["        </category>", "    </CustomColors>", "</ADSK_CLR>"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def apply_to_max(path: str = CLRX_PATH):
    """Reload the color file inside 3ds Max."""
    try:
        from pymxs import runtime as rt
        rt.colorMan.loadColorFile(path)
        rt.colorMan.reInitIcons()
        rt.colorMan.repaintUI(True)
    except Exception as e:
        print(f"[ThemesManager] apply_to_max: {e}")


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def apply_listener_colors(base: str, font_size: int = 0):
    """Set MAXScript Listener/MacroRecorder colors via MAXScript globals."""
    try:
        from pymxs import runtime as rt
        from theme_engine import _shift, _contrast_text

        listener_bg  = _shift(base, dL=0.02)
        macro_bg     = _shift(base, dL=-0.02)
        text_col     = _contrast_text(base)
        msg_col      = _shift(base, dL=0.45, scaleC=0.05)
        output_col   = _shift(base, dL=0.35, scaleC=0.05)

        lr, lg, lb   = _hex_to_rgb(listener_bg)
        mr, mg, mb   = _hex_to_rgb(macro_bg)
        tr, tg, tb   = _hex_to_rgb(text_col)
        otr, otg, otb = _hex_to_rgb(output_col)
        msr, msg_, msb = _hex_to_rgb(msg_col)

        # These are MAXScript global variables — set directly
        rt.listenerBackgroundColor             = rt.Color(lr, lg, lb)
        rt.macroRecorderBackgroundColor        = rt.Color(mr, mg, mb)
        rt.inputTextColor                      = rt.Color(tr, tg, tb)
        rt.macroRecorderTextColor              = rt.Color(tr, tg, tb)
        rt.outputTextColor                     = rt.Color(otr, otg, otb)
        rt.messageTextColor                    = rt.Color(msr, msg_, msb)

        if font_size > 0:
            rt.editorFontSize = font_size

    except Exception as e:
        print(f"[ThemesManager] apply_listener_colors: {e}")


_MARKER_START = "# mab.ThemesManager_start"
_MARKER_END   = "# mab.ThemesManager_end"


def _build_editor_block(base: str, accent: str, highlight: str) -> str:
    from theme_engine import _shift, _contrast_text, _is_dark
    dark    = _is_dark(base)
    s       = 1 if dark else -1
    bg      = _shift(base, dL=s*(-0.02))
    fg      = _contrast_text(bg)
    comment = _shift(bg, dL=s*0.22, scaleC=0.06)    # relative to bg, same direction
    keyword = _shift(accent, dL=s*0.12)
    string_ = _shift(highlight, dL=s*0.05)
    number  = _shift(highlight, dH=30, dL=s*0.08)
    func_   = _shift(accent, dH=-20, dL=s*0.18)
    op      = _shift(accent, dL=s*0.15)
    sel_bg  = _shift(accent, dL=-0.2, scaleC=0.4)
    sel_fg  = _contrast_text(sel_bg)
    line_bg = _shift(base, dL=s*0.04)
    ln_fg   = _shift(bg, dL=s*0.28, scaleC=0.04)
    err_bg  = _shift(accent, dH=30, dL=-0.3, scaleC=0.2)

    return "\n".join([
        _MARKER_START,
        f"selection.fore={sel_fg}",
        f"selection.back={sel_bg}",
        f"selection.alpha=80",
        f"caret.period=400",
        f"caret.width=2",
        f"caret.fore={fg}",
        f"caret.line.back={line_bg}",
        f"caret.line.back.alpha=50",
        f"style.*.33=back:{bg},$(font.small),fore:{ln_fg}",
        f"fold.margin.colour={bg}",
        f"fold.margin.highlight.colour={bg}",
        "",
        "# ── Python ──────────────────────────────────",
        f"style.python.32=back:{bg}",
        f"style.python.0=fore:{_shift(highlight, dH=10)}",
        f"style.python.1=fore:{comment}",
        f"style.python.2=fore:{op}",
        f"style.python.3=fore:{string_}",
        f"style.python.4=fore:{string_},$(font.monospace)",
        f"style.python.5=fore:{keyword},bold",
        f"style.python.6=fore:{string_}",
        f"style.python.7=fore:{string_}",
        f"style.python.8=fore:{func_},bold",
        f"style.python.9=fore:{func_},bold",
        f"style.python.10=fore:{fg},bold",
        f"style.python.11=fore:{fg}",
        f"style.python.12=fore:{comment}",
        f"style.python.13=fore:{fg},$(font.monospace),back:{err_bg},eolfilled",
        f"style.python.14=fore:{op}",
        f"style.python.15=fore:{number}",
        "",
        "# ── MAXScript ───────────────────────────────",
        f"style.MAXScript.32=$(font.base),fore:{fg},back:{bg}",
        f"style.MAXScript.0=fore:{func_}",
        f"style.MAXScript.1=fore:{comment}",
        f"style.MAXScript.2=fore:{comment}",
        f"style.MAXScript.3=fore:{op}",
        f"style.MAXScript.4=fore:{string_}",
        f"style.MAXScript.5=fore:{string_}",
        f"style.MAXScript.6=fore:{string_},back:{err_bg},eolfilled",
        f"style.MAXScript.7=fore:{fg}",
        f"style.MAXScript.8=fore:{fg},bold",
        f"style.MAXScript.9=fore:{func_}",
        f"style.MAXScript.10=fore:{number}",
        f"style.MAXScript.11=fore:{string_},$(font.monospace)",
        f"style.MAXScript.12=fore:{keyword},bold",
        f"style.MAXScript.13=fore:{op},bold",
        f"style.MAXScript.14=fore:{op}",
        f"style.MAXScript.15=fore:{op}",
        f"style.MAXScript.16=fore:{op}",
        f"style.MAXScript.17=fore:{op}",
        f"style.MAXScript.18=fore:{func_},italics",
        f"style.MAXScript.19=fore:{func_},italics",
        f"style.MAXScript.20=fore:{op},italics",
        f"style.MAXScript.21=fore:{op},italics",
        f"style.MAXScript.22=fore:{op}",
        f"style.MAXScript.23=fore:{op},bold,italics",
        f"style.MAXScript.24=fore:{op},italics",
        f"style.MAXScript.34=fore:{keyword},bold",
        f"style.MAXScript.35=fore:{keyword},bold",
        f"style.MAXScript.37=fore:{keyword}",
        _MARKER_END,
    ])


def _merge_properties(existing: str, new_block: str) -> str:
    """Replace our marker block if present, otherwise append it."""
    if _MARKER_START in existing:
        start = existing.index(_MARKER_START)
        end   = existing.index(_MARKER_END) + len(_MARKER_END)
        return existing[:start].rstrip("\n") + "\n" + new_block + "\n" + existing[end:].lstrip("\n")
    return existing.rstrip("\n") + "\n\n" + new_block + "\n"


def apply_editor_properties(base: str, accent: str, highlight: str):
    """Merge theme syntax colors into MXS_EditorUser.properties of the running Max version."""
    try:
        new_block = _build_editor_block(base, accent, highlight)
        enu_path  = get_max_enu_dir()
        if not enu_path:
            return
        out_path = os.path.join(enu_path, "MXS_EditorUser.properties")
        existing = ""
        if os.path.isfile(out_path):
            with open(out_path, "r", encoding="utf-8", errors="ignore") as f:
                existing = f.read()
        merged = _merge_properties(existing, new_block)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(merged)
        print(f"[ThemesManager] Editor properties written: {out_path}")
    except Exception as e:
        print(f"[ThemesManager] apply_editor_properties: {e}")


def _to_xaml_color(hex_color: str) -> str:
    """Convert #rrggbb to XAML #FFrrggbb format."""
    h = hex_color.lstrip("#").upper()
    return f"#FF{h}"


def apply_ribbon_theme(base: str, accent: str, highlight: str):
    """
    Write CustomRibbonTheme.xaml for all installed Max versions using regex.
    Backup original as .xaml.mab_backup, replace via elevated helper.
    """
    try:
        import os, tempfile, ctypes, re
        from theme_engine import _shift, _contrast_text, _is_dark

        dark = _is_dark(base)
        s    = 1 if dark else -1

        # ribbon area = slightly different from base
        ribbon_bg    = _shift(base, dL=s*0.06)
        panel_bg_t   = _shift(base, dL=s*0.08)
        panel_bg_b   = _shift(base, dL=s*0.04)
        # tab strip area
        tab_strip    = _shift(base, dL=s*0.12)
        tab_sel_t    = _shift(base, dL=s*0.20)
        tab_sel_b    = _shift(base, dL=s*0.14)
        tab_hover_t  = _shift(base, dL=s*0.16)
        tab_hover_b  = _shift(base, dL=s*0.12)
        # buttons
        btn_idle_t   = _shift(base, dL=s*0.14)
        btn_idle_b   = _shift(base, dL=s*0.08)
        btn_hover_t  = _shift(base, dL=s*0.22)
        btn_hover_b  = _shift(base, dL=s*0.16)
        btn_press_t  = _shift(accent, dL=-0.12, scaleC=0.6)
        btn_press_b  = _shift(accent, dL=-0.20, scaleC=0.6)
        btn_active_t = _shift(accent, dL=0.04)
        btn_active_b = _shift(accent, dL=-0.06)
        # text
        text_col     = _contrast_text(base)
        text_dim     = _shift(base, dL=s*0.38, scaleC=0.04)
        separator    = _shift(base, dL=s*0.18)
        panel_title  = _shift(base, dL=s*0.10)

        def xc(h): return _to_xaml_color(h)

        # Build all key variants (dark + light + LightTheme suffix)
        def make_solid(base_keys: dict) -> dict:
            result = {}
            for k, v in base_keys.items():
                result[k] = v
                result[k + "_Light"] = v
                result[k + "-LightTheme"] = v
            return result

        def make_gradient(base_keys: dict) -> dict:
            result = {}
            for k, v in base_keys.items():
                result[k] = v
                result[k + "_Light"] = v
                result[k + "-LightTheme"] = v
            return result

        # SolidColorBrush replacements — applied to both dark and light variants
        solid_replacements = make_solid({
            "RibbonTabBackgroundBrush":             xc(tab_strip),
            "RibbonTabItemForegroundBrush":         xc(text_dim),
            "RibbonTabItemSelectedForegroundBrush": xc(text_col),
            "RibbonTabItemRolloverForegroundBrush": xc(text_dim),
            "RibbonItemStyleTextForeground":        xc(text_col),
            "RibbonTextForeground":                 xc(text_col),
            "RibbonPanelTitleForeground":           xc(text_col),
            "RibbonSeparatorBrush":                 xc(separator),
            "RibbonArrowBrush":                     xc(text_col),
            "RibbonOverflowTabPanelForeground":     xc(text_col),
            "RibbonOverflowTabPanelBackground":     xc(tab_strip),
            "RibbonGalleryBackgroundFillBrush":     xc(panel_bg_t),
            "SliderTextBoxBackgroundBrush":         xc(btn_idle_t),
            "ComboBoxDropDownBackgroundBrush":      xc(btn_idle_t),
            "MenuItemListBoxBackgroundBrush":       xc(btn_idle_t),
            "DropDownListBoxBackgroundBrush":       xc(btn_idle_t),
            "SpinnerBackgroundBrush":               xc(btn_idle_t),
            "RibbonTextBoxBackground":              xc(btn_idle_t),
            "RibbonTextBoxForeground":              xc(text_col),
        })

        # Color key replacements
        color_key_replacements = {
            "RibbonPanelBackgroundColor_1":       xc(panel_bg_t),
            "RibbonPanelBackgroundColor_2":       xc(panel_bg_b),
            "RibbonPanelBackgroundColor_1_Light": xc(panel_bg_t),
            "RibbonPanelBackgroundColor_2_Light": xc(panel_bg_b),
        }

        # LinearGradientBrush: applied to dark + light variants
        gradient_replacements = make_gradient({
            "RibbonDarkThemePanelBackground":              (xc(panel_bg_t), xc(panel_bg_b)),
            "RibbonDarkThemePanelBackgroundVerticalLeft":  (xc(panel_bg_t), xc(panel_bg_b)),
            "RibbonDarkThemePanelBackgroundVerticalRight": (xc(panel_bg_t), xc(panel_bg_b)),
            "RibbonLightThemePanelBackground":             (xc(panel_bg_t), xc(panel_bg_b)),
            "RibbonLightThemePanelBackgroundVerticalLeft": (xc(panel_bg_t), xc(panel_bg_b)),
            "RibbonLightThemePanelBackgroundVerticalRight":(xc(panel_bg_t), xc(panel_bg_b)),
            "RibbonPanelSlideoutAreaBrushDefault":         (xc(panel_title), xc(panel_bg_b)),
            "RibbonItemStyleButtonBackgroundBrushIdle":    (xc(btn_idle_t), xc(btn_idle_b)),
            "RibbonButtonBackgroundBrushRollover":         (xc(btn_hover_t), xc(btn_hover_b)),
            "RibbonButtonBackgroundBrushPressed":          (xc(btn_press_t), xc(btn_press_b)),
            "RibbonTabItemBrushSelected":                  (xc(tab_sel_t), xc(tab_sel_b)),
            "RibbonTabItemBrushRollover":                  (xc(tab_hover_t), xc(tab_hover_b)),
            "RibbonPanelsBackgroundBrush":                 (xc(ribbon_bg), xc(ribbon_bg)),
            "RibbonListButtonBackgroundBrushRollover":     (xc(btn_idle_b), xc(btn_hover_t)),
        })

        prog = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        autodesk = os.path.join(prog, "Autodesk")
        xaml_files = []
        if os.path.isdir(autodesk):
            for entry in os.listdir(autodesk):
                xaml = os.path.join(autodesk, entry, "en-US", "UI", "CustomRibbonTheme.xaml")
                if os.path.isfile(xaml):
                    xaml_files.append(xaml)

        if not xaml_files:
            print("[ThemesManager] No CustomRibbonTheme.xaml found")
            return

        for xaml_path in xaml_files:
            with open(xaml_path, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = content

            # Replace SolidColorBrush Color attributes by key name
            for key, new_color in solid_replacements.items():
                new_content = re.sub(
                    rf'(x:Key="{re.escape(key)}"[^>]*Color=")[^"]*(")',
                    rf'\g<1>{new_color}\2',
                    new_content
                )

            # Replace <Color> values by key name
            for key, new_color in color_key_replacements.items():
                new_content = re.sub(
                    rf'(x:Key="{re.escape(key)}">)[^<]*(<)',
                    rf'\g<1>{new_color}\2',
                    new_content
                )

            # Replace LinearGradientBrush top+bottom colors by key name
            for key, (top, bot) in gradient_replacements.items():
                new_content = re.sub(
                    rf'(x:Key="{re.escape(key)}"[^>]*>[\s\S]*?GradientStop[^C]*Color=")[^"]*("[\s\S]*?GradientStop[^C]*Color=")[^"]*(")',
                    rf'\g<1>{top}\2{bot}\3',
                    new_content, count=1
                )

            # Replace active button gradient (accent)
            new_content = re.sub(
                r'(x:Key="RibbonButtonBackgroundBrushActive"[^>]*>[\s\S]*?GradientStop[^C]*Color=")[^"]*("[\s\S]*?GradientStop[^C]*Color=")[^"]*(")',
                rf'\g<1>{xc(btn_active_t)}\2{xc(btn_active_b)}\3',
                new_content, count=1
            )

            # Write to temp file (mkstemp avoids race condition)
            import json as _json
            tmp_fd, tmp = tempfile.mkstemp(suffix=".xaml")
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Helper script for admin copy
            bak_path = xaml_path + ".mab_backup"
            hlp_fd, helper = tempfile.mkstemp(suffix=".py")
            # Use json.dumps to safely escape all paths — avoids injection via backslash/quote
            with os.fdopen(hlp_fd, "w", encoding="utf-8") as f:
                f.write(
                    f"import shutil, os\n"
                    f"src = {_json.dumps(tmp)}\n"
                    f"dst = {_json.dumps(xaml_path)}\n"
                    f"bak = {_json.dumps(bak_path)}\n"
                    f"hlp = {_json.dumps(helper)}\n"
                    f"if not os.path.isfile(bak):\n"
                    f"    shutil.copy2(dst, bak)\n"
                    f"shutil.copy2(src, dst)\n"
                    f"os.remove(src)\n"
                    f"os.remove(hlp)\n"
                )

            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas",
                r"C:\Windows\System32\cmd.exe",
                f'/c python "{helper}"',
                None, 0
            )
            if result <= 32:
                print(f"[ThemesManager] Admin elevation failed (code {result})")
            else:
                print(f"[ThemesManager] Ribbon XAML updated: {xaml_path}")
                print("[ThemesManager] Restart 3ds Max to apply ribbon changes")

    except Exception as e:
        print(f"[ThemesManager] apply_ribbon_theme: {e}")


def save_listener_startup_script(base: str, font_size: int = 0):
    """Write startup script: listener colors + title bar restore on Max launch."""
    try:
        from pymxs import runtime as rt
        from theme_engine import _shift, _contrast_text

        listener_bg = _shift(base, dL=0.02)
        macro_bg    = _shift(base, dL=-0.02)
        text_col    = _contrast_text(base)
        msg_col     = _shift(base, dL=0.45, scaleC=0.05)
        output_col  = _shift(base, dL=0.35, scaleC=0.05)
        fg_col      = _contrast_text(base)

        br, bg_, bb = _hex_to_rgb(base)
        fr, fg_, fb = _hex_to_rgb(fg_col)

        def rgb(h):
            r, g, b = _hex_to_rgb(h)
            return f"(color {r} {g} {b})"

        lines = [
            "-- Auto-generated by 3ds Max Themes Manager",
            "",
            "-- Listener colors",
            f"listenerBackgroundColor          = {rgb(listener_bg)}",
            f"macroRecorderBackgroundColor     = {rgb(macro_bg)}",
            f"inputTextColor                   = {rgb(text_col)}",
            f"macroRecorderTextColor           = {rgb(text_col)}",
            f"outputTextColor                  = {rgb(output_col)}",
            f"messageTextColor                 = {rgb(msg_col)}",
        ]
        if font_size > 0:
            lines.append(f"editorFontSize = {font_size}")

        # Title bar restore via Python DWM
        # Bundle path for Python imports
        bundle_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "\\\\")

        lines += [
            "",
            "-- Title bar colors (Windows 11)",
            "(",
            "    local sys = python.import \"sys\"",
            f"    local bundleDir = \"{bundle_dir}\"",
            "    local syspaths = for p in (sys.path as array) collect (tolower (substituteString p \"\\\\\" \"/\"))",
            "    local normDir = tolower (substituteString bundleDir \"\\\\\" \"/\")",
            "    if (findItem syspaths normDir) == 0 then (sys.path.insert 0 bundleDir)",
            "    try (",
            "        local mw = python.import \"ui.main_window\"",
            f"        local base_col = \"{base}\"",
            f"        local fg_col   = \"{fg_col}\"",
            "        mw.apply_titlebar_to_all_max_windows base_col fg_col",
            "    ) catch()",
            ")",
        ]

        content = "\n".join(lines)
        script_name = "MAB_ThemesManager_startup.ms"

        # Write only to the current running Max version
        startup_dir = rt.pathConfig.GetDir(rt.Name("userStartupScripts"))
        with open(startup_dir + "\\" + script_name, "w", encoding="utf-8") as f:
            f.write(content)

    except Exception as e:
        print(f"[ThemesManager] save_listener_startup_script: {e}")
