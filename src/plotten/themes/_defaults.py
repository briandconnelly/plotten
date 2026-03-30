from __future__ import annotations

from plotten.themes._elements import ElementText
from plotten.themes._theme import Theme


def theme_default() -> Theme:
    """Clean modern theme with white panel and subdued gridlines (all defaults)."""
    return Theme(complete=True)


def theme_minimal() -> Theme:
    """Minimal theme — no panel fill, light grid, no axis lines."""
    return Theme(
        panel_background="none",
        grid_color="#cccccc",
        axis_line_width=0.0,
        grid_line_width=0.3,
        complete=True,
    )


def theme_dark() -> Theme:
    """Dark theme — dark backgrounds with light text and subtle grid lines."""
    return Theme(
        background="#2d2d2d",
        panel_background="#3d3d3d",
        grid_color="#555555",
        title_color="#ffffff",
        subtitle_color="#e0e0e0",
        strip_text_color="#e0e0e0",
        axis_text=ElementText(color="#cccccc"),
        axis_title=ElementText(color="#e0e0e0"),
        complete=True,
    )


def theme_bw() -> Theme:
    """Black-and-white theme — white panel with black border, light grid."""
    return Theme(
        panel_background="#ffffff",
        grid_color="#d9d9d9",
        grid_line_width=0.3,
        panel_border_color="#000000",
        panel_border_width=1.0,
        axis_line_x=True,
        axis_line_y=True,
        tick_length=4.0,
        complete=True,
    )


def theme_classic() -> Theme:
    """Classic theme — white panel, bottom+left axis lines only, no grid."""
    return Theme(
        panel_background="#ffffff",
        grid_major_x=False,
        grid_major_y=False,
        grid_minor_x=False,
        grid_minor_y=False,
        axis_line_x=True,
        axis_line_y=True,
        axis_line_width=1.0,
        tick_length=4.0,
        complete=True,
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
        complete=True,
    )


def theme_grey() -> Theme:
    """Classic ggplot2 default: grey background with white gridlines."""
    return Theme(
        background="#e5e5e5",
        panel_background="#ebebeb",
        grid_color="#ffffff",
        grid_line_width=0.8,
        axis_line_width=0,
        panel_border_color="#000000",
        panel_border_width=0.5,
        strip_background="#d9d9d9",
        complete=True,
    )


def theme_538() -> Theme:
    """FiveThirtyEight style — light grey background, bold title, white grid."""
    return Theme(
        background="#f0f0f0",
        panel_background="#f0f0f0",
        grid_color="#ffffff",
        grid_line_width=0.8,
        grid_minor_x=False,
        grid_minor_y=False,
        axis_line_x=False,
        axis_line_y=False,
        title_size=18,
        font_family="sans-serif",
        complete=True,
    )


def theme_economist() -> Theme:
    """The Economist style — light blue-grey background, y-axis grid only."""
    return Theme(
        background="#d5e4eb",
        panel_background="#d5e4eb",
        grid_major_x=False,
        grid_minor_x=False,
        grid_minor_y=False,
        title_size=18,
        complete=True,
    )


def theme_tufte() -> Theme:
    """Edward Tufte minimal — no grid, thin axis lines, serif font."""
    return Theme(
        background="#ffffff",
        panel_background="none",
        grid_major_x=False,
        grid_major_y=False,
        grid_minor_x=False,
        grid_minor_y=False,
        axis_line_x=True,
        axis_line_y=True,
        axis_line_width=0.3,
        tick_length=4.0,
        font_family="serif",
        complete=True,
    )


def theme_seaborn() -> Theme:
    """Seaborn-inspired — white background, light grey grid, panel border."""
    return Theme(
        background="#ffffff",
        panel_background="#ffffff",
        grid_color="#eaeaf2",
        grid_line_width=0.8,
        axis_line_x=False,
        axis_line_y=False,
        panel_border_color="#cccccc",
        panel_border_width=1.0,
        complete=True,
    )


def theme_linedraw() -> Theme:
    """Line-drawing theme — white background with thin black lines everywhere."""
    return Theme(
        panel_background="#ffffff",
        grid_color="#d9d9d9",
        grid_line_width=0.3,
        panel_border_color="#000000",
        panel_border_width=0.5,
        axis_line_x=True,
        axis_line_y=True,
        axis_line_width=0.5,
        tick_length=4.0,
        strip_background="#d9d9d9",
        complete=True,
    )


def theme_light() -> Theme:
    """Light theme — light grey lines and axes, directing attention to the data."""
    return Theme(
        panel_background="#ffffff",
        grid_color="#d9d9d9",
        grid_line_width=0.3,
        panel_border_color="#999999",
        panel_border_width=0.5,
        axis_line_x=True,
        axis_line_y=True,
        axis_line_width=0.3,
        tick_length=4.0,
        strip_background="#d9d9d9",
        strip_text_color="#333333",
        complete=True,
    )


def theme_test() -> Theme:
    """Theme for visual unit tests — white background, black border, no grid."""
    return Theme(
        background="#ffffff",
        panel_background="#ffffff",
        grid_major_x=False,
        grid_major_y=False,
        grid_minor_x=False,
        grid_minor_y=False,
        panel_border_color="#000000",
        panel_border_width=0.5,
        axis_line_x=True,
        axis_line_y=True,
        axis_line_width=0.5,
        tick_length=4.0,
        complete=True,
    )


# American spelling alias
theme_gray = theme_grey
