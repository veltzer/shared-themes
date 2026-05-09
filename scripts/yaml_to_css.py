#!/usr/bin/env python
"""Generate themes.css from themes.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "themes.yaml"
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
 * so it shows even when no `data-theme` attribute is set.
 */
"""

# Pretty section banners for each theme. Free-form — extend as new themes
# are added. Themes without an entry get a plain "/* <name> */" banner.
BANNERS: dict[str, str] = {
    "azure": "Azure (indigo light) — default when no data-theme attribute is set",
    "paper": "Paper (warm light)",
    "midnight": "Midnight (dark blue)",
    "nord": "Nord (cool muted)",
    "solarized": "Solarized (light)",
    "rosepine": "Rosepine (muted purple dark)",
}


def emit_block(selector: str, vars_: dict[str, str]) -> str:
    lines = [f"{selector} {{"]
    for name, value in vars_.items():
        lines.append(f"  --{name}: {value};")
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    data = yaml.safe_load(YAML_PATH.read_text())
    default = data["default"]
    base = data["base"]
    themes = data["themes"]

    if default not in themes:
        sys.exit(f"default theme {default!r} is not defined in themes")

    parts = [HEADER]

    parts.append("/* ─── Base tokens (radius, font, transition, default shadow) ─── */")
    parts.append(emit_block(":root", base))

    for name, vars_ in themes.items():
        banner = BANNERS.get(name, name)
        parts.append(f"/* ─── {banner} ─── */")
        if name == default:
            selector = f':root, [data-theme="{name}"]'
        else:
            selector = f'[data-theme="{name}"]'
        parts.append(emit_block(selector, vars_))

    output = "\n\n".join(parts) + "\n"
    CSS_PATH.write_text(output)
    print(f"wrote {CSS_PATH.relative_to(ROOT)} ({len(themes)} themes, default={default})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
