"""Built-in theme presets + user preset persistence."""
import os
import json

PRESETS = [
    {
        "name": "Max Dark (Default)",
        "base":      "#1c1c1c",
        "accent":    "#5f8ac1",
        "highlight": "#ffb100",
        "theme_type": 0,
    },
    {
        "name": "Dark Blue",
        "base":      "#151b25",
        "accent":    "#3d8bff",
        "highlight": "#00d4ff",
        "theme_type": 0,
    },
    {
        "name": "Dark Warm",
        "base":      "#1e1a17",
        "accent":    "#c87941",
        "highlight": "#f5c842",
        "theme_type": 0,
    },
    {
        "name": "Slate",
        "base":      "#2a2e35",
        "accent":    "#6eb5a0",
        "highlight": "#e0c46a",
        "theme_type": 0,
    },
    {
        "name": "Light (Default)",
        "base":      "#dcdcdc",
        "accent":    "#2a6bbf",
        "highlight": "#d97a00",
        "theme_type": 1,
    },
    {
        "name": "Light Silver",
        "base":      "#e8e8e8",
        "accent":    "#5577aa",
        "highlight": "#c0392b",
        "theme_type": 1,
    },
    {
        "name": "Light Sand",
        "base":      "#ede8e0",
        "accent":    "#8b6914",
        "highlight": "#c0392b",
        "theme_type": 1,
    },
    {
        "name": "Light Mint",
        "base":      "#e4eeea",
        "accent":    "#2e7d5e",
        "highlight": "#c0392b",
        "theme_type": 1,
    },
    {
        "name": "Light Lavender",
        "base":      "#ebe8f0",
        "accent":    "#6a4fa0",
        "highlight": "#c0392b",
        "theme_type": 1,
    },
    {
        "name": "Midnight Purple",
        "base":      "#181420",
        "accent":    "#9b6dff",
        "highlight": "#ff6eb4",
        "theme_type": 0,
    },
]

USER_PRESETS_FILE = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "MaxThemesManager",
    "user_presets.json",
)


def _load_user_presets() -> list[dict]:
    if not os.path.isfile(USER_PRESETS_FILE):
        return []
    try:
        with open(USER_PRESETS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return [p for p in data if isinstance(p, dict) and "name" in p]
    except Exception:
        return []


def _save_user_presets(user_list: list[dict]):
    os.makedirs(os.path.dirname(USER_PRESETS_FILE), exist_ok=True)
    with open(USER_PRESETS_FILE, "w", encoding="utf-8") as f:
        json.dump(user_list, f, indent=2, ensure_ascii=False)


def load_all_presets() -> list[dict]:
    """Returns built-in presets followed by user-saved presets."""
    user = [dict(p, user=True) for p in _load_user_presets()]
    return PRESETS + user


def save_user_preset(name: str, base: str, accent: str, highlight: str, theme_type: int = 0):
    """Save or overwrite a user preset by name."""
    user = _load_user_presets()
    user = [p for p in user if p.get("name") != name]
    user.append({
        "name":       name,
        "base":       base,
        "accent":     accent,
        "highlight":  highlight,
        "theme_type": theme_type,
    })
    _save_user_presets(user)


def delete_user_preset(name: str):
    """Delete a user preset by name (built-ins are not deletable)."""
    user = _load_user_presets()
    user = [p for p in user if p.get("name") != name]
    _save_user_presets(user)
