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

    # Global element overrides for grid
    if isinstance(theme.panel_grid_major, ElementBlank):
        grid_major_x = False
        grid_major_y = False
    if isinstance(theme.panel_grid_minor, ElementBlank):
        grid_minor_x = False
        grid_minor_y = False

    # Per-axis grid element overrides
    if isinstance(theme.panel_grid_major_x, ElementBlank):
        grid_major_x = False
    if isinstance(theme.panel_grid_major_y, ElementBlank):
        grid_major_y = False
    if isinstance(theme.panel_grid_minor_x, ElementBlank):
        grid_minor_x = False
    if isinstance(theme.panel_grid_minor_y, ElementBlank):
        grid_minor_y = False

    # Resolve grid colors and widths per axis
    major_grid_color_x = theme.grid_color
    major_grid_width_x = theme.grid_line_width
    major_grid_color_y = theme.grid_color
    major_grid_width_y = theme.grid_line_width

    # Global major grid element
    if isinstance(theme.panel_grid_major, ElementLine):
        if theme.panel_grid_major.color is not None:
            major_grid_color_x = theme.panel_grid_major.color
            major_grid_color_y = theme.panel_grid_major.color
        if theme.panel_grid_major.size is not None:
            major_grid_width_x = theme.panel_grid_major.size
            major_grid_width_y = theme.panel_grid_major.size

    # Per-axis major grid elements override global
    if isinstance(theme.panel_grid_major_x, ElementLine):
        if theme.panel_grid_major_x.color is not None:
            major_grid_color_x = theme.panel_grid_major_x.color
        if theme.panel_grid_major_x.size is not None:
            major_grid_width_x = theme.panel_grid_major_x.size
    if isinstance(theme.panel_grid_major_y, ElementLine):
        if theme.panel_grid_major_y.color is not None:
            major_grid_color_y = theme.panel_grid_major_y.color
        if theme.panel_grid_major_y.size is not None:
            major_grid_width_y = theme.panel_grid_major_y.size

    minor_grid_color_x = theme.grid_color
    minor_grid_width_x = theme.grid_line_width * 0.5
    minor_grid_color_y = theme.grid_color
    minor_grid_width_y = theme.grid_line_width * 0.5

    if isinstance(theme.panel_grid_minor, ElementLine):
        if theme.panel_grid_minor.color is not None:
            minor_grid_color_x = theme.panel_grid_minor.color
            minor_grid_color_y = theme.panel_grid_minor.color
        if theme.panel_grid_minor.size is not None:
            minor_grid_width_x = theme.panel_grid_minor.size
            minor_grid_width_y = theme.panel_grid_minor.size

    if isinstance(theme.panel_grid_minor_x, ElementLine):
        if theme.panel_grid_minor_x.color is not None:
            minor_grid_color_x = theme.panel_grid_minor_x.color
        if theme.panel_grid_minor_x.size is not None:
            minor_grid_width_x = theme.panel_grid_minor_x.size
    if isinstance(theme.panel_grid_minor_y, ElementLine):
        if theme.panel_grid_minor_y.color is not None:
            minor_grid_color_y = theme.panel_grid_minor_y.color
        if theme.panel_grid_minor_y.size is not None:
            minor_grid_width_y = theme.panel_grid_minor_y.size

    # Clear any default grid, then apply per-axis
    ax.grid(False)
    if grid_major_x:
        ax.xaxis.grid(True, which="major", color=major_grid_color_x, linewidth=major_grid_width_x)
    if grid_major_y:
        ax.yaxis.grid(True, which="major", color=major_grid_color_y, linewidth=major_grid_width_y)
    if grid_minor_x or grid_minor_y:
        ax.minorticks_on()
        if grid_minor_x:
            ax.xaxis.grid(
                True, which="minor", color=minor_grid_color_x, linewidth=minor_grid_width_x
            )
        if grid_minor_y:
            ax.yaxis.grid(
                True, which="minor", color=minor_grid_color_y, linewidth=minor_grid_width_y
            )
    ax.set_axisbelow(True)

    # Spine styling (polar axes have different spine names)
    is_polar_ax = ax.name == "polar"

    # Resolve axis line element properties
    line_width = theme.axis_line_width
    line_color = None
    if isinstance(theme.axis_line_element, ElementLine):
        if theme.axis_line_element.size is not None:
            line_width = theme.axis_line_element.size
        line_color = theme.axis_line_element.color

    for spine in ax.spines.values():
        spine.set_linewidth(line_width)
        if line_color is not None:
            spine.set_edgecolor(line_color)

    # Axis line visibility
    if not is_polar_ax:
        axis_line_x = theme.axis_line_x
        axis_line_y = theme.axis_line_y
        # ElementBlank on axis_line_element disables all
        if isinstance(theme.axis_line_element, ElementBlank):
            axis_line_x = False
            axis_line_y = False
        ax.spines["bottom"].set_visible(axis_line_x)
        ax.spines["top"].set_visible(axis_line_x)
        ax.spines["left"].set_visible(axis_line_y)
        ax.spines["right"].set_visible(axis_line_y)

    # Panel border
    panel_border_color = theme.panel_border_color
    panel_border_width = theme.panel_border_width
    if isinstance(theme.panel_border, ElementBlank):
        panel_border_color = None
    elif isinstance(theme.panel_border, type(None)):
        pass
    if panel_border_color is not None:
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(panel_border_color)
            spine.set_linewidth(panel_border_width)

    # Tick styling — resolve per-axis element overrides
    axis_text_kw = text_props(
        theme.axis_text,
        theme,
        default_size=theme.tick_size,
        default_color="#000000",
    )

    # Per-axis text element overrides (axis_text_x, axis_text_y)
    axis_text_x_kw = _resolve_per_axis_text(
        theme.axis_text_x,
        axis_text_kw,
        theme,
        size_override=theme.axis_text_x_size,
        rotation_override=theme.axis_text_x_rotation,
    )
    axis_text_y_kw = _resolve_per_axis_text(
        theme.axis_text_y,
        axis_text_kw,
        theme,
        size_override=theme.axis_text_y_size,
        rotation_override=theme.axis_text_y_rotation,
    )

    # Resolve tick lengths per-axis
    tick_length_x = theme.axis_ticks_length_x or theme.tick_length
    tick_length_y = theme.axis_ticks_length_y or theme.tick_length

    # Resolve tick visibility/styling from axis_ticks elements
    show_ticks_x = True
    show_ticks_y = True
    tick_color_x = axis_text_x_kw.get("color", "#000000")
    tick_color_y = axis_text_y_kw.get("color", "#000000")
    tick_width_x = line_width
    tick_width_y = line_width

    if isinstance(theme.axis_ticks, ElementBlank):
        show_ticks_x = False
        show_ticks_y = False
    elif isinstance(theme.axis_ticks, ElementLine):
        if theme.axis_ticks.color is not None:
            tick_color_x = theme.axis_ticks.color
            tick_color_y = theme.axis_ticks.color
        if theme.axis_ticks.size is not None:
            tick_width_x = theme.axis_ticks.size
            tick_width_y = theme.axis_ticks.size

    # Per-axis tick overrides
    if isinstance(theme.axis_ticks_x, ElementBlank):
        show_ticks_x = False
    elif isinstance(theme.axis_ticks_x, ElementLine):
        if theme.axis_ticks_x.color is not None:
            tick_color_x = theme.axis_ticks_x.color
        if theme.axis_ticks_x.size is not None:
            tick_width_x = theme.axis_ticks_x.size
    if isinstance(theme.axis_ticks_y, ElementBlank):
        show_ticks_y = False
    elif isinstance(theme.axis_ticks_y, ElementLine):
        if theme.axis_ticks_y.color is not None:
            tick_color_y = theme.axis_ticks_y.color
        if theme.axis_ticks_y.size is not None:
            tick_width_y = theme.axis_ticks_y.size

    ax.tick_params(
        axis="x",
        labelsize=axis_text_x_kw.get("fontsize", theme.tick_size),
        labelrotation=axis_text_x_kw.get("rotation", 0),
        labelcolor=axis_text_x_kw.get("color", "#000000"),
        length=tick_length_x if show_ticks_x else 0,
        width=tick_width_x,
        color=tick_color_x,
        bottom=show_ticks_x,
        top=show_ticks_x,
    )
    ax.tick_params(
        axis="y",
        labelsize=axis_text_y_kw.get("fontsize", theme.tick_size),
        labelrotation=axis_text_y_kw.get("rotation", 0),
        labelcolor=axis_text_y_kw.get("color", "#000000"),
        length=tick_length_y if show_ticks_y else 0,
        width=tick_width_y,
        color=tick_color_y,
        left=show_ticks_y,
        right=show_ticks_y,
    )

    # Apply font family/weight/style to tick labels
    tick_family_x = axis_text_x_kw.get("fontfamily", theme.font_family)
    tick_family_y = axis_text_y_kw.get("fontfamily", theme.font_family)
    for label in ax.get_xticklabels():
        label.set_fontfamily(tick_family_x)
        if "fontweight" in axis_text_x_kw:
            label.set_fontweight(axis_text_x_kw["fontweight"])
        if "fontstyle" in axis_text_x_kw:
            label.set_fontstyle(axis_text_x_kw["fontstyle"])
    for label in ax.get_yticklabels():
        label.set_fontfamily(tick_family_y)
        if "fontweight" in axis_text_y_kw:
            label.set_fontweight(axis_text_y_kw["fontweight"])
        if "fontstyle" in axis_text_y_kw:
            label.set_fontstyle(axis_text_y_kw["fontstyle"])

    # Draw layers
    coord = resolved.coord
    for layer in panel.layers:
        draw_data = cast("GeomDrawData", layer.data)
        if hasattr(coord, "transform_data"):
            draw_data = coord.transform_data(draw_data, resolved.scales)  # type: ignore[union-attr]
        draw_params = cast("GeomParams", layer.params)
        # Inject theme defaults for text geoms
        draw_params = _inject_theme_text_defaults(layer.geom, draw_params, theme)
        layer.geom.draw(draw_data, ax, draw_params)

    # Font — axis titles with per-axis element overrides
    axis_title_kw = text_props(
        theme.axis_title,
        theme,
        default_size=theme.label_size,
        default_color="#000000",
    )

    # Per-axis title element overrides
    axis_title_x_kw = _resolve_per_axis_text(
        theme.axis_title_x,
        axis_title_kw,
        theme,
        size_override=theme.axis_title_x_size,
    )
    axis_title_y_kw = _resolve_per_axis_text(
        theme.axis_title_y,
        axis_title_kw,
        theme,
        size_override=theme.axis_title_y_size,
    )

    # Check if per-axis title elements suppress the title
    if not isinstance(theme.axis_title_x, ElementBlank):
        ax.xaxis.label.set_fontfamily(axis_title_x_kw.get("fontfamily", theme.font_family))
        ax.xaxis.label.set_fontsize(axis_title_x_kw.get("fontsize", theme.label_size))
        if "fontweight" in axis_title_x_kw:
            ax.xaxis.label.set_fontweight(axis_title_x_kw["fontweight"])
        if "fontstyle" in axis_title_x_kw:
            ax.xaxis.label.set_fontstyle(axis_title_x_kw["fontstyle"])
        if "color" in axis_title_x_kw:
            ax.xaxis.label.set_color(axis_title_x_kw["color"])
    else:
        ax.xaxis.label.set_fontsize(0)

    if not isinstance(theme.axis_title_y, ElementBlank):
        ax.yaxis.label.set_fontfamily(axis_title_y_kw.get("fontfamily", theme.font_family))
        ax.yaxis.label.set_fontsize(axis_title_y_kw.get("fontsize", theme.label_size))
        if "fontweight" in axis_title_y_kw:
            ax.yaxis.label.set_fontweight(axis_title_y_kw["fontweight"])
        if "fontstyle" in axis_title_y_kw:
            ax.yaxis.label.set_fontstyle(axis_title_y_kw["fontstyle"])
        if "color" in axis_title_y_kw:
            ax.yaxis.label.set_color(axis_title_y_kw["color"])
    else:
        ax.yaxis.label.set_fontsize(0)


