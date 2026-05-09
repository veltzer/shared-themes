# shared-themes

CSS variables and a theme switcher shared across the teaching-* repos
(teaching-slides, teaching-syllabi, teaching-animations).

## Files

- `themes.yaml` — **source of truth.** Base tokens (radius, font,
  transition) and the six named themes (`azure`, `paper`, `midnight`,
  `nord`, `solarized`, `rosepine`).
- `themes.css` — *generated* from `themes.yaml`. Six theme blocks
  exposed as CSS custom properties. **Azure is the canonical default**,
  applied to `:root` so it shows even when no `data-theme` attribute is
  set. Azure matches the blue palette used on veltzer.github.io (the
  MkDocs Material blog).
- `theme.py` — *generated* from `themes.yaml`. Same data as a Python
  dict, for scripts that need the palette outside the browser.
- `scripts/yaml_to_css.py`, `scripts/yaml_to_python.py` — generators.
  Re-run after editing `themes.yaml`. CI fails if either output is out
  of sync.
- `theme-switcher.js` — vanilla-JS helper that wires a
  `<select id="theme-select">` to the `data-theme` attribute on `<html>`
  and persists the choice in `localStorage`.

## Editing themes

Edit `themes.yaml`, then regenerate:

```bash
python3 scripts/yaml_to_css.py
python3 scripts/yaml_to_python.py
```

Commit `themes.yaml` together with the regenerated `themes.css` and
`theme.py`. CI verifies they match.

## Using from Python

```python
from theme import THEMES, BASE, DEFAULT_THEME, THEME_NAMES

bg = THEMES["azure"]["bg"]      # "#ffffff"
radius = BASE["radius"]          # "10px"
```

## Use

Add as a git submodule:

```bash
git submodule add https://github.com/veltzer/shared-themes shared/shared-themes
```

Import the themes in your CSS:

```css
@import url('../shared/shared-themes/themes.css');
```

That's it for styling — azure applies by default. Users can flip themes
via the switcher.

In your HTML, include the switcher and call it after the DOM is ready:

```html
<script src="shared/shared-themes/theme-switcher.js"></script>
<script>
  initThemeSwitcher();
</script>
```

The `<select id="theme-select">` should list `<option value="azure">`
etc. for each theme you want to expose. The chosen theme is persisted
under a single shared `localStorage` key (`veltzer-site-theme`) so
sibling sites on the same origin share preferences. The default is
azure; override per-app with `initThemeSwitcher({ defaultTheme: "midnight" })`.

## Adding a new theme

Add a new entry under `themes:` in `themes.yaml`, defining every
variable already defined in the existing themes (`bg`, `accent`, etc.)
so consumers don't see undefined values when they switch. Then run the
two generators above and commit the regenerated outputs.

If the new theme deserves a section banner in the generated `themes.css`
(e.g. "Solarized (light)"), add it to the `BANNERS` dict at the top of
`scripts/yaml_to_css.py`. Themes without an entry get a plain banner.
