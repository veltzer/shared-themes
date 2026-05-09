#!/usr/bin/env python
"""Generate manim_themes.py from themes.yaml.

The generated module is meant to be consumed directly by Manim scenes — no
adapter layer. It exposes:

  - THEMES, BASE, DEFAULT_THEME, THEME_NAMES — raw token data.
  - ACTIVE_THEME — resolved from $ANIM_THEME, validated, falls back to default.
  - T — attribute view onto THEMES[ACTIVE_THEME]. Role keys map to UPPER_SNAKE
        identifiers (bg-surface -> T.BG_SURFACE, text-primary -> T.TEXT_PRIMARY).
  - apply_defaults() — sets config.background_color and Text/MathTex/Tex
        defaults so a scene picks up the active theme's bg + text + sans font.

Names in the module are symbolic (roles, not implementations): tokens are
identified by what they are *used for* (accent, text-primary, font-mono),
never by what they happen to be (#4051b5, "JetBrains Mono"). Font role
values are stripped of CSS quoting so the bare family name is usable as
Manim's font= kwarg.
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

Exposes design tokens by role (what they're used for), not by implementation.
Consumers import this module directly:

    from manim_themes import T, BASE, apply_defaults

    apply_defaults()                      # sets bg + Text defaults

    Text("hello", color=T.ACCENT)
    Text("code", color=T.TEXT_PRIMARY, font=BASE["font-mono"])

The active theme is picked from $ANIM_THEME (validated), falling back to
DEFAULT_THEME.
"""

from __future__ import annotations

import os

from manim import ManimColor

'''

FOOTER = '''

class _T:
    """Attribute-style view onto the active palette.

    Role keys from themes.yaml are exposed as UPPER_SNAKE identifiers:
    bg-surface -> BG_SURFACE, text-primary -> TEXT_PRIMARY, accent-dim ->
    ACCENT_DIM, etc. Values are ManimColor for color roles and plain strings
    for non-color roles (e.g. shadow).
    """

    def __init__(self, palette: dict[str, object]) -> None:
        for key, value in palette.items():
            setattr(self, key.replace("-", "_").upper(), value)


ACTIVE_THEME: str = os.environ.get("ANIM_THEME", DEFAULT_THEME)
if ACTIVE_THEME not in THEMES:
    raise SystemExit(
        f"ANIM_THEME={ACTIVE_THEME!r} is not a known theme. "
        f"Known: {sorted(THEMES)}"
    )

T = _T(THEMES[ACTIVE_THEME])


def apply_defaults() -> None:
    """Boot the current Manim scene to use the active theme.

    Sets config.background_color to T.BG and Text/MathTex/Tex color defaults
    to T.TEXT_PRIMARY. Text additionally gets the sans font role as its
    default family.
    """
    from manim import MathTex, Tex, Text, config

    config.background_color = T.BG
    Text.set_default(color=T.TEXT_PRIMARY, font=BASE["font-sans"])
    MathTex.set_default(color=T.TEXT_PRIMARY)
    Tex.set_default(color=T.TEXT_PRIMARY)
'''

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RGBA_RE = re.compile(
    r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$"
)
FONT_FAMILY_RE = re.compile(r"^\s*(['\"]?)([^'\",]+)\1")


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


def font_family(value: str) -> str:
    """Extract the bare primary family from a CSS font-family string.

    'JetBrains Mono', monospace  ->  JetBrains Mono
    """
    m = FONT_FAMILY_RE.match(value)
    if not m:
        raise ValueError(f"could not parse font family from {value!r}")
    return m.group(2).strip()


def emit_value(key: str, value: str) -> str:
    """Return a Python expression for a token value."""
    expr = color_expr(value)
    if expr is not None:
        return expr
    if key.startswith("font-"):
        return repr(font_family(value))
    return repr(value)


def emit_dict(d: dict[str, str], indent: str) -> str:
    lines = ["{"]
    for k, v in d.items():
        lines.append(f"{indent}    {k!r}: {emit_value(k, v)},")
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

    out.append("THEME_NAMES: list[str] = list(THEMES)")

    out.append(FOOTER)

    PY_PATH.write_text("\n".join(out))
    print(f"wrote {PY_PATH.relative_to(ROOT)} ({len(themes)} themes, default={default})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
