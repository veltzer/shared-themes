# shared-themes

CSS variables and a theme switcher shared across the teaching-* repos
(teaching-slides, teaching-syllabi, teaching-animations).

## Files

- `themes.css` — five named themes (`paper`, `midnight`, `nord`,
  `solarized`, `rosepine`) exposed as CSS custom properties.
- `theme-switcher.js` — vanilla-JS helper that wires a
  `<select id="theme-select">` to the `data-theme` attribute on `<html>`
  and persists the choice in `localStorage`.

## Use

Add as a git submodule:

```bash
git submodule add https://github.com/veltzer/shared-themes shared/shared-themes
```

In your CSS, import the themes:

```css
@import url('../shared/shared-themes/themes.css');

/* pick a default by aliasing :root onto one theme */
:root {
  --bg: var(--bg);  /* placeholder; or set data-theme on <html> */
}
```

Easiest: set the default by adding `data-theme="paper"` (or whichever)
to `<html>` directly, then load `themes.css`.

In your HTML:

```html
<script src="shared/shared-themes/theme-switcher.js"></script>
<script>
  initThemeSwitcher({
    storageKey: "my-app-theme",
    defaultTheme: "paper"
  });
</script>
```

The `<select id="theme-select">` should list `<option value="paper">`
etc. for each theme you want to expose.

## Adding a new theme

Add a new `[data-theme="<name>"]` block to `themes.css`. Each block must
define every variable already defined in the existing themes
(`--bg`, `--accent`, `--green`, etc.) so consumers don't see undefined
values when they switch.
