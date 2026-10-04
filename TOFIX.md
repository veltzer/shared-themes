# TOFIX

Findings from a code scan on 2026-10-04.

## Medium

- `doc/files.md:92` - says rsconstruct.toml has "Two `explicit` processors, one per generator", but `rsconstruct.toml:16-43` has four: css, python, manim (`scripts/yaml_to_manim.py` -> `manim_themes.py`) and `generated_in_sync` (`scripts/check_generated_in_sync.py`). The doc never mentions `manim_themes.py`, `yaml_to_manim.py` or the sync-check script at all; add sections for them and fix the count.
- `README.md:9` - the "Files" list and the "Editing themes" regenerate commands (`README.md:30-35`) cover only `themes.css` and `theme.py`; the third generated artifact `manim_themes.py` (and `python3 scripts/yaml_to_manim.py`) is missing, so following the README by hand leaves it stale and the `generated_in_sync` check fails. Add it, or point readers at `rsconstruct build` instead.
- `themes.yaml:4` - the header lists only `themes.css` and `theme.py` as generated artifacts; add `manim_themes.py (via scripts/yaml_to_manim.py)`.

## Low

- `config/project.lua:3` - DESCRIPTION_SHORT lists five themes "(paper, midnight, nord, solarized, rosepine)" and omits `azure`, which is the canonical default (`themes.yaml:8`). Add it.
- `theme-switcher.js:6` - comment says sibling sites share the theme on "the same origin (veltzer.org/*)"; the consuming Pages sites are served from veltzer.github.io (as `README.md:17` already says). Update the comment.
