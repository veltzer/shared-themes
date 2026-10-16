#!/usr/bin/env python
"""Generate marp/<theme>.css, one marp theme per palette, from themes.yaml.

Each file extends marp's built-in `default` theme and recolors it with the
shared tokens: the tokens are declared on `section` (marp scopes a theme to
the slide element), marp's own `--color-*` variables are mapped onto them,
and a few explicit rules cover what the default theme does not route
through a variable. A deck selects one with `theme: <code>` in its front
matter, and marp-cli loads the directory with `--theme-set marp`.
"""

from __future__ import annotations

import shutil
import sys

from themes_common import ROOT, load_themes

MARP_DIR = ROOT / "marp"

# marp's default theme reads these; mapping them is what recolors it.
MARP_VARS: dict[str, str] = {
    "color-background": "bg",
    "color-foreground": "text-primary",
    "color-highlight": "accent",
    "color-dimmed": "text-muted",
    "color-background-code": "bg-surface",
    "color-background-paginate": "accent-dim",
    "color-background-stripe": "bg-elevated",
}

RULES = """\
section {
  font-family: var(--font-sans);
}

section a {
  color: var(--accent);
}

section code,
section pre {
  font-family: var(--font-mono);
}

section pre {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
}

section blockquote {
  border-left: 4px solid var(--accent);
  color: var(--text-secondary);
}

section table th {
  background: var(--bg-surface);
}

section table th,
section table td {
  border-color: var(--border);
}

section hr {
  border-color: var(--border-subtle);
}

section header,
section footer,
section::after {
  color: var(--text-muted);
}
"""


def emit_theme(code: str, label: str, base: dict[str, str], tokens: dict[str, str]) -> str:
    lines = [
        f"/* @theme {code} */",
        "/*",
        f" * shared-themes/marp/{code}.css",
        " *",
        " * GENERATED FROM themes.yaml — do not edit by hand.",
        " * Run scripts/yaml_to_marp.py after editing themes.yaml.",
        " *",
        f" * Marp theme \"{code}\" ({label}): marp's default theme restyled with the",
        " * shared design tokens. Select it with `theme: " + code + "` in a deck and",
        " * load it with `marp --theme-set <path to this marp/ directory>`.",
        " */",
        "",
        "@import 'default';",
        "",
        "section {",
    ]
    for name, value in base.items():
        lines.append(f"  --{name}: {value};")
    for name, value in tokens.items():
        lines.append(f"  --{name}: {value};")
    lines.append("")
    for marp_name, token in MARP_VARS.items():
        lines.append(f"  --{marp_name}: var(--{token});")
    lines.append("}")
    lines.append("")
    lines.append(RULES)
    return "\n".join(lines)


def main() -> int:
    data = load_themes()
    if MARP_DIR.exists():
        shutil.rmtree(MARP_DIR)
    MARP_DIR.mkdir()
    for code, tokens in data.themes.items():
        path = MARP_DIR / f"{code}.css"
        path.write_text(emit_theme(code, data.labels[code], data.base, tokens))
    print(f"wrote {MARP_DIR.relative_to(ROOT)}/ ({len(data.themes)} marp themes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
