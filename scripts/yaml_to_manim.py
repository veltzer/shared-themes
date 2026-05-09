#!/usr/bin/env python
"""Generate manim_themes.py from themes.yaml.

Color tokens are emitted as ManimColor instances so Manim scenes can use them
directly (e.g. ``self.camera.background_color = THEMES["azure"]["bg"]``).
Non-color base tokens (radius, font, transition) are passed through as the
original strings — Manim won't consume them, but they're kept so the structure
mirrors theme.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "themes.yaml"
PY_PATH = ROOT / "manim_themes.py"

HEADER = '''\
"""
shared-themes/manim_themes.py

GENERATED FROM themes.yaml — do not edit by hand.
Run scripts/yaml_to_manim.py after editing themes.yaml.

Exposes the same design tokens as themes.css, as ManimColor objects ready
for use inside Manim animations.

    from manim_themes import THEMES, BASE, DEFAULT_THEME
    azure_bg = THEMES["azure"]["bg"]          # ManimColor
    self.camera.background_color = azure_bg
"""

from __future__ import annotations

from manim import ManimColor

'''

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RGBA_RE = re.compile(
    r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$"
)


def color_expr(value: str) -> str | None:
    """Return a Python expression constructing a ManimColor, or None if not a color."""
    s = value.strip()
    if HEX_RE.match(s):
        return f'ManimColor("{s}")'
    m = RGBA_RE.match(s)
    if m:
        r, g, b, a = m.group(1), m.group(2), m.group(3), m.group(4)
        if a is None:
            return f"ManimColor(({r}, {g}, {b}))"
        return f"ManimColor(({r}, {g}, {b}, int(round({a} * 255))))"
    return None


def emit_value(value: str) -> str:
    """Return a Python expression for a token value."""
    expr = color_expr(value)
    if expr is not None:
        return expr
    return repr(value)


def emit_dict(d: dict[str, str], indent: str) -> str:
    lines = ["{"]
    for k, v in d.items():
        lines.append(f"{indent}    {k!r}: {emit_value(v)},")
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def main() -> int:
    data = yaml.safe_load(YAML_PATH.read_text())
    default = data["default"]
    base = data["base"]
    themes = data["themes"]

    if default not in themes:
        sys.exit(f"default theme {default!r} is not defined in themes")

    out: list[str] = [HEADER]

    out.append(f"DEFAULT_THEME: str = {default!r}\n")

    out.append("BASE: dict[str, object] = " + emit_dict(base, "") + "\n")

    out.append("THEMES: dict[str, dict[str, object]] = {")
    for name, vars_ in themes.items():
        out.append(f"    {name!r}: " + emit_dict(vars_, "    ") + ",")
    out.append("}\n")

    out.append("THEME_NAMES: list[str] = list(THEMES)\n")

    PY_PATH.write_text("\n".join(out))
    print(f"wrote {PY_PATH.relative_to(ROOT)} ({len(themes)} themes, default={default})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
