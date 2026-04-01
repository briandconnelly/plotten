from __future__ import annotations

from plotten.themes._elements import ElementText
from plotten.themes._theme import Theme


def theme_default(base_size: float | None = None) -> Theme:
    """Clean modern theme with white panel and subdued gridlines (all defaults)."""
    kw: dict = {"complete": True}
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_minimal(base_size: float | None = None) -> Theme:
    """Minimal theme — no panel fill, light grid, no axis lines."""
    kw: dict = {
        "panel_background": "none",
        "grid_color": "#cccccc",
        "axis_line_width": 0.0,
        "grid_line_width": 0.3,
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_dark(base_size: float | None = None) -> Theme:
    """Dark theme — dark backgrounds with light text and subtle grid lines."""
    kw: dict = {
        "background": "#2d2d2d",
        "panel_background": "#3d3d3d",
        "grid_color": "#555555",
        "title_color": "#ffffff",
        "subtitle_color": "#e0e0e0",
        "strip_text_color": "#e0e0e0",
        "axis_text": ElementText(color="#cccccc"),
        "axis_title": ElementText(color="#e0e0e0"),
        "plot_caption": ElementText(color="#999999"),
        "legend_title_element": ElementText(color="#e0e0e0"),
        "legend_text_element": ElementText(color="#cccccc"),
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_bw(base_size: float | None = None) -> Theme:
    """Black-and-white theme — white panel with black border, light grid."""
    kw: dict = {
        "panel_background": "#ffffff",
        "grid_color": "#d9d9d9",
        "grid_line_width": 0.3,
        "panel_border_color": "#000000",
        "panel_border_width": 1.0,
        "axis_line_x": True,
        "axis_line_y": True,
        "tick_length": 4.0,
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_classic(base_size: float | None = None) -> Theme:
    """Classic theme — white panel, bottom+left axis lines only, no grid."""
    kw: dict = {
        "panel_background": "#ffffff",
        "grid_major_x": False,
        "grid_major_y": False,
        "grid_minor_x": False,
        "grid_minor_y": False,
        "axis_line_x": True,
        "axis_line_y": True,
        "axis_line_width": 1.0,
        "tick_length": 4.0,
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_void(base_size: float | None = None) -> Theme:
    """Void theme — transparent everything, no axes/grid/labels."""
    kw: dict = {
        "background": "none",
        "panel_background": "none",
        "grid_major_x": False,
        "grid_major_y": False,
        "grid_minor_x": False,
        "grid_minor_y": False,
        "axis_line_x": False,
        "axis_line_y": False,
        "axis_line_width": 0.0,
        "tick_length": 0.0,
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    else:
        kw["tick_size"] = 0
    return Theme(**kw)


def theme_grey(base_size: float | None = None) -> Theme:
    """Classic ggplot2 default: grey background with white gridlines."""
    kw: dict = {
        "background": "#e5e5e5",
        "panel_background": "#ebebeb",
        "grid_color": "#ffffff",
        "grid_line_width": 0.8,
        "axis_line_width": 0,
        "panel_border_color": "#000000",
        "panel_border_width": 0.5,
        "strip_background": "#d9d9d9",
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_538(base_size: float | None = None) -> Theme:
    """FiveThirtyEight style — light grey background, bold title, white grid."""
    kw: dict = {
        "background": "#f0f0f0",
        "panel_background": "#f0f0f0",
        "grid_color": "#ffffff",
        "grid_line_width": 0.8,
        "grid_minor_x": False,
        "grid_minor_y": False,
        "axis_line_x": False,
        "axis_line_y": False,
        "font_family": "sans-serif",
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    else:
        kw["title_size"] = 18
    return Theme(**kw)


def theme_economist(base_size: float | None = None) -> Theme:
    """The Economist style — light blue-grey background, y-axis grid only."""
    kw: dict = {
        "background": "#d5e4eb",
        "panel_background": "#d5e4eb",
        "grid_major_x": False,
        "grid_minor_x": False,
        "grid_minor_y": False,
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    else:
        kw["title_size"] = 18
    return Theme(**kw)


def theme_tufte(base_size: float | None = None) -> Theme:
    """Edward Tufte minimal — no grid, thin axis lines, serif font."""
    kw: dict = {
        "background": "#ffffff",
        "panel_background": "none",
        "grid_major_x": False,
        "grid_major_y": False,
        "grid_minor_x": False,
        "grid_minor_y": False,
        "axis_line_x": True,
        "axis_line_y": True,
        "axis_line_width": 0.3,
        "tick_length": 4.0,
        "font_family": "serif",
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_seaborn(base_size: float | None = None) -> Theme:
    """Seaborn-inspired — white background, light grey grid, panel border."""
    kw: dict = {
        "background": "#ffffff",
        "panel_background": "#ffffff",
        "grid_color": "#eaeaf2",
        "grid_line_width": 0.8,
        "axis_line_x": False,
        "axis_line_y": False,
        "panel_border_color": "#cccccc",
        "panel_border_width": 1.0,
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_linedraw(base_size: float | None = None) -> Theme:
    """Line-drawing theme — white background with thin black lines everywhere."""
    kw: dict = {
        "panel_background": "#ffffff",
        "grid_color": "#d9d9d9",
        "grid_line_width": 0.3,
        "panel_border_color": "#000000",
        "panel_border_width": 0.5,
        "axis_line_x": True,
        "axis_line_y": True,
        "axis_line_width": 0.5,
        "tick_length": 4.0,
        "strip_background": "#d9d9d9",
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_light(base_size: float | None = None) -> Theme:
    """Light theme — light grey lines and axes, directing attention to the data."""
    kw: dict = {
        "panel_background": "#ffffff",
        "grid_color": "#d9d9d9",
        "grid_line_width": 0.3,
        "panel_border_color": "#999999",
        "panel_border_width": 0.5,
        "axis_line_x": True,
        "axis_line_y": True,
        "axis_line_width": 0.3,
        "tick_length": 4.0,
        "strip_background": "#d9d9d9",
        "strip_text_color": "#333333",
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_test(base_size: float | None = None) -> Theme:
    """Theme for visual unit tests — white background, black border, no grid."""
    kw: dict = {
        "background": "#ffffff",
        "panel_background": "#ffffff",
        "grid_major_x": False,
        "grid_major_y": False,
        "grid_minor_x": False,
        "grid_minor_y": False,
        "panel_border_color": "#000000",
        "panel_border_width": 0.5,
        "axis_line_x": True,
        "axis_line_y": True,
        "axis_line_width": 0.5,
        "tick_length": 4.0,
        "complete": True,
    }
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


# American spelling alias
theme_gray = theme_grey
