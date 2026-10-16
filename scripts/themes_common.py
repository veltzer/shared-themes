"""Shared loader for themes.yaml, used by every generator in scripts/.

Splits each theme entry into its display `label`, its `description` and its
tokens, and checks the file is consistent before any generator writes an
output: the default theme must exist, every theme needs a label and a
description, and every theme must define every token the default theme
defines unless `base:` provides a fallback.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "themes.yaml"


@dataclass(frozen=True)
class Themes:
    default: str
    base: dict[str, str]
    # code -> display name, in file order
    labels: dict[str, str]
    # code -> short hint ("dark blue"), in file order
    descriptions: dict[str, str]
    # code -> tokens, in file order
    themes: dict[str, dict[str, str]]


def load_themes() -> Themes:
    data = yaml.safe_load(YAML_PATH.read_text())
    default = data["default"]
    base = data["base"]
    raw = data["themes"]

    if default not in raw:
        sys.exit(f"default theme {default!r} is not defined in themes")

    labels: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    themes: dict[str, dict[str, str]] = {}
    for code, entry in raw.items():
        tokens = dict(entry)
        label = tokens.pop("label", None)
        if not isinstance(label, str) or not label:
            sys.exit(f"theme {code!r} has no label")
        description = tokens.pop("description", None)
        if not isinstance(description, str) or not description:
            sys.exit(f"theme {code!r} has no description")
        labels[code] = label
        descriptions[code] = description
        themes[code] = tokens

    required = set(themes[default]) - set(base)
    for code, tokens in themes.items():
        missing = sorted(required - set(tokens))
        if missing:
            sys.exit(f"theme {code!r} is missing tokens {missing}")

    return Themes(
        default=default,
        base=base,
        labels=labels,
        descriptions=descriptions,
        themes=themes,
    )
