/*
 * shared-themes/theme-switcher.js
 *
 * Wires up a <select id="theme-select"> to the data-theme attribute on
 * <html>, persisting the choice in localStorage under a single shared
 * key. All sibling sites on the same origin (veltzer.github.io/*) share the
 * theme: pick a theme on one, navigate to another, and the choice
 * follows you.
 *
 * A reader who has never chosen gets the theme their system asks for:
 * DARK_THEME under prefers-color-scheme: dark, LIGHT_THEME otherwise, and it
 * follows the system while they have not chosen. Only a choice made in the
 * select is stored. The two names are `default` and `default-dark` in
 * themes.yaml; scripts/yaml_to_css.py fails when they drift. An app that
 * wants one starting theme whatever the system says passes defaultTheme:
 *   initThemeSwitcher({ defaultTheme: "midnight" });
 */
const THEME_STORAGE_KEY = "veltzer-site-theme";
const LIGHT_THEME = "azure";
const DARK_THEME = "midnight";

function initThemeSwitcher(options) {
    options = options || {};
    const sel = document.getElementById("theme-select");
    if (!sel) return;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

    // The theme for a reader who has not chosen one.
    function unchosenTheme() {
        if (options.defaultTheme) return options.defaultTheme;
        return prefersDark.matches ? DARK_THEME : LIGHT_THEME;
    }
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

    function showTheme(name) {
        document.documentElement.setAttribute("data-theme", name);
        setSelValue(name);
    }

    function applyTheme(name) {
        showTheme(name);
        localStorage.setItem(THEME_STORAGE_KEY, name);
    }

    sel.addEventListener("change", function() {
        applyTheme(sel.value);
    });

    // Follow the system between light and dark until the reader chooses.
    prefersDark.addEventListener("change", function() {
        if (!localStorage.getItem(THEME_STORAGE_KEY)) {
            showTheme(unchosenTheme());
        }
    });

    // Pick up changes made by sibling tabs/sites on the same origin.
    window.addEventListener("storage", function(e) {
        if (e.key === THEME_STORAGE_KEY && e.newValue) {
            applyTheme(e.newValue);
        }
    });

    showTheme(localStorage.getItem(THEME_STORAGE_KEY) || unchosenTheme());
}

// Loaded via a classic <script src>, so consumers call this as a global
// (see README). Publish it explicitly rather than relying on top-level
// declarations leaking onto window.
window.initThemeSwitcher = initThemeSwitcher;
