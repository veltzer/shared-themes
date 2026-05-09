"""
shared-themes/manim_themes.py

GENERATED FROM themes.yaml — do not edit by hand.
Run scripts/yaml_to_manim.py after editing themes.yaml.

Exposes design tokens by role (what they're used for), not by implementation.
Consumers import this module directly:

    from manim_themes import T, BASE, apply_defaults

    apply_defaults()                      # sets bg + Text defaults

    Text("hello", color=T.ACCENT)
    Text("code", color=T.TEXT_PRIMARY, font=BASE["font-mono"])

The active theme is picked from $ANIM_THEME (validated), falling back to
DEFAULT_THEME.
"""

from __future__ import annotations

import os

from manim import ManimColor


DEFAULT_THEME: str = 'azure'

BASE: dict[str, object] = {
    'radius-xs': '4px',
    'radius-sm': '6px',
    'radius': '10px',
    'radius-pill': '20px',
    'transition': '180ms cubic-bezier(0.4, 0, 0.2, 1)',
    'transition-slow': '350ms ease',
    'font-sans': 'Outfit',
    'font-mono': 'JetBrains Mono',
    'shadow': '0 1px 3px rgba(0,0,0,0.4), 0 4px 12px rgba(0,0,0,0.25)',
}

THEMES: dict[str, dict[str, object]] = {
    'azure': {
        'bg': ManimColor("#ffffff"),
        'bg-surface': ManimColor("#f5f5f7"),
        'bg-elevated': ManimColor("#eaeaef"),
        'bg-hover': ManimColor("#dcdce5"),
        'border': ManimColor("#d0d0db"),
        'border-subtle': ManimColor("#ececf2"),
        'text-primary': ManimColor((0, 0, 0, int(round(0.87 * 255)))),
        'text-secondary': ManimColor((0, 0, 0, int(round(0.54 * 255)))),
        'text-muted': ManimColor((0, 0, 0, int(round(0.32 * 255)))),
        'accent': ManimColor("#4051b5"),
        'accent-dim': ManimColor((64, 81, 181, int(round(0.12 * 255)))),
        'success': ManimColor("#1c7d4d"),
        'success-dim': ManimColor((28, 125, 77, int(round(0.12 * 255)))),
        'warning': ManimColor("#b87d1a"),
        'warning-dim': ManimColor((184, 125, 26, int(round(0.12 * 255)))),
        'danger': ManimColor("#c72c34"),
        'danger-dim': ManimColor((199, 44, 52, int(round(0.12 * 255)))),
        'gradient-start': ManimColor("#303fa1"),
        'gradient-end': ManimColor("#526cfe"),
        'shadow': '0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06)',
    },
    'paper': {
        'bg': ManimColor("#faf8f5"),
        'bg-surface': ManimColor("#f0ede8"),
        'bg-elevated': ManimColor("#e8e4de"),
        'bg-hover': ManimColor("#ddd8d0"),
        'border': ManimColor("#cdc6bb"),
        'border-subtle': ManimColor("#e0dbd4"),
        'text-primary': ManimColor("#2c2824"),
        'text-secondary': ManimColor("#706860"),
        'text-muted': ManimColor("#a09888"),
        'accent': ManimColor("#9b6b3e"),
        'accent-dim': ManimColor((155, 107, 62, int(round(0.12 * 255)))),
        'success': ManimColor("#3a8a5c"),
        'success-dim': ManimColor((58, 138, 92, int(round(0.12 * 255)))),
        'warning': ManimColor("#b87d1a"),
        'warning-dim': ManimColor((184, 125, 26, int(round(0.12 * 255)))),
        'danger': ManimColor("#c05040"),
        'danger-dim': ManimColor((192, 80, 64, int(round(0.12 * 255)))),
        'gradient-start': ManimColor("#2c2824"),
        'gradient-end': ManimColor("#9b6b3e"),
        'shadow': '0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06)',
    },
    'midnight': {
        'bg': ManimColor("#0f1117"),
        'bg-surface': ManimColor("#161922"),
        'bg-elevated': ManimColor("#1e2130"),
        'bg-hover': ManimColor("#252940"),
        'border': ManimColor("#2a2e3f"),
        'border-subtle': ManimColor("#1e2130"),
        'text-primary': ManimColor("#e8eaf0"),
        'text-secondary': ManimColor("#8b90a0"),
        'text-muted': ManimColor("#5c6070"),
        'accent': ManimColor("#6c8cff"),
        'accent-dim': ManimColor((108, 140, 255, int(round(0.12 * 255)))),
        'success': ManimColor("#34d399"),
        'success-dim': ManimColor((52, 211, 153, int(round(0.12 * 255)))),
        'warning': ManimColor("#fbbf24"),
        'warning-dim': ManimColor((251, 191, 36, int(round(0.12 * 255)))),
        'danger': ManimColor("#f87171"),
        'danger-dim': ManimColor((248, 113, 113, int(round(0.12 * 255)))),
        'gradient-start': ManimColor("#e8eaf0"),
        'gradient-end': ManimColor("#6c8cff"),
    },
    'nord': {
        'bg': ManimColor("#2e3440"),
        'bg-surface': ManimColor("#3b4252"),
        'bg-elevated': ManimColor("#434c5e"),
        'bg-hover': ManimColor("#4c566a"),
        'border': ManimColor("#4c566a"),
        'border-subtle': ManimColor("#434c5e"),
        'text-primary': ManimColor("#eceff4"),
        'text-secondary': ManimColor("#d8dee9"),
        'text-muted': ManimColor("#7b88a1"),
        'accent': ManimColor("#88c0d0"),
        'accent-dim': ManimColor((136, 192, 208, int(round(0.15 * 255)))),
        'success': ManimColor("#a3be8c"),
        'success-dim': ManimColor((163, 190, 140, int(round(0.15 * 255)))),
        'warning': ManimColor("#ebcb8b"),
        'warning-dim': ManimColor((235, 203, 139, int(round(0.15 * 255)))),
        'danger': ManimColor("#bf616a"),
        'danger-dim': ManimColor((191, 97, 106, int(round(0.15 * 255)))),
        'gradient-start': ManimColor("#eceff4"),
        'gradient-end': ManimColor("#88c0d0"),
    },
    'solarized': {
        'bg': ManimColor("#fdf6e3"),
        'bg-surface': ManimColor("#eee8d5"),
        'bg-elevated': ManimColor("#e6dfcb"),
        'bg-hover': ManimColor("#ddd6c1"),
        'border': ManimColor("#d0c8b0"),
        'border-subtle': ManimColor("#e6dfcb"),
        'text-primary': ManimColor("#073642"),
        'text-secondary': ManimColor("#586e75"),
        'text-muted': ManimColor("#93a1a1"),
        'accent': ManimColor("#268bd2"),
        'accent-dim': ManimColor((38, 139, 210, int(round(0.12 * 255)))),
        'success': ManimColor("#859900"),
        'success-dim': ManimColor((133, 153, 0, int(round(0.12 * 255)))),
        'warning': ManimColor("#b58900"),
        'warning-dim': ManimColor((181, 137, 0, int(round(0.12 * 255)))),
        'danger': ManimColor("#dc322f"),
        'danger-dim': ManimColor((220, 50, 47, int(round(0.12 * 255)))),
        'gradient-start': ManimColor("#073642"),
        'gradient-end': ManimColor("#268bd2"),
        'shadow': '0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)',
    },
    'rosepine': {
        'bg': ManimColor("#191724"),
        'bg-surface': ManimColor("#1f1d2e"),
        'bg-elevated': ManimColor("#26233a"),
        'bg-hover': ManimColor("#312e47"),
        'border': ManimColor("#393552"),
        'border-subtle': ManimColor("#26233a"),
        'text-primary': ManimColor("#e0def4"),
        'text-secondary': ManimColor("#908caa"),
        'text-muted': ManimColor("#6e6a86"),
        'accent': ManimColor("#c4a7e7"),
        'accent-dim': ManimColor((196, 167, 231, int(round(0.14 * 255)))),
        'success': ManimColor("#9ccfd8"),
        'success-dim': ManimColor((156, 207, 216, int(round(0.14 * 255)))),
        'warning': ManimColor("#f6c177"),
        'warning-dim': ManimColor((246, 193, 119, int(round(0.14 * 255)))),
        'danger': ManimColor("#eb6f92"),
        'danger-dim': ManimColor((235, 111, 146, int(round(0.14 * 255)))),
        'gradient-start': ManimColor("#e0def4"),
        'gradient-end': ManimColor("#c4a7e7"),
    },
}

