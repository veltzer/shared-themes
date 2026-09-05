/*
 * shared-themes/theme-switcher.js
 *
 * Wires up a <select id="theme-select"> to the data-theme attribute on
 * <html>, persisting the choice in localStorage under a single shared
 * key. All sibling sites on the same origin (veltzer.org/*) share the
 * theme: pick a theme on one, navigate to another, and the choice
 * follows you.
 *
 * The default theme is "azure" (set in themes.css). Override at runtime
 * with defaultTheme if a specific app wants a different starting theme:
 *   initThemeSwitcher({ defaultTheme: "midnight" });
 */
const THEME_STORAGE_KEY = "veltzer-site-theme";

function initThemeSwitcher(options) {
    options = options || {};
    const defaultTheme = options.defaultTheme || "azure";
    const sel = document.getElementById("theme-select");
    if (!sel) return;
    const saved = localStorage.getItem(THEME_STORAGE_KEY) || defaultTheme;
    const isMaterial = sel.tagName.toLowerCase() === "md-outlined-select"
        || sel.tagName.toLowerCase() === "md-filled-select";

    function setSelValue(name) {
        if (isMaterial) {
            // For <md-outlined-select> we have to flip the `selected`
            // attribute on the matching <md-select-option> child, then
            // poke the host so it reflects the new selection.
            const opts = sel.querySelectorAll("md-select-option");
            opts.forEach(function(o) {
                if (o.value === name) {
                    o.setAttribute("selected", "");
                    o.selected = true;
                } else {
                    o.removeAttribute("selected");
                    o.selected = false;
                }
            });
            sel.value = name;
        } else {
            sel.value = name;
        }
    }

    function applyTheme(name) {
        document.documentElement.setAttribute("data-theme", name);
        setSelValue(name);
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

// Loaded via a classic <script src>, so consumers call this as a global
// (see README). Publish it explicitly rather than relying on top-level
// declarations leaking onto window.
window.initThemeSwitcher = initThemeSwitcher;
