#!/usr/bin/env python
"""Generate latex/<theme>.tex, one LaTeX preamble theme per palette, from themes.yaml.

Each file is a fragment for the preamble of a xelatex or lualatex document
(pandoc's latex template, through header-includes): every color token as an
xcolor color named `theme-<role>`, the page and text colors, the token fonts
loaded from fonts/, and links, headings and table rules recolored. LaTeX has
no alpha channel, so translucent tokens are composited over the theme's
`bg` (themes_common.opaque_colors).

The fonts are loaded by file, from `\\sharedthemesfontdir`, which defaults to
shared/shared-themes/fonts/ (the mount point every consumer uses, relative
to where the engine runs); a consumer elsewhere defines it before including
the theme.
"""

from __future__ import annotations

import shutil
import sys

from themes_common import (
    ROOT,
    check_declared_outputs,
    font_family,
    load_themes,
    opaque_colors,
)

LATEX_DIR = ROOT / "latex"
FONTS_DIR = ROOT / "fonts"

# The font files a role is set from: the upright and bold weights fonts/
# ships for it. No italics are shipped, so italics are a slanted upright.
FONT_FACES: dict[str, tuple[str, str]] = {
    "font-sans": ("Regular", "Bold"),
    "font-mono": ("Regular", "SemiBold"),
}

RULES = """\
% Set in the preamble, the text color becomes LaTeX's default color, which
% the page headers and footers return to as well.
\\pagecolor{theme-bg}
\\color{theme-text-primary}

% Links: pandoc's template sets hidelinks unless colorlinks is given, and
% applies its \\hypersetup after the header-includes, so this runs later.
\\AtBeginDocument{\\hypersetup{
  colorlinks=true,
  linkcolor=theme-accent,
  urlcolor=theme-accent,
  citecolor=theme-accent,
  filecolor=theme-accent,
}}

% Headings in the accent, as on the sites; the title stays text-primary.
% titlesec's starred form keeps the class's spacing and changes only the font.
\\usepackage{titlesec}
\\titleformat*{\\section}{\\normalfont\\Large\\bfseries\\color{theme-accent}}
\\titleformat*{\\subsection}{\\normalfont\\large\\bfseries\\color{theme-accent}}
\\titleformat*{\\subsubsection}{\\normalfont\\normalsize\\bfseries\\color{theme-accent}}

% Table rules (booktabs, which pandoc's tables use, honors colortbl).
\\usepackage{colortbl}
\\arrayrulecolor{theme-border}
"""


def font_stem(role: str, value: str) -> str:
    """The file stem fonts/ uses for a role's family: 'JetBrains Mono' -> JetBrainsMono."""
    stem = font_family(value).replace(" ", "")
    for weight in FONT_FACES[role]:
        path = FONTS_DIR / f"{stem}-{weight}.ttf"
        if not path.is_file():
            sys.exit(f"{role}: {path.relative_to(ROOT)} does not exist")
    return stem


def emit_fonts(base: dict[str, str]) -> list[str]:
    sans = font_stem("font-sans", base["font-sans"])
    mono = font_stem("font-mono", base["font-mono"])
    sans_upright, sans_bold = FONT_FACES["font-sans"]
    mono_upright, mono_bold = FONT_FACES["font-mono"]
    sans_options = (
        "Path=\\sharedthemesfontdir, Extension=.ttf, "
        f"UprightFont=*-{sans_upright}, BoldFont=*-{sans_bold}, "
        f"ItalicFont=*-{sans_upright}, ItalicFeatures={{FakeSlant=0.2}}, "
        f"BoldItalicFont=*-{sans_bold}, BoldItalicFeatures={{FakeSlant=0.2}}"
    )
    mono_options = (
        "Path=\\sharedthemesfontdir, Extension=.ttf, Scale=MatchLowercase, "
        f"UprightFont=*-{mono_upright}, BoldFont=*-{mono_bold}, "
        f"ItalicFont=*-{mono_upright}, ItalicFeatures={{FakeSlant=0.2}}, "
        f"BoldItalicFont=*-{mono_bold}, BoldItalicFeatures={{FakeSlant=0.2}}"
    )
    return [
        "% Fonts, by file: fontspec needs xelatex or lualatex.",
        "\\usepackage{iftex}",
        "\\RequireTUTeX",
        "\\providecommand{\\sharedthemesfontdir}{shared/shared-themes/fonts/}",
        "\\usepackage{fontspec}",
        f"\\setmainfont{{{sans}}}[{sans_options}]",
        f"\\setsansfont{{{sans}}}[{sans_options}]",
        f"\\setmonofont{{{mono}}}[{mono_options}]",
    ]


def emit_theme(code: str, label: str, base: dict[str, str], tokens: dict[str, str]) -> str:
    lines = [
        f"% shared-themes/latex/{code}.tex",
        "%",
        "% GENERATED FROM themes.yaml — do not edit by hand.",
        "% Run scripts/yaml_to_latex.py after editing themes.yaml.",
        "%",
        f"% LaTeX theme \"{code}\" ({label}): the shared design tokens for the preamble",
        "% of a xelatex or lualatex document, e.g. pandoc's header-includes.",
        "",
        "\\usepackage{xcolor}",
    ]
    for name, rgb in opaque_colors(tokens).items():
        lines.append(f"\\definecolor{{theme-{name}}}{{HTML}}{{{rgb}}}")
    lines.append("")
    lines.extend(emit_fonts(base))
    lines.append("")
    lines.append(RULES)
    return "\n".join(lines)


def main() -> int:
    data = load_themes()
    if LATEX_DIR.exists():
        shutil.rmtree(LATEX_DIR)
    LATEX_DIR.mkdir()
    written = []
    for code, tokens in data.themes.items():
        path = LATEX_DIR / f"{code}.tex"
        path.write_text(emit_theme(code, data.labels[code], data.base, tokens))
        written.append(path)
    check_declared_outputs(written)
    print(f"wrote {LATEX_DIR.relative_to(ROOT)}/ ({len(written)} LaTeX themes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
