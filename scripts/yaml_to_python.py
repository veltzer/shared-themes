#!/usr/bin/env python
"""Generate theme.py from themes.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "themes.yaml"
PY_PATH = ROOT / "theme.py"

HEADER = '''\
"""
shared-themes/theme.py

GENERATED FROM themes.yaml — do not edit by hand.
Run scripts/yaml_to_python.py after editing themes.yaml.

Exposes the same design tokens as themes.css, for Python consumers.

    from theme import THEMES, BASE, DEFAULT_THEME
    azure_bg = THEMES["azure"]["bg"]
    radius   = BASE["radius"]
"""

from __future__ import annotations

'''


def py_repr_dict(d: dict[str, str], indent: str) -> str:
    """Emit a dict literal with one key per line, sorted by insertion order."""
    lines = ["{"]
    for k, v in d.items():
        lines.append(f'{indent}    {k!r}: {v!r},')
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

    out.append("BASE: dict[str, str] = " + py_repr_dict(base, "") + "\n")

    out.append("THEMES: dict[str, dict[str, str]] = {")
    for name, vars_ in themes.items():
        out.append(f"    {name!r}: " + py_repr_dict(vars_, "    ") + ",")
    out.append("}\n")

    out.append("THEME_NAMES: list[str] = list(THEMES)\n")

    PY_PATH.write_text("\n".join(out))
    print(f"wrote {PY_PATH.relative_to(ROOT)} ({len(themes)} themes, default={default})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
