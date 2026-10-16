# shared-themes

Design tokens and a theme switcher shared by every site and document the
fleet publishes: veltzer.github.io (built with rssite), the teaching-*
repos (teaching-slides, teaching-syllabi, teaching-animations), the
syllabi rspandoc renders, and the marp decks rsslide renders.

It is a token library, not a layout. Six named palettes
(`azure`, `paper`, `midnight`, `nord`, `solarized`, `rosepine`) are
exposed as CSS custom properties; every consumer keeps its own HTML,
templates and layout and takes only the colors, fonts, radii, shadows and
transitions from here. That is what lets a web site, a slide deck and a
printed syllabus look like one family without sharing a line of markup.

For a full breakdown of every file's role, see
[`doc/files.md`](doc/files.md).

## Files

- `themes.yaml` — **source of truth.** Base tokens (radius, font,
  transition, default shadow) and the six themes, each with a `label`
  (its display name) and its tokens.
- `themes.css` — *generated.* The tokens as CSS custom properties, one
  block per theme scoped to `[data-theme="<code>"]`. **Azure is the
  canonical default**, applied to `:root` too, so it shows even when no
  `data-theme` attribute is set. Azure matches the blue palette used on
  veltzer.github.io.
- `themes.json` — *generated.* The same data for consumers without a
  YAML parser: rssite templates (`load_data`), Rust tools, Lua filters.
  Themes are a list in file order, each `{code, label, tokens}`.
- `theme.py`, `manim_themes.py` — *generated.* The palette as Python,
  for scripts that need it outside the browser, and as a Manim module.
- `marp/<code>.css` — *generated.* One marp theme per palette, built on
  marp's `default` theme. A deck selects one with `theme: <code>`.
- `base.css`, `typography.css`, `components.css` — hand-written CSS
  layers for the sites that want the same reset, headings and widgets.
  Every value in them is a `var(--<role>)` token.
- `theme-switcher.js` — vanilla-JS helper that wires a
  `<select id="theme-select">` to the `data-theme` attribute on `<html>`
  and persists the choice in `localStorage`.
- `diagram-themes.yaml`, `diagram_theme.py` — source and generated
  Python for how SVG diagrams look (colors, gradients, drop shadows,
  typography, markers). Separate from the page themes above.
- `design-tokens.grit`, `biome-tokens.jsonc` — the biome rules that
  forbid raw colors, fonts, radii and shadows in a consumer's CSS.

## The consumer contract

Every consumer relies on the same four facts, so a theme chosen on one
site follows the reader to the next.

1. Styling comes from `var(--<role>)` tokens that `themes.css` defines.
   A consumer never writes a raw color; the biome plugin enforces this
   (`biome lint --config-path shared/shared-themes/biome-tokens.jsonc`).
2. The active theme is the `data-theme` attribute on `<html>`. No
   attribute means the default theme.
3. The chosen theme is stored in `localStorage` under the single key
   `veltzer-site-theme`. Sibling sites on the same origin
   (veltzer.github.io) share it.
4. The list of themes, their order and their display names come from
   `themes.yaml` (or its generated twins), never from a hand-typed copy.

What a consumer copies into its published output: `themes.css` and
`theme-switcher.js`, plus whichever of `base.css`, `typography.css` and
`components.css` it uses.

## Use

Add the repo as a git submodule:

```bash
git submodule add https://github.com/veltzer/shared-themes shared/shared-themes
```

### Web sites

Link the tokens and the switcher, and build the `<select>` from
`themes.json` so the list is never retyped. In an rssite template:

```html
<link rel="stylesheet" href="{{ get_url(path='shared-themes/themes.css') }}">
{% set palette = load_data(path="shared/shared-themes/themes.json") %}
<select id="theme-select">
{% for theme in palette.themes %}
  <option value="{{ theme.code }}">{{ theme.label }}</option>
{% endfor %}
</select>
<script src="{{ get_url(path='shared-themes/theme-switcher.js') }}"></script>
<script>initThemeSwitcher();</script>
```

Azure applies with no JS running. Override the starting theme per app
with `initThemeSwitcher({ defaultTheme: "midnight" })`.

### Marp decks

Put the palette in the deck's front matter and hand the theme directory
to marp-cli:

```yaml
---
theme: azure
---
```

```bash
marp --theme-set shared/shared-themes/marp deck.md
```

rsslide, which renders the fleet's decks, keeps the `theme:` directive
when it imports a deck but does not apply a theme yet (its README lists
`theme` as planned). When it does, `themes.json` is the palette it should
read; until then its output is marp's default look.

### Documents (rspandoc or pandoc)

Pass `themes.css` as a stylesheet before the document's own:

```bash
rspandoc --standalone --embed-resources \
    --css=shared/shared-themes/themes.css --css=print/syllabus.css doc.md
```

A standalone document has no switcher, so it renders in the default
theme unless its own stylesheet sets `data-theme` or overrides tokens.

### Python

```python
from theme import THEMES, BASE, DEFAULT_THEME, THEME_NAMES, THEME_LABELS

bg = THEMES["azure"]["bg"]       # "#ffffff"
radius = BASE["radius"]          # "10px"
THEME_LABELS["rosepine"]         # "Rosé Pine"
```

## Editing themes

Edit `themes.yaml` (or `diagram-themes.yaml`), then regenerate every
output and run the checks:

```bash
rsconstruct build
```

Commit the source together with the regenerated outputs. CI runs the same
build and fails if a committed generated file is stale or untracked.

## Adding a new theme

Add an entry under `themes:` in `themes.yaml` with a `label` and every
token the default theme defines (`bg`, `accent`, ...); the generators
refuse a theme that is missing one, since consumers would see undefined
values when they switch. Then:

1. Add its `marp/<code>.css` to the `marp` processor's `output_files` and
   to the `generated_in_sync` list in `rsconstruct.toml`.
2. Run `rsconstruct build` and commit the new generated files with the
   source.

If the theme deserves a descriptive section banner in `themes.css` (for
example "Solarized (light)"), add it to `BANNERS` in
`scripts/yaml_to_css.py`; otherwise its label is used.
