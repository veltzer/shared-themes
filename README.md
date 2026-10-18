# shared-themes

Design tokens and a theme switcher shared by every site and document the
fleet publishes: veltzer.github.io (built with rssite), the teaching-*
repos (teaching-slides, teaching-syllabi, teaching-animations), the
syllabi rspandoc renders (HTML, PDF and Word), and the marp decks rsslide
renders.

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
  (its display name), a `description` (a short hint such as "dark blue")
  and its tokens.
- `themes.css` — *generated.* The tokens as CSS custom properties, one
  block per theme scoped to `[data-theme="<code>"]`. **Azure is the
  canonical default**, applied to `:root` too, so it shows even when no
  `data-theme` attribute is set. Azure matches the blue palette used on
  veltzer.github.io.
- `themes.json` — *generated.* The same data for consumers without a
  YAML parser: rssite templates (`load_data`), Rust tools, Lua filters.
  Themes are a list in file order, each `{code, label, description, tokens}`.
- `theme.py`, `manim_themes.py` — *generated.* The palette as Python,
  for scripts that need it outside the browser, and as a Manim module.
- `marp/<code>.css` — *generated.* One marp theme per palette, built on
  marp's `default` theme. A deck selects one with `theme: <code>`.
- `latex/<code>.tex` — *generated.* One LaTeX preamble theme per palette
  for xelatex/lualatex: the tokens as xcolor colors (`theme-<role>`), the
  page and text colors, the fonts from `fonts/`, and links, headings and
  table rules recolored.
- `docx/<code>.docx` — *generated.* One Word reference document per light
  palette (dark ones would need a page background, which pandoc drops),
  for pandoc's `--reference-doc`.
- `fonts/`, `fonts.css` — the fonts the tokens name (Outfit, JetBrains
  Mono) as committed files, woff2 for the web and ttf for the PDF tools,
  with their SIL OFL licences and a provenance table, and the generated
  `@font-face` declarations. `scripts/fetch_fonts.py` fetches them from
  the upstream releases; nothing is fetched at page view or at build.
- `base.css`, `typography.css`, `components.css` — hand-written CSS
  layers for the sites that want the same reset, headings and widgets.
  Every value in them is a `var(--<role>)` token.
- `shared_themes.py` — the consumer helper for sites that inline the
  shared layers into one page: the layers concatenated in order, the
  switcher, the theme `<select>` entries from `themes.json`, and the copy
  of `fonts/` beside the page. One implementation instead of one per
  consumer.
- `theme-switcher.js` — vanilla-JS helper that wires a
  `<select id="theme-select">` to the `data-theme` attribute on `<html>`
  and persists the choice in `localStorage`.
- `theme-onload.js` — for a page with no switcher (a pandoc-rendered
  syllabus): applies the stored choice on load, so the theme follows the
  reader from the sites that have one.
- `diagram-themes.yaml`, `diagram_theme.py`, `diagram-themes.json` —
  source and generated Python and JSON for how SVG diagrams look (colors,
  gradients, drop shadows, typography, markers). Separate from the page
  themes above, but tied to them: for every diagram theme and every page
  palette the generator derives a variant `<theme>-<palette>` with the
  diagram's neutrals taken from the palette (`palette-neutrals` says which
  token feeds which role), so a renderer that knows the deck's palette
  (rsslide) can make a diagram follow the slide.
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

What a consumer copies into its published output: `themes.css`,
`theme-switcher.js`, `fonts.css` and the `fonts/` directory beside it
(the URLs in `fonts.css` are relative to it), plus whichever of
`base.css`, `typography.css` and `components.css` it uses. A tool that
renders PDF points at the `.ttf` files in `fonts/`.

## Use

Add the repo as a git submodule:

```bash
git submodule add https://github.com/veltzer/shared-themes shared/shared-themes
```

### Web sites

Link the tokens and the switcher, and build the `<select>` from
`themes.json` so the list is never retyped. In an rssite template:

