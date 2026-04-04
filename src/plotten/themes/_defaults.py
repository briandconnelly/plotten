from __future__ import annotations

from typing import Any

from plotten.themes._elements import ElementText
from plotten.themes._theme import Theme


def _make_theme(base_size: float | None, **kw: Any) -> Theme:
    """Create a complete theme, threading base_size if provided."""
    kw["complete"] = True
    if base_size is not None:
        kw["base_size"] = base_size
    return Theme(**kw)


def theme_default(base_size: float | None = None) -> Theme:
    """Clean modern theme with white panel and subdued gridlines (all defaults)."""
    return _make_theme(base_size)


def theme_minimal(base_size: float | None = None) -> Theme:
    """Minimal theme — no panel fill, light grid, no axis lines."""
    return _make_theme(
        base_size,
        panel_background="none",
        grid_color="#cccccc",
        axis_line_width=0.0,
        grid_line_width=0.3,
    )


def theme_dark(base_size: float | None = None) -> Theme:
    """Dark theme — dark backgrounds with light text and subtle grid lines."""
    return _make_theme(
        base_size,
        background="#2d2d2d",
        panel_background="#3d3d3d",
        grid_color="#555555",
        title_color="#ffffff",
        subtitle_color="#e0e0e0",
        strip_text_color="#e0e0e0",
        axis_text=ElementText(color="#cccccc"),
        axis_title=ElementText(color="#e0e0e0"),
        plot_caption=ElementText(color="#999999"),
        legend_title_element=ElementText(color="#e0e0e0"),
        legend_text_element=ElementText(color="#cccccc"),
    )


def theme_bw(base_size: float | None = None) -> Theme:
    """Black-and-white theme — white panel with black border, light grid."""
    return _make_theme(
        base_size,
        panel_background="#ffffff",
        grid_color="#d9d9d9",
        grid_line_width=0.3,
        panel_border_color="#000000",
        panel_border_width=1.0,
        axis_line_x=True,
        axis_line_y=True,
        tick_length=4.0,
    )


def theme_classic(base_size: float | None = None) -> Theme:
    """Classic theme — white panel, bottom+left axis lines only, no grid."""
    return _make_theme(
        base_size,
        panel_background="#ffffff",
        grid_major_x=False,
        grid_major_y=False,
        grid_minor_x=False,
        grid_minor_y=False,
        axis_line_x=True,
        axis_line_y=True,
        axis_line_width=1.0,
        tick_length=4.0,
    )


def theme_void(base_size: float | None = None) -> Theme:
    """Void theme — transparent everything, no axes/grid/labels."""
    kw: dict[str, Any] = {
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
    }
    if base_size is None:
        kw["tick_size"] = 0
    return _make_theme(base_size, **kw)


def theme_gray(base_size: float | None = None) -> Theme:
    """Classic ggplot2 default: gray background with white gridlines."""
    return _make_theme(
        base_size,
        background="#e5e5e5",
        panel_background="#ebebeb",
        grid_color="#ffffff",
        grid_line_width=0.8,
        axis_line_width=0,
        panel_border_color="#000000",
        panel_border_width=0.5,
        strip_background="#d9d9d9",
    )


def theme_538(base_size: float | None = None) -> Theme:
    """FiveThirtyEight style — light grey background, bold title, white grid."""
    kw: dict[str, Any] = {
        "background": "#f0f0f0",
        "panel_background": "#f0f0f0",
        "grid_color": "#ffffff",
        "grid_line_width": 0.8,
        "grid_minor_x": False,
        "grid_minor_y": False,
        "axis_line_x": False,
        "axis_line_y": False,
        "font_family": "sans-serif",
    }
    if base_size is None:
        kw["title_size"] = 18
    return _make_theme(base_size, **kw)


def theme_economist(base_size: float | None = None) -> Theme:
    """The Economist style — light blue-grey background, y-axis grid only."""
    kw: dict[str, Any] = {
        "background": "#d5e4eb",
        "panel_background": "#d5e4eb",
        "grid_major_x": False,
        "grid_minor_x": False,
        "grid_minor_y": False,
    }
    if base_size is None:
        kw["title_size"] = 18
    return _make_theme(base_size, **kw)


def theme_tufte(base_size: float | None = None) -> Theme:
    """Edward Tufte minimal — no grid, thin axis lines, serif font."""
    return _make_theme(
        base_size,
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
    )


def theme_seaborn(base_size: float | None = None) -> Theme:
    """Seaborn-inspired — white background, light grey grid, panel border."""
    return _make_theme(
        base_size,
        background="#ffffff",
        panel_background="#ffffff",
        grid_color="#eaeaf2",
        grid_line_width=0.8,
        axis_line_x=False,
        axis_line_y=False,
        panel_border_color="#cccccc",
        panel_border_width=1.0,
    )


def theme_linedraw(base_size: float | None = None) -> Theme:
    """Line-drawing theme — white background with thin black lines everywhere."""
    return _make_theme(
        base_size,
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
    )


def theme_light(base_size: float | None = None) -> Theme:
    """Light theme — light grey lines and axes, directing attention to the data."""
    return _make_theme(
        base_size,
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
    )


def theme_test(base_size: float | None = None) -> Theme:
    """Theme for visual unit tests — white background, black border, no grid.

    Intended for internal visual regression tests; for publication figures
    prefer :func:`theme_bw` or :func:`theme_classic`.
    """
    return _make_theme(
        base_size,
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
    )


# British spelling alias
theme_grey = theme_gray