def _resolve_per_axis_text(
    per_axis_element: object,
    global_kw: dict,
    theme: object,
    *,
    size_override: float | None = None,
    rotation_override: float | None = None,
) -> dict:
    """Resolve per-axis element text props, falling back to global."""
    from plotten.themes._elements import ElementBlank, ElementText

    kw = dict(global_kw)

    # Apply scalar overrides first (backward compat)
    if size_override is not None:
        kw["fontsize"] = size_override
    if rotation_override is not None and rotation_override != 0:
        kw["rotation"] = rotation_override

    # Per-axis element override takes highest precedence
    if isinstance(per_axis_element, ElementBlank):
        kw["fontsize"] = 0
    elif isinstance(per_axis_element, ElementText):
        if per_axis_element.size is not None:
            kw["fontsize"] = per_axis_element.size
        if per_axis_element.color is not None:
            kw["color"] = per_axis_element.color
        if per_axis_element.family is not None:
            kw["fontfamily"] = per_axis_element.family
        if per_axis_element.weight is not None:
            kw["fontweight"] = per_axis_element.weight
        if per_axis_element.style is not None:
            kw["fontstyle"] = per_axis_element.style
        if per_axis_element.rotation is not None:
            kw["rotation"] = per_axis_element.rotation

    return kw


def _inject_theme_text_defaults(
    geom: object,
    params: GeomParams,
    theme: Theme,
) -> GeomParams:
    """Inject theme defaults (font_family, label colors) into text geom params."""
    from plotten.geoms._text import GeomLabel, GeomText

    if not isinstance(geom, (GeomText, GeomLabel)):
        return params

    updated = dict(params)
    # Font family fallback from theme
    if updated.get("family") is None:
        updated["family"] = theme.font_family
    # Label background/border defaults from theme for GeomLabel
    if isinstance(geom, GeomLabel):
        # Detect dark themes and adjust label fill/color defaults
        bg = theme.panel_background
        if updated.get("fill") is None and _is_dark_color(bg):
            updated["fill"] = bg  # label fill matches panel background
        if updated.get("color") is None and _is_dark_color(theme.background):
            updated["color"] = "#cccccc"  # light border on dark themes
    return updated  # type: ignore[return-value]


def _is_dark_color(color: str) -> bool:
    """Heuristic check if a color string is dark (luminance < 0.4)."""
    if color == "none" or not color.startswith("#") or len(color) < 7:
        return False
    try:
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.4
    except ValueError:
        return False
