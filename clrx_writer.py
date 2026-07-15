
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

CLRX_PATH = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    r"Autodesk\3dsMax\2026 - 64bit\ENU\en-US\UI\MaxStartUI.clrx"
)


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
            existing[cid].set("value", hex_val)
        # If not present, skip — we only update what's already in the file

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
        rt.colorMan.repaintUI()
    except Exception as e:
        print(f"[ThemeCustomizer] apply_to_max: {e}")
