# File roles

Reference for what each file in this repo is responsible for, whether
it's hand-written or generated, and how the pieces fit together.

## Source of truth

### `themes.yaml`
Hand-written. Single source of truth for the design tokens.

Contents:
- `default:` — name of the theme that also applies to `:root`.
- `base:` — tokens shared across all themes (`radius-*`, `font-*`,
  `transition*`, default dark-theme `shadow`).
- `themes:` — per-theme palettes (`bg`, `accent`, `text-primary`, …).
  Each theme must define every variable; missing keys produce
  inconsistent CSS at theme-switch time.

Edit this file when changing colors, adding a theme, or tweaking the
shared radius/font/transition tokens. After editing, run the generators
(see below) and commit `themes.yaml` together with the regenerated
outputs. CI fails if they're out of sync.

## Generated outputs

### `themes.css` — *generated from `themes.yaml`*
CSS custom properties for all themes. The default theme is emitted as a
combined selector (`:root, [data-theme="azure"] { … }`) so it applies
even when no `data-theme` attribute is set.

Consumers `@import` this from their own CSS. Do not edit by hand —
changes will be overwritten on the next build.

### `theme.py` — *generated from `themes.yaml`*
Same data as `themes.css`, exposed to Python:

```python
from theme import THEMES, BASE, DEFAULT_THEME, THEME_NAMES

THEMES["azure"]["bg"]   # "#ffffff"
BASE["radius"]          # "10px"
DEFAULT_THEME           # "azure"
```

For Python scripts that need the palette outside the browser
(matplotlib, PIL, SVG generation, terminal output, …). Do not edit by
hand.

## Hand-written CSS layers

### `base.css`
Reset, body styling, links, scrollbars, mobile breakpoint. Pulls in the
Google Fonts (`Outfit`, `JetBrains Mono`) used by the typography layer.
Loaded by every consuming site. Contains *no* design tokens — those all
live in `themes.css`.

### `typography.css`
Headings (`h1`, `h2`), `#total-count`, `.subtitle`, `.count`,
`.no-results`, `.build-info`. Same look across all consuming sites.

### `components.css`
Common UI components: header bar, filters, dropdowns, text inputs,
toggle switch, breadcrumbs, badges, subfolder cards, autocomplete,
download icon, item lists. Site-specific components (e.g. a video
player) belong in the consuming site's own CSS, not here.

## JavaScript

### `theme-switcher.js`
Vanilla JS. Wires a `<select id="theme-select">` to the `data-theme`
attribute on `<html>` and persists the choice in `localStorage` under a
shared key (`veltzer-site-theme`) so sibling sites on the same origin
share the preference. Call `initThemeSwitcher()` after the DOM is
ready; pass `{ defaultTheme: "midnight" }` to override per app.

## Generators

### `scripts/yaml_to_css.py`
Reads `themes.yaml` and writes `themes.css`. Section banners for known
themes are configured via the `BANNERS` dict at the top of the script;
themes without an entry get a plain banner. Run after editing
`themes.yaml`, or via `rsconstruct build`.

### `scripts/yaml_to_python.py`
Reads `themes.yaml` and writes `theme.py`. Emits `THEMES`, `BASE`,
`DEFAULT_THEME`, and `THEME_NAMES`. Run after editing `themes.yaml`,
or via `rsconstruct build`.

## Build and CI

### `rsconstruct.toml`
RSConstruct build config. Two `explicit` processors, one per generator,
each declaring `themes.yaml` and the script as inputs and the
generated file as the output. Build commands:

```bash
rsconstruct build       # regenerate stale outputs
rsconstruct status      # see what's stale
rsconstruct clean       # remove outputs
```

### `.github/workflows/lint.yml`
Two jobs:
- **stylelint** — lints `base.css`, `typography.css`, `components.css`,
  and the allowlist fixture.
- **generated-in-sync** — re-runs both generators and fails if
  `themes.css` or `theme.py` differs from what's committed. This is the
  drift guard for the YAML-as-source-of-truth setup.

### `test_stylelint_allowlist.css`
Fixture, not a real stylesheet. References every role token allowed by
the stylelint config. If a token is removed from `themes.yaml` but left
in stylelint's allowlist (or vice versa), this file goes out of sync
and stylelint fails. Empty stylelint output = config and tokens agree.

## Top-level

### `README.md`
User-facing intro: how to add the repo as a submodule, import the
files, wire up the switcher. For internal file roles, see this doc.

### `.gitignore`
Excludes `__pycache__/`, `*.pyc`, `*.pyo`, and `/.rsconstruct/` (the
build cache).
