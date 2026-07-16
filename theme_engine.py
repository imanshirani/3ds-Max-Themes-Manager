
import math


# ── OKLCH ↔ sRGB conversion (no external deps) ─────────────────────────────

def _linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def _gamma(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    r, g, b = (_linear(int(h[i:i+2], 16) / 255) for i in (0, 2, 4))
    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b
    l_, m_, s_ = l**0.3333333, m**0.3333333, s**0.3333333
    L = 0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_
    a = 1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_
    b_ = 0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_
    C = math.sqrt(a*a + b_*b_)
    H = math.degrees(math.atan2(b_, a)) % 360
    return L, C, H

def oklch_to_hex(L: float, C: float, H: float) -> str:
    L = max(0.0, min(1.0, L))
    C = max(0.0, C)
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    r =  4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    b_ = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    r, g, b_ = (_gamma(max(0.0, min(1.0, x))) for x in (r, g, b_))
    return "#{:02x}{:02x}{:02x}".format(int(r*255+.5), int(g*255+.5), int(b_*255+.5))

def _shift(hex_color: str, dL=0.0, dC=0.0, dH=0.0, scaleC=1.0) -> str:
    L, C, H = hex_to_oklch(hex_color)
    return oklch_to_hex(L + dL, C * scaleC + dC, (H + dH) % 360)

def _mix(a: str, b: str, t: float) -> str:
    La, Ca, Ha = hex_to_oklch(a)
    Lb, Cb, Hb = hex_to_oklch(b)
    dH = ((Hb - Ha + 180) % 360) - 180
    return oklch_to_hex(La+(Lb-La)*t, Ca+(Cb-Ca)*t, Ha+dH*t)


# ── Color map generation ────────────────────────────────────────────────────

def _luminance(hex_color: str) -> float:
    """WCAG relative luminance (0=black, 1=white)."""
    h = hex_color.lstrip("#")
    r, g, b = (_linear(int(h[i:i+2], 16) / 255) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def _is_dark(hex_color: str) -> bool:
    return _luminance(hex_color) < 0.179

def _contrast_text(bg_hex: str) -> str:
    """Return white or near-black whichever has higher WCAG contrast on bg_hex."""
    lum = _luminance(bg_hex)
    contrast_white = (1.0 + 0.05) / (lum + 0.05)
    contrast_black = (lum + 0.05) / (0.0 + 0.05)
    return "#f0f0f0" if contrast_white >= contrast_black else "#1a1a1a"

def generate_color_map(base: str, accent: str, highlight: str) -> dict:
    """
    Returns a dict {color_id: hex_string} covering the key UI color IDs.
    Fixed/structural colors (trackbar keys, unwrap, etc.) are left unchanged.
    """
    dark = _is_dark(base)
    text_dL = 0.65 if dark else -0.65

    btn_bg = _shift(base, dL=-0.05)

    m = {}

    # ── Appearance ──
    m[111] = base                                             # Background Odd
    m[112] = _shift(base, dL=0.03)                          # Background Even
    m[113] = btn_bg                                           # Button
    m[114] = _contrast_text(btn_bg)                          # Button Text
    m[115] = _contrast_text(btn_bg)                          # Button Text Pressed
    m[116] = _shift(accent, dL=0.15)                         # Focus Border
    m[117] = _shift(base, dL=0.12)                           # UI Borders
    m[1]   = _shift(base, dL=text_dL*0.95, scaleC=0.08)     # Text
    m[4]   = accent                                           # Active Command
    m[5]   = _shift(base, dL=0.08)                           # 3D Highlight
    m[6]   = _shift(base, dL=-0.08)                          # 3D Shadow
    m[8]   = _shift(accent, dL=-0.2, scaleC=0.4)            # Active Caption
    m[9]   = highlight                                        # ToolTip (Viewport) BG
    m[10]  = _shift(highlight, dL=text_dL, scaleC=0.05)     # ToolTip (Viewport) Text
    m[11]  = _shift(base, dL=text_dL*0.9, scaleC=0.05)      # Highlight Text
    m[13]  = _shift(accent, dL=0.05, dC=0.02)               # Item Highlight
    m[14]  = _shift(accent, dH=15)                           # Sub-object Selection
    m[15]  = _shift(base, dL=-0.12)                          # 3D Dark Shadow
    m[16]  = _shift(base, dL=0.16)                           # 3D Light
    m[17]  = _shift(base, dL=-0.08)                          # App Workspace
    m[25]  = _shift(accent, dL=-0.1)                         # Pressed Buttons
    m[26]  = _shift(base, dL=-0.03)                          # Time Slider BG
    m[33]  = _shift(accent, scaleC=0.0, dL=text_dL)         # Selection Rubber Band
    m[34]  = accent                                           # Modifier Selection
    m[38]  = accent                                           # Pressed Hierarchy Button
    m[93]  = _shift(highlight, dH=160, dL=0.1)              # Adaptive Degradation Active
    m[127] = _shift(base, dL=0.18)                           # ToolTip (UI) BG
    m[128] = _shift(base, dL=text_dL, scaleC=0.05)          # ToolTip (UI) Text
    m[129] = _shift(base, dL=-0.01)                          # Row Background
    m[130] = _shift(base, dL=0.04)                           # Row Alt Background
    m[131] = _shift(base, dL=-0.04)                          # Render Message BG
    m[132] = _shift(base, dL=text_dL*0.8, scaleC=0.05)      # Render Message Text
    m[133] = _shift(accent, dL=0.15, scaleC=0.6)            # Render Message System
    m[134] = _shift(highlight, dH=30)                        # Render Message Warning
    m[136] = _shift(highlight, dL=0.1)                       # Search Highlight
    # Fixed
    m[118] = "#8f2f2f"   # Animation Key Brackets
    m[135] = "#ec4841"   # Render Error

    # ── Trackbar ──
    m[18]  = _shift(base, dL=-0.04)                          # Trackbar BG
    m[19]  = _shift(accent, dL=-0.15, scaleC=0.4)           # Trackbar Selected BG
    m[20]  = _shift(base, dL=text_dL*0.7, scaleC=0.05)      # Trackbar Text
    m[21]  = _shift(base, dL=0.22)                           # Trackbar Ticks
    m[22]  = "#000000"
    m[23]  = "#ffffff"
    m[24]  = highlight                                        # Trackbar Cursor
    # Key colors fixed
    m[79]  = "#a30000"; m[80] = "#007a00"; m[81] = "#0000c9"
    m[82]  = "#000000"; m[83] = "#000000"; m[84] = "#000000"; m[85] = "#000000"
    m[107] = "#00ff00"; m[108] = "#ffff00"

    # ── Viewports ──
    m[27]  = _shift(base, dL=0.06)                           # Viewport Border
    m[28]  = _shift(accent, dL=0.05)                         # Active Viewport Border

    # ── Rollup ──
    m[29]  = _shift(base, dL=0.09)                           # Rollup Title Face
    m[30]  = _shift(base, dL=text_dL*0.85, scaleC=0.05)     # Rollup Title Text
    m[31]  = _shift(base, dL=0.18)                           # Rollup Hilight
    m[32]  = _shift(base, dL=-0.04)                          # Rollup Shadow

    # ── Tabs ──
    m[17408] = _shift(base, dL=0.07)                         # Unselected Tabs
    m[17332] = "#ff0000"                                      # Auto Key Button
    m[17424] = "#3a843e"                                      # Set Key Mode

    return m
