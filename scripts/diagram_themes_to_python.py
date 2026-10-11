#!/usr/bin/env python
"""Generate diagram_theme.py from diagram-themes.yaml.

Resolves `extends` (mappings merge key by key, anything else replaces) and
validates every theme, so consumers import fully resolved, checked themes.
"""

from __future__ import annotations

import pprint
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "diagram-themes.yaml"
PY_PATH = ROOT / "diagram_theme.py"

HEADER = '''\
"""
shared-themes/diagram_theme.py

GENERATED FROM diagram-themes.yaml — do not edit by hand.
Run scripts/diagram_themes_to_python.py after editing diagram-themes.yaml.

The diagram themes, with `extends` resolved:

    from diagram_theme import DIAGRAM_THEMES, DEFAULT_DIAGRAM_THEME
    theme = DIAGRAM_THEMES["muted"]
    theme["shadow"]      # {"dx": 0, "dy": 4, ...}, or "none"
"""

from __future__ import annotations

from typing import Any

'''

# Keys every resolved theme must have.
REQUIRED = ("colors", "shadow", "markers", "shapes", "lines")
SHADOW_KEYS = {"dx", "dy", "blur", "color", "apply-to"}
APPLY_TO = {"family-only", "all"}


def merge(base: Any, over: Any) -> Any:
    """`over` on top of `base`: mappings merge key by key, the rest replaces."""
    if isinstance(base, dict) and isinstance(over, dict):
        out = dict(base)
        for key, value in over.items():
            out[key] = merge(base[key], value) if key in base else value
        return out
    return over


def resolve(name: str, themes: dict[str, Any], seen: tuple[str, ...] = ()) -> dict[str, Any]:
    if name in seen:
        sys.exit(f"diagram theme {name!r} extends itself: {' -> '.join((*seen, name))}")
    if name not in themes:
        sys.exit(f"diagram theme {seen[-1]!r} extends unknown theme {name!r}")
    theme = dict(themes[name])
    parent = theme.pop("extends", None)
    if parent is None:
        return theme
    return merge(resolve(parent, themes, (*seen, name)), theme)


def check(name: str, theme: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if key not in theme]
    if missing:
        sys.exit(f"diagram theme {name!r} lacks {', '.join(missing)}")
    shadow = theme["shadow"]
    if shadow == "none":
        return
    if not isinstance(shadow, dict) or set(shadow) != SHADOW_KEYS:
        sys.exit(f"diagram theme {name!r}: shadow must be `none` or have exactly {sorted(SHADOW_KEYS)}")
    if shadow["apply-to"] not in APPLY_TO:
        sys.exit(f"diagram theme {name!r}: shadow apply-to must be one of {sorted(APPLY_TO)}")


def main() -> int:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    default = data["default"]
    themes = data["themes"]
    if default not in themes:
        sys.exit(f"default diagram theme {default!r} is not defined in themes")

    resolved = {name: resolve(name, themes) for name in themes}
    for name, theme in resolved.items():
        check(name, theme)

    out: list[str] = [HEADER]
    out.append(f"DEFAULT_DIAGRAM_THEME: str = {default!r}\n")
    body = pprint.pformat(resolved, indent=4, width=88, sort_dicts=False)
    out.append(f"DIAGRAM_THEMES: dict[str, dict[str, Any]] = {body}\n")
    out.append("DIAGRAM_THEME_NAMES: list[str] = list(DIAGRAM_THEMES)\n")

    PY_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {PY_PATH.relative_to(ROOT)} ({len(resolved)} diagram themes, default={default})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