THEME_NAMES: list[str] = list(THEMES)


class _T:
    """Attribute-style view onto the active palette.

    Role keys from themes.yaml are exposed as UPPER_SNAKE identifiers:
    bg-surface -> BG_SURFACE, text-primary -> TEXT_PRIMARY, accent-dim ->
    ACCENT_DIM, etc. Values are ManimColor for color roles and plain strings
    for non-color roles (e.g. shadow).
    """

    def __init__(self, palette: dict[str, object]) -> None:
        for key, value in palette.items():
            setattr(self, key.replace("-", "_").upper(), value)


ACTIVE_THEME: str = os.environ.get("ANIM_THEME", DEFAULT_THEME)
if ACTIVE_THEME not in THEMES:
    raise SystemExit(
        f"ANIM_THEME={ACTIVE_THEME!r} is not a known theme. "
        f"Known: {sorted(THEMES)}"
    )

T = _T(THEMES[ACTIVE_THEME])


def apply_defaults() -> None:
    """Boot the current Manim scene to use the active theme.

    Sets config.background_color to T.BG and Text/MathTex/Tex color defaults
    to T.TEXT_PRIMARY. Text additionally gets the sans font role as its
    default family.
    """
    from manim import MathTex, Tex, Text, config

    config.background_color = T.BG
    Text.set_default(color=T.TEXT_PRIMARY, font=BASE["font-sans"])
    MathTex.set_default(color=T.TEXT_PRIMARY)
    Tex.set_default(color=T.TEXT_PRIMARY)
