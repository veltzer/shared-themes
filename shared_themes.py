"""The consumer helper: what a site that inlines the shared layers needs.

The index pages of the teaching repos build one self-contained HTML file
and copy the fonts beside it. Each used to carry its own copy of that
logic; this module is the one copy. Load it from the submodule path, so a
consumer needs no package and no sys.path games:

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "shared_themes", SHARED_THEMES_DIR / "shared_themes.py")
    st = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(st)

    html = (template
            .replace("{{CSS}}", st.css() + own_css)
            .replace("{{JS}}", st.js() + own_js)
            .replace("<!--{{THEME_OPTIONS}}-->", st.theme_options(material_web=True)))
    st.publish_fonts(site_dir)

`css()` starts with fonts.css, whose url("fonts/...") entries are relative
to the page the CSS is inlined into; `publish_fonts()` puts fonts/ beside
that page.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The layers a site inlines, in order: fonts, tokens, reset, headings, widgets.
CSS_LAYERS = ("fonts.css", "themes.css", "base.css", "typography.css", "components.css")


def css() -> str:
    """Every shared CSS layer, concatenated in order."""
    return "\n".join((HERE / name).read_text(encoding="utf-8") for name in CSS_LAYERS) + "\n"


def js() -> str:
    """The theme switcher."""
    return (HERE / "theme-switcher.js").read_text(encoding="utf-8") + "\n"


def palette() -> dict:
    """themes.json: default, base tokens, and the themes in file order."""
    return json.loads((HERE / "themes.json").read_text(encoding="utf-8"))


def theme_options(*, material_web: bool = False) -> str:
    """The theme <select> entries, from themes.json, so the list, its order,
    its labels and their hints ("Midnight (dark blue)") are never retyped.
    The default theme is marked selected to match what :root applies.
    `material_web` picks the <md-select-option> markup over <option>."""
    data = palette()
    lines = []
    for theme in data["themes"]:
        code = theme["code"]
        label = f'{theme["label"]} ({theme["description"]})'
        selected = " selected" if code == data["default"] else ""
        if material_web:
            lines.append(
                f'<md-select-option value="{code}"{selected}>'
                f'<div slot="headline">{label}</div></md-select-option>'
            )
        else:
            lines.append(f'<option value="{code}"{selected}>{label}</option>')
    return "\n".join(lines)


def publish_fonts(site_dir: Path) -> None:
    """Copy fonts/ next to the page the CSS was inlined into."""
    shutil.copytree(HERE / "fonts", Path(site_dir) / "fonts", dirs_exist_ok=True)
