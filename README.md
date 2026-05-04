# shared-themes

CSS variables and a theme switcher shared across the teaching-* repos
(teaching-slides, teaching-syllabi, teaching-animations).

## Files

- `themes.css` — five named themes (`paper`, `midnight`, `nord`,
  `solarized`, `rosepine`) exposed as CSS custom properties. **Paper is
  the canonical default**, applied to `:root` so it shows even when no
  `data-theme` attribute is set.
- `theme-switcher.js` — vanilla-JS helper that wires a
  `<select id="theme-select">` to the `data-theme` attribute on `<html>`
  and persists the choice in `localStorage`.

## Use

Add as a git submodule:

```bash
git submodule add https://github.com/veltzer/shared-themes shared/shared-themes
```

Import the themes in your CSS:

```css
@import url('../shared/shared-themes/themes.css');
```

That's it for styling — paper applies by default. Users can flip themes
via the switcher.

In your HTML, include the switcher and call it after the DOM is ready:

```html
<script src="shared/shared-themes/theme-switcher.js"></script>
<script>
  initThemeSwitcher({ storageKey: "my-app-theme" });
</script>
```

The `<select id="theme-select">` should list `<option value="paper">`
etc. for each theme you want to expose. The `storageKey` is required so
each app keeps its own preference. To override the canonical paper
default, pass `defaultTheme: "midnight"` (or whichever) to
`initThemeSwitcher`.

## Adding a new theme

Add a new `[data-theme="<name>"]` block to `themes.css`. Each block must
define every variable already defined in the existing themes
(`--bg`, `--accent`, `--green`, etc.) so consumers don't see undefined
values when they switch.
