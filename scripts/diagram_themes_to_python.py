#!/usr/bin/env python
"""Generate diagram_theme.py and diagram-themes.json from diagram-themes.yaml.

Resolves `extends` (mappings merge key by key, anything else replaces),
validates every theme, checks that every `var(--role)` reference names a
colour role the theme defines, and derives a palette variant
`<theme>-<palette>` for every theme and every page palette in themes.yaml:
the neutrals named under `palette-neutrals` come from the palette's tokens,
everything else is the theme's. Consumers get fully resolved, checked
themes: Python for the SVG scripts, JSON for rsslide.
"""

from __future__ import annotations

import json
import pprint
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from themes_common import load_themes

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "diagram-themes.yaml"
PY_PATH = ROOT / "diagram_theme.py"
JSON_PATH = ROOT / "diagram-themes.json"

HEADER = '''\
"""
shared-themes/diagram_theme.py

GENERATED FROM diagram-themes.yaml — do not edit by hand.
Run scripts/diagram_themes_to_python.py after editing diagram-themes.yaml.

The diagram themes, with `extends` resolved, and their palette variants:

    from diagram_theme import DIAGRAM_THEMES, DIAGRAM_THEME_VARIANTS, DEFAULT_DIAGRAM_THEME
    theme = DIAGRAM_THEMES["muted"]
    theme["shadow"]      # {"dx": 0, "dy": 4, ...}, or "none"
    DIAGRAM_THEME_VARIANTS["flat-midnight"]["colors"]["neutrals"]["bg"]   # "#0f1117"
"""

from __future__ import annotations

from typing import Any

'''

# Keys every resolved theme must have.
REQUIRED = ("colors", "shadow", "markers", "shapes", "lines")
SHADOW_KEYS = {"dx", "dy", "blur", "color", "apply-to"}
APPLY_TO = {"family-only", "all"}
ROLE_REF = re.compile(r"var\(--([a-z0-9-]+)\)")


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


def roles_of(theme: dict[str, Any]) -> set[str]:
    return {role for group in theme["colors"].values() for role in group}


def role_refs(value: Any) -> set[str]:
    """Every role a value references through `var(--role)`, at any depth."""
    if isinstance(value, str):
        return set(ROLE_REF.findall(value))
    if isinstance(value, dict):
        return set().union(*(role_refs(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(role_refs(v) for v in value))
    return set()


def check(name: str, theme: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if key not in theme]
    if missing:
        sys.exit(f"diagram theme {name!r} lacks {', '.join(missing)}")
    shadow = theme["shadow"]
    if shadow != "none":
        if not isinstance(shadow, dict) or set(shadow) != SHADOW_KEYS:
            sys.exit(f"diagram theme {name!r}: shadow must be `none` or have exactly {sorted(SHADOW_KEYS)}")
        if shadow["apply-to"] not in APPLY_TO:
            sys.exit(f"diagram theme {name!r}: shadow apply-to must be one of {sorted(APPLY_TO)}")
    unknown = sorted(role_refs(theme) - roles_of(theme))
    if unknown:
        sys.exit(f"diagram theme {name!r} references roles it does not define: {unknown}")


def variant(theme: dict[str, Any], neutrals_map: dict[str, str], tokens: dict[str, str]) -> dict[str, Any]:
    """The theme with its neutrals taken from a page palette's tokens."""
    out = json.loads(json.dumps(theme))  # a deep copy
    neutrals = out["colors"]["neutrals"]
    for role, token in neutrals_map.items():
        if role not in neutrals:
            sys.exit(f"palette-neutrals names {role!r}, which the theme's neutrals do not define")
        if token not in tokens:
            sys.exit(f"palette-neutrals maps {role!r} to token {token!r}, which the palette lacks")
        neutrals[role] = tokens[token]
    return out


def main() -> int:
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    default = data["default"]
    themes = data["themes"]
    neutrals_map = data.get("palette-neutrals")
    if not isinstance(neutrals_map, dict) or not neutrals_map:
        sys.exit("diagram-themes.yaml needs a `palette-neutrals` map (diagram role -> palette token)")
    if default not in themes:
        sys.exit(f"default diagram theme {default!r} is not defined in themes")

    resolved = {name: resolve(name, themes) for name in themes}
    for name, theme in resolved.items():
        check(name, theme)

    palettes = load_themes()
    variants = {
        f"{name}-{code}": variant(theme, neutrals_map, tokens)
        for name, theme in resolved.items()
        for code, tokens in palettes.themes.items()
    }

    out: list[str] = [HEADER]
    out.append(f"DEFAULT_DIAGRAM_THEME: str = {default!r}\n")
    body = pprint.pformat(resolved, indent=4, width=88, sort_dicts=False)
    out.append(f"DIAGRAM_THEMES: dict[str, dict[str, Any]] = {body}\n")
    out.append("DIAGRAM_THEME_NAMES: list[str] = list(DIAGRAM_THEMES)\n")
    out.append("# diagram neutral role -> page palette token, the rule the variants are made by")
    out.append(f"PALETTE_NEUTRALS: dict[str, str] = {neutrals_map!r}\n")
    body = pprint.pformat(variants, indent=4, width=88, sort_dicts=False)
    out.append(f"DIAGRAM_THEME_VARIANTS: dict[str, dict[str, Any]] = {body}\n")
    PY_PATH.write_text("\n".join(out), encoding="utf-8")

    doc = {
        "default": default,
        "palette-neutrals": neutrals_map,
        "themes": resolved,
        "variants": variants,
    }
    JSON_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {PY_PATH.relative_to(ROOT)} and {JSON_PATH.relative_to(ROOT)} "
        f"({len(resolved)} diagram themes, {len(variants)} palette variants, default={default})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
