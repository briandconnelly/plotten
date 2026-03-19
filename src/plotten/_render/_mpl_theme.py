"""Panel rendering: background, grid, spines, ticks, and layer drawing."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from plotten.themes._text_props import text_props

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._render._resolve import ResolvedPanel, ResolvedPlot
    from plotten._types import GeomDrawData, GeomParams
    from plotten.themes._theme import Theme


def render_panel(
    panel: ResolvedPanel,
    ax: Axes,
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Draw layers and apply theme to a single axes."""
    # Background
    if theme.panel_background != "none":
        ax.set_facecolor(theme.panel_background)
    else:
        ax.set_facecolor("none")

    # Grid — element overrides take precedence
    from plotten.themes._elements import ElementBlank, ElementLine

    grid_major_x = theme.grid_major_x
    grid_major_y = theme.grid_major_y
    grid_minor_x = theme.grid_minor_x
    grid_minor_y = theme.grid_minor_y

    # Element overrides for grid
    if isinstance(theme.panel_grid_major, ElementBlank):
        grid_major_x = False
        grid_major_y = False
    if isinstance(theme.panel_grid_minor, ElementBlank):
        grid_minor_x = False
        grid_minor_y = False

    major_grid_color = theme.grid_color
    major_grid_width = theme.grid_line_width
    if isinstance(theme.panel_grid_major, ElementLine):
        if theme.panel_grid_major.color is not None:
            major_grid_color = theme.panel_grid_major.color
        if theme.panel_grid_major.size is not None:
            major_grid_width = theme.panel_grid_major.size

    minor_grid_color = theme.grid_color
    minor_grid_width = theme.grid_line_width * 0.5
    if isinstance(theme.panel_grid_minor, ElementLine):
        if theme.panel_grid_minor.color is not None:
            minor_grid_color = theme.panel_grid_minor.color
        if theme.panel_grid_minor.size is not None:
            minor_grid_width = theme.panel_grid_minor.size

    # Clear any default grid, then apply per-axis
    ax.grid(False)
    if grid_major_x:
        ax.xaxis.grid(True, which="major", color=major_grid_color, linewidth=major_grid_width)
    if grid_major_y:
        ax.yaxis.grid(True, which="major", color=major_grid_color, linewidth=major_grid_width)
    if grid_minor_x or grid_minor_y:
        ax.minorticks_on()
        if grid_minor_x:
            ax.xaxis.grid(True, which="minor", color=minor_grid_color, linewidth=minor_grid_width)
        if grid_minor_y:
            ax.yaxis.grid(True, which="minor", color=minor_grid_color, linewidth=minor_grid_width)
    ax.set_axisbelow(True)

    # Spine styling (polar axes have different spine names)
    is_polar_ax = ax.name == "polar"
    for spine in ax.spines.values():
        spine.set_linewidth(theme.axis_line_width)

    # Axis line visibility
    if not is_polar_ax:
        axis_line_x = theme.axis_line_x
        axis_line_y = theme.axis_line_y
        ax.spines["bottom"].set_visible(axis_line_x)
        ax.spines["top"].set_visible(axis_line_x)
        ax.spines["left"].set_visible(axis_line_y)
        ax.spines["right"].set_visible(axis_line_y)

    # Panel border
    panel_border_color = theme.panel_border_color
    panel_border_width = theme.panel_border_width
    if panel_border_color is not None:
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(panel_border_color)
            spine.set_linewidth(panel_border_width)

    # Tick styling — per-axis sizes and rotation
    axis_text_kw = text_props(
        theme.axis_text,
        theme,
        default_size=theme.tick_size,
        default_color="#000000",
    )
    axis_text_x_size = theme.axis_text_x_size or axis_text_kw.get("fontsize", theme.tick_size)
    axis_text_y_size = theme.axis_text_y_size or axis_text_kw.get("fontsize", theme.tick_size)
    axis_text_x_rotation = theme.axis_text_x_rotation
    axis_text_y_rotation = theme.axis_text_y_rotation
    if "rotation" in axis_text_kw:
        axis_text_x_rotation = axis_text_kw["rotation"]
        axis_text_y_rotation = axis_text_kw["rotation"]

    ax.tick_params(
        axis="x",
        labelsize=axis_text_x_size,
        labelrotation=axis_text_x_rotation,
        labelcolor=axis_text_kw.get("color", "#000000"),
        length=theme.tick_length,
    )
    ax.tick_params(
        axis="y",
        labelsize=axis_text_y_size,
        labelrotation=axis_text_y_rotation,
        labelcolor=axis_text_kw.get("color", "#000000"),
        length=theme.tick_length,
    )
    # Apply font family to tick labels
    tick_family = axis_text_kw.get("fontfamily", theme.font_family)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(tick_family)

    # Draw layers
    coord = resolved.coord
    for layer in panel.layers:
        draw_data = cast("GeomDrawData", layer.data)
        if hasattr(coord, "transform_data"):
            draw_data = coord.transform_data(draw_data, resolved.scales)  # type: ignore[union-attr]
        draw_params = cast("GeomParams", layer.params)
        layer.geom.draw(draw_data, ax, draw_params)

    # Font — axis titles
    axis_title_kw = text_props(
        theme.axis_title,
        theme,
        default_size=theme.label_size,
        default_color="#000000",
    )
    axis_title_x_size = theme.axis_title_x_size or axis_title_kw.get("fontsize", theme.label_size)
    axis_title_y_size = theme.axis_title_y_size or axis_title_kw.get("fontsize", theme.label_size)

    ax.xaxis.label.set_fontfamily(axis_title_kw.get("fontfamily", theme.font_family))
    ax.yaxis.label.set_fontfamily(axis_title_kw.get("fontfamily", theme.font_family))
    ax.xaxis.label.set_fontsize(axis_title_x_size)
    ax.yaxis.label.set_fontsize(axis_title_y_size)
    if "fontweight" in axis_title_kw:
        ax.xaxis.label.set_fontweight(axis_title_kw["fontweight"])
        ax.yaxis.label.set_fontweight(axis_title_kw["fontweight"])
    if "fontstyle" in axis_title_kw:
        ax.xaxis.label.set_fontstyle(axis_title_kw["fontstyle"])
        ax.yaxis.label.set_fontstyle(axis_title_kw["fontstyle"])
    if "color" in axis_title_kw:
        ax.xaxis.label.set_color(axis_title_kw["color"])
        ax.yaxis.label.set_color(axis_title_kw["color"])
