#!/usr/bin/env python
"""Generate themes.css from themes.yaml."""

from __future__ import annotations

import sys

from themes_common import ROOT, is_light, load_themes

CSS_PATH = ROOT / "themes.css"

HEADER = """\
/*
 * shared-themes/themes.css
 *
 * GENERATED FROM themes.yaml — do not edit by hand.
 * Run scripts/yaml_to_css.py after editing themes.yaml.
 *
 * Six named themes, exposed as CSS custom properties scoped to
 * `[data-theme="<name>"]`. The default theme is also applied to `:root`
 * so it shows even when no `data-theme` attribute is set. Each block also
 * sets `color-scheme`, so the controls and scrollbars the browser draws
 * match the theme.
 */
"""

# The scripts that pick a theme for a reader who has not chosen one. They
# name the two defaults as string constants, which must match themes.yaml.
SWITCHER_JS = ROOT / "theme-switcher.js"
ONLOAD_JS = ROOT / "theme-onload.js"



def emit_block(selector: str, vars_: dict[str, str], scheme: str | None = None) -> str:
    lines = [f"{selector} {{"]
    if scheme:
        lines.append(f"  color-scheme: {scheme};")
    for name, value in vars_.items():
        lines.append(f"  --{name}: {value};")
    lines.append("}")
    return "\n".join(lines)


def check_js_defaults(default: str, default_dark: str) -> None:
    """Fail when the theme scripts name other defaults than themes.yaml."""
    wanted = {
        SWITCHER_JS: [f'const LIGHT_THEME = "{default}";', f'const DARK_THEME = "{default_dark}";'],
        ONLOAD_JS: [f'var DARK_THEME = "{default_dark}";'],
    }
    for path, lines in wanted.items():
        text = path.read_text()
        for line in lines:
            if line not in text:
                sys.exit(f"{path.name} does not say `{line}`, which is what themes.yaml sets")


def main() -> int:
    data = load_themes()
    default = data.default
    base = data.base
    themes = data.themes
    check_js_defaults(default, data.default_dark)

    parts = [HEADER]

    parts.append("/* ─── Base tokens (radius, font, transition, default shadow) ─── */")
    parts.append(emit_block(":root", base))

    for name, vars_ in themes.items():
        banner = f"{data.labels[name]} ({data.descriptions[name]})"
        if name == default:
            banner += " — default when no data-theme attribute is set"
        parts.append(f"/* ─── {banner} ─── */")
        if name == default:
            selector = f':root, [data-theme="{name}"]'
        else:
            selector = f'[data-theme="{name}"]'
        parts.append(emit_block(selector, vars_, "light" if is_light(vars_) else "dark"))

    output = "\n\n".join(parts) + "\n"
    CSS_PATH.write_text(output)
    print(f"wrote {CSS_PATH.relative_to(ROOT)} ({len(themes)} themes, default={default})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
