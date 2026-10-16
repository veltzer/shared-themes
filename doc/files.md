# File roles

Reference for what each file in this repo is responsible for, whether
it's hand-written or generated, and how the pieces fit together.

## Source of truth

### `themes.yaml`
Hand-written. Single source of truth for the design tokens.

Contents:
- `default:` — code of the theme that also applies to `:root`.
- `base:` — tokens shared across all themes (`radius-*`, `font-*`,
  `transition*`, default dark-theme `shadow`).
- `themes:` — one entry per theme: a `label` (the display name a switcher
  shows), a `description` (a short hint, "dark blue", that a switcher may
  show after the label and that heads the theme's block in `themes.css`)
  and the tokens (`bg`, `accent`, `text-primary`, ...). Every
  theme must define every token the default theme defines unless `base:`
  provides a fallback; the loader refuses to generate otherwise, because
  a missing key would show as an undefined value at theme-switch time.

Edit this file when changing colors, adding a theme, or tweaking the
shared radius/font/transition tokens. After editing, run
`rsconstruct build` and commit `themes.yaml` together with the
regenerated outputs. CI fails if they're out of sync.

### `diagram-themes.yaml`
Hand-written. Single source of truth for how SVG diagrams look, separate
from the page themes above. Each named diagram theme is a complete
palette: `colors` (the semantic roles `{family}-fill`, `-border`, `-text`,
`-accent` and the neutrals), `gradients`, `shadow`, `effects`
(`rect-fill`: solid or gradient), `typography`, `markers`, `shapes`,
`lines`. Whether boxes cast a drop shadow, and how big it is, is the
theme's `shadow`: `{dx, dy, blur, color, apply-to}`, or `none`.

A theme may `extends: <other>`: mappings merge key by key, anything else
(lists, scalars, `shadow: none`) replaces. `default:` names the theme a
consumer gets when it picks none.

## Generated outputs

All of these are rewritten by `rsconstruct build`. Do not edit them by
hand; changes are overwritten on the next build.

### `themes.css` — *generated from `themes.yaml`*
CSS custom properties for all themes. The default theme is emitted as a
combined selector (`:root, [data-theme="azure"] { … }`) so it applies
even when no `data-theme` attribute is set. Each block is headed by the
theme's label and description; otherwise the CSS carries tokens only.

Consumers link this from their pages.

### `themes.json` — *generated from `themes.yaml`*
The same data as JSON, for consumers that read a palette without a YAML
parser: rssite templates through `load_data`, Rust tools such as rsslide,
Lua filters. Themes are a list in file order so a switcher built from it
keeps the intended order:

```json
{
  "default": "azure",
  "base": {"radius": "10px", "...": "..."},
  "themes": [
    {"code": "azure", "label": "Azure", "description": "cool light, indigo",
     "tokens": {"bg": "#ffffff", "...": "..."}}
  ]
}
```

### `theme.py` — *generated from `themes.yaml`*
Same data as `themes.css`, exposed to Python:

```python
from theme import THEMES, BASE, DEFAULT_THEME, THEME_NAMES, THEME_LABELS, THEME_DESCRIPTIONS

THEMES["azure"]["bg"]     # "#ffffff"
BASE["radius"]            # "10px"
DEFAULT_THEME             # "azure"
THEME_LABELS["rosepine"]        # "Rosé Pine"
THEME_DESCRIPTIONS["rosepine"]  # "purple dark"
```

For Python scripts that need the palette outside the browser
(matplotlib, PIL, SVG generation, terminal output, …).

### `manim_themes.py` — *generated from `themes.yaml`*
The palette as a Manim module. Colors are `ManimColor` values and font
roles are bare family names. `T` is an attribute view onto the active
theme (`T.ACCENT`, `T.TEXT_PRIMARY`), picked from `$ANIM_THEME` with
`DEFAULT_THEME` as the fallback, and `apply_defaults()` sets the scene's
background and `Text` defaults. `THEME_LABELS` and `THEME_DESCRIPTIONS`
are there too.

### `marp/<code>.css` — *generated from `themes.yaml`*
One marp theme per palette, named by the theme code (`/* @theme azure */`).
Each imports marp's built-in `default` theme, declares every token on
`section` (marp scopes a theme to the slide element), maps marp's own
`--color-background`, `--color-foreground`, `--color-highlight` and
friends onto the tokens, and adds the few rules the default theme does
not route through a variable (links, code font, block quotes, tables,
header and footer). A deck selects one with `theme: <code>` in its front
matter and marp-cli loads the directory with `--theme-set marp`. rsslide
does not apply themes yet; see the README.

Adding a theme to `themes.yaml` means adding its file to the `marp`
processor's `output_files` and to the sync check in `rsconstruct.toml`.

### `diagram_theme.py` — *generated from `diagram-themes.yaml`*
The diagram themes with `extends` resolved:

```python
from diagram_theme import DIAGRAM_THEMES, DEFAULT_DIAGRAM_THEME

DIAGRAM_THEMES["muted"]["shadow"]   # {"dx": 0, "dy": 4, "blur": 8, ...}
DIAGRAM_THEMES["flat"]["shadow"]    # "none"
```

## Fonts

### `fonts/` — *written by `scripts/fetch_fonts.py`*
The fonts the tokens name, as committed files: Outfit in the five weights
the sites use and JetBrains Mono in two, each as `.woff2` (for the web)
and `.ttf` (for rsslide and rspandoc, which draw text themselves and need
font files). `OFL-Outfit.txt` and `OFL-JetBrainsMono.txt` are the SIL
Open Font License texts the redistribution requires. `SOURCES.md` records
upstream, release, URL and SHA-256 of every file.

### `fonts.css` — *generated by `scripts/fetch_fonts.py`*
One `@font-face` per `.woff2` file, with URLs relative to the file, so a
consumer publishes `fonts.css` and `fonts/` side by side. Generated from
the same list the script fetches, so the CSS and the files cannot drift.
Holds raw font names by design and is not linted with the token rules.

## Hand-written CSS layers

### `base.css`
Reset, body styling, links, scrollbars, mobile breakpoint. Loaded by every
consuming site. Contains *no* design tokens — those all live in
`themes.css` — and fetches nothing: the fonts come from `fonts.css`.

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

All generators live in `scripts/` and run as plain scripts from the repo
root; `rsconstruct build` runs them in the right order.

### `scripts/themes_common.py`
The loader every `themes.yaml` generator imports. Reads the YAML, splits
each theme into its `label`, its `description` and its tokens, and
validates: the default theme exists, every theme has a label and a
description, every theme defines every token the default theme defines
unless `base:` has a fallback. A generator
never sees a broken palette.

### `scripts/yaml_to_css.py`
Writes `themes.css`. Each theme's block is headed by its label and
description from `themes.yaml`; the default theme's banner says so.

### `scripts/yaml_to_json.py`
Writes `themes.json`.

### `scripts/yaml_to_python.py`
Writes `theme.py` (`THEMES`, `BASE`, `DEFAULT_THEME`, `THEME_NAMES`,
`THEME_LABELS`, `THEME_DESCRIPTIONS`).

### `scripts/yaml_to_manim.py`
Writes `manim_themes.py`. Hex and `rgb()`/`rgba()` values become
`ManimColor` expressions; font roles are reduced to the bare family name.

### `scripts/yaml_to_marp.py`
Writes `marp/<code>.css` for every theme, replacing the directory's
previous contents. The marp variable mapping and the extra rules are the
`MARP_VARS` and `RULES` constants at the top of the script.

### `scripts/fetch_fonts.py`
Fetches the fonts from their upstream releases (Outfit from its repo tree,
JetBrains Mono from its release zip) into `fonts/`, with licences and
`SOURCES.md`, and writes `fonts.css`. A one-time tool with the upstream
versions as constants; not in `rsconstruct.toml`, so a build never touches
the network for a font. Re-run to move to a newer release and commit the
diff.

### `scripts/diagram_themes_to_python.py`
Reads `diagram-themes.yaml`, resolves `extends`, checks that every theme
has its required keys and a valid `shadow`, and writes `diagram_theme.py`
(`DIAGRAM_THEMES`, `DEFAULT_DIAGRAM_THEME`, `DIAGRAM_THEME_NAMES`).

### `scripts/check_generated_in_sync.py`
The drift guard. Runs after every generator and fails the build when a
generated file is untracked (`git ls-files`) or differs from the index
(`git diff`), so a stale or forgotten output never ships. rsconstruct
appends `--inputs` and `--output-files` to its command line, so the file
list it checks ends at the first flag.

## Build and CI

### `rsconstruct.toml`
RSConstruct build config. One `explicit` processor per generator, each
declaring its YAML source, the script and (for the `themes.yaml`
generators) `scripts/themes_common.py` as inputs and the generated files
as outputs; the `generated_in_sync` processor runs the drift guard over
all of them. Checkers: ruff on `scripts/`, biome on the hand-written
stylesheets, oxlint on the switcher, yamllint, actionlint, rumdl. Build
commands:

```bash
rsconstruct build       # regenerate stale outputs and run the checks
rsconstruct status      # see what's stale
rsconstruct clean       # remove outputs
```

### `.github/workflows/build.yml`
Runs `rsconstruct build`, which among other things lints `base.css`,
`typography.css`, `components.css` and the allowlist fixture with biome
and checks that the generated files match their YAML sources (the drift
guard for the YAML-as-source-of-truth setup).

### `design-tokens.grit` and `biome-tokens.jsonc`
The design-token rules, as a biome GritQL plugin: colors, fonts, radii,
shadows and transitions must come from `var(--<role>)` tokens, and raw
hex colors, named colors and `rgb()`/`hsl()`-style functions are
forbidden. `biome-tokens.jsonc` loads the plugin with every built-in rule
off. The consuming repos lint their stylesheets with the same file through
their `shared/shared-themes` submodule
(`biome lint --config-path shared/shared-themes/biome-tokens.jsonc`).
`themes.css` and `marp/*.css` hold the raw values by design and are not
linted with it.

### `test_tokens_allowlist.css`
Fixture, not a real stylesheet. References every role token allowed by
`design-tokens.grit`. If a token is removed from `themes.yaml` but left
in the plugin's allowlist (or vice versa), this file goes out of sync
and the biome check fails. Empty biome output = rules and tokens agree.

## Top-level

### `README.md`
User-facing intro: the consumer contract, how to add the repo as a
submodule, and how each kind of consumer (site, marp deck, document,
Python) picks up the themes. For internal file roles, see this doc.

### `.gitignore`
Excludes `__pycache__/`, `*.pyc`, `*.pyo`, and `/.rsconstruct/` (the
build cache).
