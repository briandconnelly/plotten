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


def theme_bw() -> Theme:
    """Black-and-white theme — white panel with black border, light grid."""
    return Theme(
        panel_background="#ffffff",
        grid_color="#d9d9d9",
        grid_line_width=0.3,
        panel_border_color="#000000",
        panel_border_width=1.0,
    )


def theme_classic() -> Theme:
    """Classic theme — white panel, bottom+left axis lines only, no grid."""
    return Theme(
        panel_background="#ffffff",
        grid_major_x=False,
        grid_major_y=False,
        grid_minor_x=False,
        grid_minor_y=False,
        axis_line_width=1.0,
    )


def theme_void() -> Theme:
    """Void theme — transparent everything, no axes/grid/labels."""
    return Theme(
        background="none",
        panel_background="none",
        grid_major_x=False,
        grid_major_y=False,
        grid_minor_x=False,
        grid_minor_y=False,
        axis_line_x=False,
        axis_line_y=False,
        axis_line_width=0.0,
        tick_length=0.0,
        tick_size=0,
    )
