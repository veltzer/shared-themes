/*
 * shared-themes/theme-switcher.js
 *
 * Wires up a <select id="theme-select"> to the data-theme attribute on
 * <html>, persisting the choice in localStorage. Call once after the DOM
 * is ready.
 *
 * Usage:
 *   initThemeSwitcher({ storageKey: "my-app-theme" });
 *
 * The default theme is "paper" (set in themes.css). Override per-app
 * with defaultTheme if you really need a different starting theme:
 *   initThemeSwitcher({ storageKey: "my-app-theme", defaultTheme: "midnight" });
 */
function initThemeSwitcher(options) {
    const storageKey = options.storageKey;
    const defaultTheme = options.defaultTheme || "paper";
    const sel = document.getElementById("theme-select");
    if (!sel) return;
    const saved = localStorage.getItem(storageKey) || defaultTheme;

    function applyTheme(name) {
        document.documentElement.setAttribute("data-theme", name);
        sel.value = name;
        localStorage.setItem(storageKey, name);
    }

    sel.addEventListener("change", function() {
        applyTheme(sel.value);
    });

    applyTheme(saved);
}
