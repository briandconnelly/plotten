"""Panel rendering: background, grid, spines, ticks, and layer drawing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from plotten.themes._text_props import text_props

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._render._resolve import ResolvedPanel, ResolvedPlot
    from plotten._types import GeomDrawData, GeomParams
    from plotten.themes._elements import ElementBlank, ElementLine, ElementText
    from plotten.themes._theme import Theme


def _resolve_visibility(
    default: bool,
    global_el: ElementLine | ElementBlank | None,
    per_axis_el: ElementLine | ElementBlank | None,
) -> bool:
    """Resolve grid/tick visibility through the global → per-axis cascade."""
    from plotten.themes._elements import ElementBlank

    if isinstance(global_el, ElementBlank):
        default = False
    if isinstance(per_axis_el, ElementBlank):
        default = False
    return default


def _resolve_line_prop[T](
    default: T,
    global_el: ElementLine | ElementBlank | None,
    per_axis_el: ElementLine | ElementBlank | None,
    attr: str,
    *,
    base_line: ElementLine | None = None,
) -> T:
    """Resolve a line property (color/size) through base → global → per-axis cascade."""
    from plotten.themes._elements import ElementLine

    if isinstance(base_line, ElementLine):
        val = getattr(base_line, attr, None)
        if val is not None:
            default = val
    if isinstance(global_el, ElementLine):
        val = getattr(global_el, attr, None)
        if val is not None:
            default = val
    if isinstance(per_axis_el, ElementLine):
        val = getattr(per_axis_el, attr, None)
        if val is not None:
            default = val
    return default


def render_panel(
    panel: ResolvedPanel,
    ax: Axes,
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Draw layers and apply theme to a single axes."""
    from plotten.themes._elements import ElementBlank, ElementLine

    # Background
    if theme.panel_background != "none":
        ax.set_facecolor(theme.panel_background)
    else:
        ax.set_facecolor("none")

    # Grid — element overrides take precedence
    grid_major_x = _resolve_visibility(
        theme.grid_major_x, theme.panel_grid_major, theme.panel_grid_major_x
    )
    grid_major_y = _resolve_visibility(
        theme.grid_major_y, theme.panel_grid_major, theme.panel_grid_major_y
    )
    grid_minor_x = _resolve_visibility(
        theme.grid_minor_x, theme.panel_grid_minor, theme.panel_grid_minor_x
    )
    grid_minor_y = _resolve_visibility(
        theme.grid_minor_y, theme.panel_grid_minor, theme.panel_grid_minor_y
    )

    # Resolve grid colors and widths per axis
    base_line = theme.line
    major_grid_color_x = _resolve_line_prop(
        theme.grid_color,
        theme.panel_grid_major,
        theme.panel_grid_major_x,
        "color",
        base_line=base_line,
    )
    major_grid_color_y = _resolve_line_prop(
        theme.grid_color,
        theme.panel_grid_major,
        theme.panel_grid_major_y,
        "color",
        base_line=base_line,
    )
    major_grid_width_x = _resolve_line_prop(
        theme.grid_line_width,
        theme.panel_grid_major,
        theme.panel_grid_major_x,
        "size",
        base_line=base_line,
    )
    major_grid_width_y = _resolve_line_prop(
        theme.grid_line_width,
        theme.panel_grid_major,
        theme.panel_grid_major_y,
        "size",
        base_line=base_line,
    )

    minor_grid_color_x = _resolve_line_prop(
        theme.grid_color,
        theme.panel_grid_minor,
        theme.panel_grid_minor_x,
        "color",
        base_line=base_line,
    )
    minor_grid_color_y = _resolve_line_prop(
        theme.grid_color,
        theme.panel_grid_minor,
        theme.panel_grid_minor_y,
        "color",
        base_line=base_line,
    )
    minor_grid_width_x = _resolve_line_prop(
        theme.grid_line_width * 0.5,
        theme.panel_grid_minor,
        theme.panel_grid_minor_x,
        "size",
        base_line=base_line,
    )
    minor_grid_width_y = _resolve_line_prop(
        theme.grid_line_width * 0.5,
        theme.panel_grid_minor,
        theme.panel_grid_minor_y,
        "size",
        base_line=base_line,
    )

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
    ax.set_axisbelow(not theme.panel_ontop)

    # Spine styling (polar axes have different spine names)
    is_polar_ax = ax.name == "polar"

    # Resolve axis line element properties — inherit from theme.line
    from plotten.themes._elements import merge_line

    resolved_axis_line = merge_line(
        theme.axis_line_element if isinstance(theme.axis_line_element, ElementLine) else None,
        base_line,
    )
    line_width = theme.axis_line_width
    line_color = None
    if isinstance(resolved_axis_line, ElementLine):
        if resolved_axis_line.size is not None:
            line_width = resolved_axis_line.size
        line_color = resolved_axis_line.color

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

    # Panel border — inherit from theme.rect
    from plotten.themes._elements import ElementRect, merge_rect

    base_rect = theme.rect if isinstance(theme.rect, ElementRect) else None
    panel_border_color = theme.panel_border_color
    panel_border_width = theme.panel_border_width
    if base_rect is not None:
        if panel_border_color is None and base_rect.color is not None:
            panel_border_color = base_rect.color
        if panel_border_width == 1.0 and base_rect.size is not None:
            panel_border_width = base_rect.size
    if isinstance(theme.panel_border, ElementBlank):
        for spine in ax.spines.values():
            spine.set_visible(False)
        panel_border_color = None
    elif isinstance(theme.panel_border, ElementRect):
        resolved_border = merge_rect(theme.panel_border, base_rect)
        if isinstance(resolved_border, ElementRect):
            if resolved_border.color is not None:
                panel_border_color = resolved_border.color
            if resolved_border.size is not None:
                panel_border_width = resolved_border.size
    elif theme.panel_border is None:
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
    show_ticks_x = _resolve_visibility(True, theme.axis_ticks, theme.axis_ticks_x)
    show_ticks_y = _resolve_visibility(True, theme.axis_ticks, theme.axis_ticks_y)
    tick_color_x = _resolve_line_prop(
        axis_text_x_kw.get("color", "#000000"),
        theme.axis_ticks,
        theme.axis_ticks_x,
        "color",
        base_line=base_line,
    )
    tick_color_y = _resolve_line_prop(
        axis_text_y_kw.get("color", "#000000"),
        theme.axis_ticks,
        theme.axis_ticks_y,
        "color",
        base_line=base_line,
    )
    tick_width_x = _resolve_line_prop(
        line_width,
        theme.axis_ticks,
        theme.axis_ticks_x,
        "size",
        base_line=base_line,
    )
    tick_width_y = _resolve_line_prop(
        line_width,
        theme.axis_ticks,
        theme.axis_ticks_y,
        "size",
        base_line=base_line,
    )

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

    # Draw layers — assign incrementing zorder so layer order is respected
    coord = resolved.coord
    for layer_idx, layer in enumerate(panel.layers):
        draw_data = cast("GeomDrawData", layer.data)
        if hasattr(coord, "transform_data"):
            draw_data = coord.transform_data(draw_data, resolved.scales)  # type: ignore[union-attr]
        draw_params = cast("GeomParams", layer.params)
        # Inject theme defaults for text geoms
        draw_params = _inject_theme_text_defaults(layer.geom, draw_params, theme)
        artists_before = set(ax.get_children())
        try:
            layer.geom.draw(draw_data, ax, draw_params)
        except Exception as exc:
            from plotten._validation import RenderError

            geom_cls = type(layer.geom).__name__
            friendly = geom_cls.replace("Geom", "geom_").lower()
            data_keys = sorted(draw_data.keys())
            raise RenderError(
                f"Error rendering {friendly}: {exc}\n"
                f"  Data keys: {data_keys}\n"
                f"  Params: {dict(draw_params)}"
            ) from exc
        # Bump zorder of newly added artists so later layers draw on top
        base_zorder = 2 + layer_idx
        for artist in ax.get_children():
            if artist not in artists_before:
                artist.set_zorder(base_zorder)

    # Font — axis titles with per-axis element overrides
    axis_title_kw = text_props(
        theme.axis_title,
        theme,
        default_size=theme.label_size,
        default_color="#000000",
        is_title=True,
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
    per_axis_element: ElementText | ElementBlank | None,
    global_kw: dict[str, Any],
    theme: Theme,
    *,
    size_override: float | None = None,
    rotation_override: float | None = None,
) -> dict[str, Any]:
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
            from plotten.themes._elements import Rel

            if isinstance(per_axis_element.size, Rel):
                base = kw.get("fontsize")
                if base is not None:
                    kw["fontsize"] = per_axis_element.size.factor * base
            else:
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
    if color == "none":
        return False
    try:
        from matplotlib.colors import to_rgb

        r, g, b = to_rgb(color)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 0.4
    except ValueError:
        return False
