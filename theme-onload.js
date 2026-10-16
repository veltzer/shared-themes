/*
 * shared-themes/theme-onload.js
 *
 * For a page that has no theme switcher of its own (a syllabus rendered by
 * pandoc, say): apply the theme the reader chose on a sibling site, so the
 * choice follows them here too. Reads the same localStorage key the
 * switcher (theme-switcher.js) writes and sets data-theme on <html>, which
 * is what themes.css keys its blocks on. Runs inline at the start of the
 * body, before any content is painted, so there is no flash of the default
 * theme. Storage that is blocked or empty leaves the default in place.
 */
(function () {
    var THEME_STORAGE_KEY = "veltzer-site-theme";
    try {
        var theme = localStorage.getItem(THEME_STORAGE_KEY);
        if (theme) {
            document.documentElement.setAttribute("data-theme", theme);
        }
    } catch (e) {
        // storage unavailable: the default theme from :root stays
    }
})();
