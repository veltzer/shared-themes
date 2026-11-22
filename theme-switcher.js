/*
 * shared-themes/theme-switcher.js
 *
 * Wires up a <select id="theme-select"> to the data-theme attribute on
 * <html>, persisting the choice in localStorage under a single shared
 * key. All sibling sites on the same origin (veltzer.github.io/*) share the
 * theme: pick a theme on one, navigate to another, and the choice
 * follows you.
 *
 * The select opens with an Auto entry, which the script adds itself (so
 * no consumer's markup changes) and which is the default: the theme the
 * system asks for, DARK_THEME under prefers-color-scheme: dark, LIGHT_THEME
 * otherwise, following the system as it changes. Auto stores nothing;
 * choosing it removes a stored choice, which is how a reader who once
 * picked a theme goes back to following their system. Only a named theme
 * is stored. The two names are `default` and `default-dark` in themes.yaml;
 * scripts/yaml_to_css.py fails when they drift. The entry's label is
 * AUTO_LABEL, or options.autoLabel.
 *
 * An app that wants one starting theme whatever the system says passes
 * defaultTheme, and gets no Auto entry, since nothing then follows the
 * system:
 *   initThemeSwitcher({ defaultTheme: "midnight" });
 */
const THEME_STORAGE_KEY = "veltzer-site-theme";
const LIGHT_THEME = "azure";
const DARK_THEME = "midnight";
const AUTO_THEME = "auto";
const AUTO_LABEL = "Auto";

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

    // Storage can be blocked (private modes, a browser set to refuse site
    // data): reading or writing it then throws. The theme still switches
    // for the page; it is only not remembered, and the script that called
    // initThemeSwitcher goes on running.
    function storedTheme() {
        try {
            const name = localStorage.getItem(THEME_STORAGE_KEY);
            return name === AUTO_THEME ? null : name;
        } catch (e) {
            return null;
        }
    }

    function storeTheme(name) {
        try {
            if (name === AUTO_THEME) {
                localStorage.removeItem(THEME_STORAGE_KEY);
            } else {
                localStorage.setItem(THEME_STORAGE_KEY, name);
            }
        } catch (e) {
            // not remembered
        }
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

    // The Auto entry, first in the list, unless the app fixed its starting
    // theme or its markup already carries one.
    const offerAuto = !options.defaultTheme;
    if (offerAuto && !sel.querySelector('[value="' + AUTO_THEME + '"]')) {
        const label = options.autoLabel || AUTO_LABEL;
        let entry;
        if (isMaterial) {
            entry = document.createElement("md-select-option");
            const headline = document.createElement("div");
            headline.setAttribute("slot", "headline");
            headline.textContent = label;
            entry.appendChild(headline);
        } else {
            entry = document.createElement("option");
            entry.textContent = label;
        }
        entry.setAttribute("value", AUTO_THEME);
        sel.insertBefore(entry, sel.firstElementChild);
    }

    // Show a theme: a named one as itself, Auto as the system's light or
    // dark, with Auto selected in the list.
    function showTheme(name) {
        const auto = name === AUTO_THEME;
        document.documentElement.setAttribute("data-theme", auto ? unchosenTheme() : name);
        setSelValue(name);
    }

    function applyTheme(name) {
        showTheme(name);
        storeTheme(name);
    }

    function currentTheme() {
        return storedTheme() || (offerAuto ? AUTO_THEME : unchosenTheme());
    }

    sel.addEventListener("change", function() {
        applyTheme(sel.value);
    });

    // Follow the system between light and dark while on Auto.
    prefersDark.addEventListener("change", function() {
        if (!storedTheme()) {
            showTheme(currentTheme());
        }
    });

    // Pick up changes made by sibling tabs/sites on the same origin: a theme
    // chosen there, or Auto (the key removed).
    window.addEventListener("storage", function(e) {
        if (e.key === THEME_STORAGE_KEY) {
            showTheme(currentTheme());
        }
    });

    showTheme(currentTheme());
}

// Loaded via a classic <script src>, so consumers call this as a global
// (see README). Publish it explicitly rather than relying on top-level
// declarations leaking onto window.
window.initThemeSwitcher = initThemeSwitcher;