```html
<link rel="stylesheet" href="{{ get_url(path='shared-themes/fonts.css') }}">
<link rel="stylesheet" href="{{ get_url(path='shared-themes/themes.css') }}">
{% set palette = load_data(path="shared/shared-themes/themes.json") %}
<select id="theme-select">
{% for theme in palette.themes %}
  <option value="{{ theme.code }}">{{ theme.label }} ({{ theme.description }})</option>
{% endfor %}
</select>
<script src="{{ get_url(path='shared-themes/theme-switcher.js') }}"></script>
<script>initThemeSwitcher();</script>
```

Azure applies with no JS running. Override the starting theme per app
with `initThemeSwitcher({ defaultTheme: "midnight" })`.

### Self-contained pages

A site that inlines the shared CSS into one HTML file, as the teaching
index pages do, loads `shared_themes.py` from the submodule and lets it
do the four things such a page needs:

```python
st.css()                          # fonts.css + themes.css + base + typography + components
st.js()                           # theme-switcher.js
st.theme_options(material_web=True)  # the <select> entries, labels and hints
st.publish_fonts(site_dir)        # fonts/ beside the page
```

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

A standalone document has no switcher. To make the reader's choice from
the sites follow them into the document, put `theme-onload.js` inline at
the start of the body; a Lua filter can do that with a raw HTML block (the
teaching syllabi do), which works in pandoc and rspandoc alike. Without
it the document renders in the default theme.

A PDF goes through LaTeX, which never sees the CSS. Render it with xelatex
(or lualatex) and put `latex/<code>.tex` in the preamble:

```bash
pandoc --pdf-engine=xelatex \
    --include-in-header=shared/shared-themes/latex/azure.tex doc.md -o doc.pdf
```

When one pandoc command line serves several formats, `--include-in-header`
would also paste the LaTeX into the HTML head; a Lua filter can add the file
to `header-includes` as a raw `latex` block instead, which every other
writer drops (the teaching syllabi do this). Run from the directory that
holds `shared/`, or define `\sharedthemesfontdir` first: the fonts load
from `shared/shared-themes/fonts/` relative to it.

A Word document takes its styles from a reference document:

```bash
pandoc --reference-doc=shared/shared-themes/docx/azure.docx doc.md -o doc.docx
```

Only the light palettes have one. Print has no switcher, so a document
picks its palette when it is built; the syllabi use the default, azure.

### Python

```python
from theme import THEMES, BASE, DEFAULT_THEME, THEME_NAMES, THEME_LABELS

bg = THEMES["azure"]["bg"]       # "#ffffff"
radius = BASE["radius"]          # "10px"
THEME_LABELS["rosepine"]         # "Rosé Pine"
```

## Updating the fonts

Bump the version constants in `scripts/fetch_fonts.py`, run it, and commit
the diff under `fonts/` together with `fonts.css` and `fonts/SOURCES.md`:

```bash
scripts/fetch_fonts.py
```

It is a one-time tool, not part of the build.

## Editing themes

Edit `themes.yaml` (or `diagram-themes.yaml`), then regenerate every
output and run the checks:

```bash
rsconstruct build
```

Commit the source together with the regenerated outputs. CI runs the same
build and fails if a committed generated file is stale or untracked.

## Adding a new theme

Add an entry under `themes:` in `themes.yaml` with a `label`, a
`description` and every token the default theme defines (`bg`, `accent`, ...); the generators
refuse a theme that is missing one, since consumers would see undefined
values when they switch. Then:

1. Add its `marp/<code>.css` to the `marp` processor's `output_files` and
   to the `generated_in_sync` list in `rsconstruct.toml`.
2. Do the same with its `latex/<code>.tex` (the `latex` processor) and,
   if its background is light, its `docx/<code>.docx` (the `docx`
   processor). The docx generator decides light from the background's
   luminance, so a mismatch with the list fails the build.
3. Run `rsconstruct build` and commit the new generated files with the
   source.

The banner over the theme's block in `themes.css` is its label and
description; there is nothing else to name.
