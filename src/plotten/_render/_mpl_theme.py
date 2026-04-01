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
    *elements: ElementLine | ElementBlank | None,
) -> bool:
    """Resolve grid/tick visibility through the element cascade.

    Any :class:`ElementBlank` in the chain suppresses visibility.
    Elements are checked in order from broadest (e.g. ``panel_grid``)
    to most specific (e.g. ``panel_grid_major_x``).
    """
    from plotten.themes._elements import ElementBlank

    for el in elements:
        if isinstance(el, ElementBlank):
            default = False
    return default


def _resolve_line_prop[T](
    default: T,
    *elements: ElementLine | ElementBlank | None,
    attr: str,
    base_line: ElementLine | None = None,
) -> T:
    """Resolve a line property (color/size) through the element cascade.

    Elements are checked in order from broadest to most specific;
    the last non-None value wins.
    """
    from plotten.themes._elements import ElementLine

    if isinstance(base_line, ElementLine):
        val = getattr(base_line, attr, None)
        if val is not None:
            default = val
    for el in elements:
        if isinstance(el, ElementLine):
            val = getattr(el, attr, None)
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
    from plotten.themes._elements import ElementBlank, ElementLine, ElementRect, resolve_background

    panel_fill, panel_edge, panel_edge_w = resolve_background(theme.panel_background)
    if panel_fill and panel_fill != "none":
        ax.set_facecolor(panel_fill)
    else:
        ax.set_facecolor("none")
    if panel_edge is not None:
        ax.patch.set_edgecolor(panel_edge)
        ax.patch.set_linewidth(panel_edge_w or 1.0)

    # Grid — element overrides take precedence
    # Cascade: panel_grid → panel_grid_major/minor → panel_grid_major/minor_x/y
    pg = theme.panel_grid
    grid_major_x = _resolve_visibility(
        theme.grid_major_x, pg, theme.panel_grid_major, theme.panel_grid_major_x
    )
    grid_major_y = _resolve_visibility(
        theme.grid_major_y, pg, theme.panel_grid_major, theme.panel_grid_major_y
    )
    grid_minor_x = _resolve_visibility(
        theme.grid_minor_x, pg, theme.panel_grid_minor, theme.panel_grid_minor_x
    )
    grid_minor_y = _resolve_visibility(
        theme.grid_minor_y, pg, theme.panel_grid_minor, theme.panel_grid_minor_y
    )

    # Resolve grid colors and widths per axis
    base_line = theme.line
    major_grid_color_x = _resolve_line_prop(
        theme.grid_color,
        pg,
        theme.panel_grid_major,
        theme.panel_grid_major_x,
        attr="color",
        base_line=base_line,
    )
    major_grid_color_y = _resolve_line_prop(
        theme.grid_color,
        pg,
        theme.panel_grid_major,
        theme.panel_grid_major_y,
        attr="color",
        base_line=base_line,
    )
    major_grid_width_x = _resolve_line_prop(
        theme.grid_line_width,
        pg,
        theme.panel_grid_major,
        theme.panel_grid_major_x,
        attr="size",
        base_line=base_line,
    )
    major_grid_width_y = _resolve_line_prop(
        theme.grid_line_width,
        pg,
        theme.panel_grid_major,
        theme.panel_grid_major_y,
        attr="size",
        base_line=base_line,
    )

    minor_grid_color_x = _resolve_line_prop(
        theme.grid_color,
        pg,
        theme.panel_grid_minor,
        theme.panel_grid_minor_x,
        attr="color",
        base_line=base_line,
    )
    minor_grid_color_y = _resolve_line_prop(
        theme.grid_color,
        pg,
        theme.panel_grid_minor,
        theme.panel_grid_minor_y,
        attr="color",
        base_line=base_line,
    )
    minor_grid_width_x = _resolve_line_prop(
        theme.grid_line_width * 0.5,
        pg,
        theme.panel_grid_minor,
        theme.panel_grid_minor_x,
        attr="size",
        base_line=base_line,
    )
    minor_grid_width_y = _resolve_line_prop(
        theme.grid_line_width * 0.5,
        pg,
        theme.panel_grid_minor,
        theme.panel_grid_minor_y,
        attr="size",
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
    from plotten.themes._elements import merge_rect

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
        attr="color",
        base_line=base_line,
    )
    tick_color_y = _resolve_line_prop(
        axis_text_y_kw.get("color", "#000000"),
        theme.axis_ticks,
        theme.axis_ticks_y,
        attr="color",
        base_line=base_line,
    )
    tick_width_x = _resolve_line_prop(
        line_width,
        theme.axis_ticks,
        theme.axis_ticks_x,
        attr="size",
        base_line=base_line,
    )
    tick_width_y = _resolve_line_prop(
        line_width,
        theme.axis_ticks,
        theme.axis_ticks_y,
        attr="size",
        base_line=base_line,
    )

    ax.tick_params(
        axis="x",
        which="major",
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
        which="major",
        labelsize=axis_text_y_kw.get("fontsize", theme.tick_size),
        labelrotation=axis_text_y_kw.get("rotation", 0),
        labelcolor=axis_text_y_kw.get("color", "#000000"),
        length=tick_length_y if show_ticks_y else 0,
        width=tick_width_y,
        color=tick_color_y,
        left=show_ticks_y,
        right=show_ticks_y,
    )

    # Minor ticks — cascade: axis_minor_ticks → axis_minor_ticks_x/y
    show_minor_x = _resolve_visibility(
        grid_minor_x, theme.axis_minor_ticks, theme.axis_minor_ticks_x
    )
    show_minor_y = _resolve_visibility(
        grid_minor_y, theme.axis_minor_ticks, theme.axis_minor_ticks_y
    )
    if show_minor_x or show_minor_y:
        ax.minorticks_on()
        minor_length_x = (
            theme.axis_minor_ticks_length_x or theme.axis_minor_ticks_length or tick_length_x * 0.5
        )
        minor_length_y = (
            theme.axis_minor_ticks_length_y or theme.axis_minor_ticks_length or tick_length_y * 0.5
        )
        minor_color_x = _resolve_line_prop(
            tick_color_x,
            theme.axis_minor_ticks,
            theme.axis_minor_ticks_x,
            attr="color",
            base_line=base_line,
        )
        minor_color_y = _resolve_line_prop(
            tick_color_y,
            theme.axis_minor_ticks,
            theme.axis_minor_ticks_y,
            attr="color",
            base_line=base_line,
        )
        minor_width_x = _resolve_line_prop(
            tick_width_x * 0.5,
            theme.axis_minor_ticks,
            theme.axis_minor_ticks_x,
            attr="size",
            base_line=base_line,
        )
        minor_width_y = _resolve_line_prop(
            tick_width_y * 0.5,
            theme.axis_minor_ticks,
            theme.axis_minor_ticks_y,
            attr="size",
            base_line=base_line,
        )
        ax.tick_params(
            axis="x",
            which="minor",
            length=minor_length_x if show_minor_x else 0,
            width=minor_width_x,
            color=minor_color_x,
            bottom=show_minor_x,
            top=show_minor_x,
        )
        ax.tick_params(
            axis="y",
            which="minor",
            length=minor_length_y if show_minor_y else 0,
            width=minor_width_y,
            color=minor_color_y,
            left=show_minor_y,
            right=show_minor_y,
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

    # Polar axis theme overrides — theta maps to x, r maps to y in matplotlib
    if is_polar_ax:
        # axis_text_theta / axis_text_r — override tick label styling
        if isinstance(theme.axis_text_theta, ElementBlank):
            ax.tick_params(axis="x", labelbottom=False)
        elif theme.axis_text_theta is not None:
            theta_kw = text_props(theme.axis_text_theta, theme, default_size=theme.tick_size)
            ax.tick_params(
                axis="x",
                labelsize=theta_kw.get("fontsize", theme.tick_size),
                labelcolor=theta_kw.get("color", "#000000"),
            )
            if "rotation" in theta_kw:
                ax.tick_params(axis="x", labelrotation=theta_kw["rotation"])

        if isinstance(theme.axis_text_r, ElementBlank):
            ax.tick_params(axis="y", labelleft=False)
        elif theme.axis_text_r is not None:
            r_kw = text_props(theme.axis_text_r, theme, default_size=theme.tick_size)
            ax.tick_params(
                axis="y",
                labelsize=r_kw.get("fontsize", theme.tick_size),
                labelcolor=r_kw.get("color", "#000000"),
            )

        # axis_ticks_theta / axis_ticks_r — tick mark visibility and styling
        theta_tick_len = theme.axis_ticks_length_theta or theme.tick_length
        r_tick_len = theme.axis_ticks_length_r or theme.tick_length

        if isinstance(theme.axis_ticks_theta, ElementBlank):
            ax.tick_params(axis="x", length=0)
        elif isinstance(theme.axis_ticks_theta, ElementLine):
            tkw: dict[str, Any] = {"axis": "x", "length": theta_tick_len}
            if theme.axis_ticks_theta.color is not None:
                tkw["color"] = theme.axis_ticks_theta.color
            if theme.axis_ticks_theta.size is not None:
                tkw["width"] = theme.axis_ticks_theta.size
            ax.tick_params(**tkw)

        if isinstance(theme.axis_ticks_r, ElementBlank):
            ax.tick_params(axis="y", length=0)
        elif isinstance(theme.axis_ticks_r, ElementLine):
            rkw: dict[str, Any] = {"axis": "y", "length": r_tick_len}
            if theme.axis_ticks_r.color is not None:
                rkw["color"] = theme.axis_ticks_r.color
            if theme.axis_ticks_r.size is not None:
                rkw["width"] = theme.axis_ticks_r.size
            ax.tick_params(**rkw)

        # axis_line_theta / axis_line_r — polar spine styling
        # Polar axes have "polar" spine (outer circle) and "start"/"end" spines
        if isinstance(theme.axis_line_theta, ElementBlank) and "polar" in ax.spines:
            ax.spines["polar"].set_visible(False)
        elif isinstance(theme.axis_line_theta, ElementLine) and "polar" in ax.spines:
            ax.spines["polar"].set_visible(True)
            if theme.axis_line_theta.color is not None:
                ax.spines["polar"].set_edgecolor(theme.axis_line_theta.color)
            if theme.axis_line_theta.size is not None:
                ax.spines["polar"].set_linewidth(theme.axis_line_theta.size)

        if isinstance(theme.axis_line_r, ElementBlank):
            if "start" in ax.spines:
                ax.spines["start"].set_visible(False)
            if "end" in ax.spines:
                ax.spines["end"].set_visible(False)
        elif isinstance(theme.axis_line_r, ElementLine):
            for sp_name in ("start", "end"):
                if sp_name in ax.spines:
                    ax.spines[sp_name].set_visible(True)
                    if theme.axis_line_r.color is not None:
                        ax.spines[sp_name].set_edgecolor(theme.axis_line_r.color)
                    if theme.axis_line_r.size is not None:
                        ax.spines[sp_name].set_linewidth(theme.axis_line_r.size)

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
        from plotten.themes._elements import resolve_background

        bg_fill, _, _ = resolve_background(theme.panel_background)
        bg = bg_fill or "none"
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
