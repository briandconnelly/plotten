from __future__ import annotations

from plotten.themes._theme import Theme


def theme_default() -> Theme:
    """Clean theme with a light gray panel background (all defaults)."""
    return Theme()


def theme_minimal() -> Theme:
    """Minimal theme — no panel fill, light grid, no axis lines."""
    return Theme(
        panel_background="none",
        grid_color="#cccccc",
        axis_line_width=0.0,
        grid_line_width=0.3,
    )


def theme_dark() -> Theme:
    """Dark theme — dark backgrounds with subtle grid lines.

    Note: light-colored text adjustments should be handled at render time.
    """
    return Theme(
        background="#2d2d2d",
        panel_background="#3d3d3d",
        grid_color="#555555",
    )
