/* shared-themes/theme-onload.js: apply the reader's theme before paint (doc/files.md). */
(function () {
    var THEME_STORAGE_KEY = "veltzer-site-theme";
    var DARK_THEME = "midnight";
    var theme = null;
    try {
        theme = localStorage.getItem(THEME_STORAGE_KEY);
    } catch {
        // storage unavailable: fall through to the system preference
    }
    if (theme === "auto") {
        theme = null;
    }
    if (!theme && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        theme = DARK_THEME;
    }
    if (theme) {
        document.documentElement.setAttribute("data-theme", theme);
    }
})();
