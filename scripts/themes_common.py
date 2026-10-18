"""Shared loader for themes.yaml, used by every generator in scripts/.

Splits each theme entry into its display `label`, its `description` and its
tokens, and checks the file is consistent before any generator writes an
output: the default theme must exist, every theme needs a label and a
description, and every theme must define every token the default theme
defines unless `base:` provides a fallback.
"""

from __future__ import annotations

import re
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


# ── print consumers ──────────────────────────────────────────────────────────
# LaTeX and Word have no alpha channel and no CSS font stacks, so the print
# generators (yaml_to_latex.py, yaml_to_docx.py) need every color as an opaque
# RGB value and every font role as one family name.

HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RGBA_RE = re.compile(
    r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$"
)
FONT_FAMILY_RE = re.compile(r"^\s*(['\"]?)([^'\",]+)\1")

# Theme tokens that are not colors. Every other theme token must parse as one.
NON_COLOR_TOKENS = frozenset({"shadow"})


def font_family(value: str) -> str:
    """Extract the bare primary family from a CSS font-family string.

    'JetBrains Mono', monospace  ->  JetBrains Mono
    """
    m = FONT_FAMILY_RE.match(value)
    if not m:
        raise ValueError(f"could not parse font family from {value!r}")
    return m.group(2).strip()


def parse_color(value: str) -> tuple[int, int, int, float]:
    """Parse a token color (#rgb, #rrggbb, rgb(), rgba()) into r, g, b, alpha."""
    s = value.strip()
    m = HEX_RE.match(s)
    if m:
        digits = m.group(1)
        if len(digits) == 3:
            digits = "".join(c * 2 for c in digits)
        return int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16), 1.0
    m = RGBA_RE.match(s)
    if m:
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        alpha = 1.0 if m.group(4) is None else float(m.group(4))
        if max(r, g, b) > 255 or not 0.0 <= alpha <= 1.0:
            raise ValueError(f"color out of range: {value!r}")
        return r, g, b, alpha
    raise ValueError(f"not a color: {value!r}")


def opaque_colors(tokens: dict[str, str]) -> dict[str, str]:
    """Every color token of a theme as an opaque RRGGBB hex string.

    A translucent color is composited over the theme's own `bg`, which is
    what it looks like on the page; `bg` itself must be opaque.
    """
    br, bgg, bb, ba = parse_color(tokens["bg"])
    if ba != 1.0:
        raise ValueError(f"bg must be opaque, got {tokens['bg']!r}")
    out: dict[str, str] = {}
    for name, value in tokens.items():
        if name in NON_COLOR_TOKENS:
            continue
        r, g, b, a = parse_color(value)
        rgb = (round(c * a + under * (1 - a)) for c, under in ((r, br), (g, bgg), (b, bb)))
        out[name] = "".join(f"{c:02X}" for c in rgb)
    return out


def is_light(tokens: dict[str, str]) -> bool:
    """Whether a theme's background is light (WCAG relative luminance >= 0.5)."""
    channels = parse_color(tokens["bg"])[:3]

    def linear(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b >= 0.5


def check_declared_outputs(written: list[Path]) -> None:
    """Fail unless the files a generator wrote are exactly its declared outputs.

    rsconstruct calls an explicit processor with `--output-files <files...>`
    after its other arguments; that list is the processor's `output_files` in
    rsconstruct.toml. A theme added to themes.yaml but not to the list (or
    the reverse) would otherwise be generated but never cached or checked.
    Run by hand, without the flag, there is nothing to compare against.
    """
    argv = sys.argv[1:]
    if "--output-files" not in argv:
        return
    declared: set[str] = set()
    for arg in argv[argv.index("--output-files") + 1:]:
        if arg.startswith("--"):
            break
        declared.add(arg)
    actual = {str(path.relative_to(ROOT)) for path in written}
    if actual != declared:
        sys.exit(
            "generated files differ from output_files in rsconstruct.toml: "
            f"not declared {sorted(actual - declared)}, not generated {sorted(declared - actual)}"
        )
