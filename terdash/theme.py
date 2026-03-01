"""Deep-sea blue color theme for TerDash."""

# ── Accent colors (softened for readability) ──
CYAN = "#56d4e8"
GREEN = "#48e06a"
YELLOW = "#f0d264"
ORANGE = "#f08c45"
PINK = "#e83e8c"
PURPLE = "#a855f7"

# Backward-compatible aliases
NEON_CYAN = CYAN
NEON_GREEN = GREEN
NEON_YELLOW = YELLOW
NEON_ORANGE = ORANGE
NEON_PINK = PINK
NEON_PURPLE = PURPLE

# ── Background shades (deep navy blue) ──
BG_DARK = "#0d1b2a"
BG_PANEL = "#152238"
BG_SURFACE = "#1c2d44"
BG_BORDER = "#233554"

# ── Text ──
TEXT_PRIMARY = "#e0e0ff"
TEXT_DIM = "#6a7a9a"
TEXT_MUTED = "#3a4a6a"

# ── Status colors ──
STATUS_OK = GREEN
STATUS_WARN = YELLOW
STATUS_CRITICAL = PINK
STATUS_DOWN = "#ff0040"

# ── Contribution heatmap (cyan gradient) ──
CONTRIB_LEVELS = [
    "#152238",   # level 0 — empty (matches panel bg)
    "#0f3b5c",   # level 1
    "#1a6b8a",   # level 2
    "#28a0a8",   # level 3
    "#56d4e8",   # level 4 — max
]

# ── Gauge gradient (green -> yellow -> orange -> pink) ──
GAUGE_COLORS = [
    GREEN,    # 0-25%
    YELLOW,   # 25-50%
    ORANGE,   # 50-75%
    PINK,     # 75-100%
]

# ── Panel accent colors (for left border bars) ──
PANEL_ACCENTS = {
    "contrib": CYAN,
    "streak": GREEN,
    "codetime": PURPLE,
    "cpu": ORANGE,
    "memory": PINK,
    "network": GREEN,
    "services": YELLOW,
    "subscriptions": CYAN,
}


def gauge_color(percent: float) -> str:
    """Return a color based on usage percentage."""
    if percent < 25:
        return GAUGE_COLORS[0]
    elif percent < 50:
        return GAUGE_COLORS[1]
    elif percent < 75:
        return GAUGE_COLORS[2]
    else:
        return GAUGE_COLORS[3]
