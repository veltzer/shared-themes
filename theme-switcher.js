/*
 * shared-themes/theme-switcher.js
 *
 * Wires up a <select id="theme-select"> to the data-theme attribute on
 * <html>, persisting the choice in localStorage under a single shared
 * key. All sibling sites on the same origin (veltzer.org/*) share the
 * theme: pick a theme on one, navigate to another, and the choice
 * follows you.
 *
 * The default theme is "paper" (set in themes.css). Override at runtime
 * with defaultTheme if a specific app wants a different starting theme:
 *   initThemeSwitcher({ defaultTheme: "midnight" });
 */
const THEME_STORAGE_KEY = "veltzer-site-theme";

function initThemeSwitcher(options) {
    options = options || {};
    const defaultTheme = options.defaultTheme || "paper";
    const sel = document.getElementById("theme-select");
    if (!sel) return;
    const saved = localStorage.getItem(THEME_STORAGE_KEY) || defaultTheme;

    function applyTheme(name) {
        document.documentElement.setAttribute("data-theme", name);
        sel.value = name;
        localStorage.setItem(THEME_STORAGE_KEY, name);
    }

    sel.addEventListener("change", function() {
        applyTheme(sel.value);
    });

    // Pick up changes made by sibling tabs/sites on the same origin.
    window.addEventListener("storage", function(e) {
        if (e.key === THEME_STORAGE_KEY && e.newValue) {
            applyTheme(e.newValue);
        }
    });

    applyTheme(saved);
}
