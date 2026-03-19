from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt

from plotten._render._legend import draw_legend
from plotten._render._resolve import ResolvedLayer, ResolvedPanel, ResolvedPlot, resolve
from plotten.scales._position import ScaleDiscrete
from plotten.themes._theme import Theme

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def render_single(plot: Any, resolved: ResolvedPlot, fig: Any, ax: Any) -> None:
    """Render a single-panel resolved plot onto an existing fig/ax pair."""
    from plotten.coords._flip import CoordFlip

    theme: Theme = resolved.theme or Theme()
    is_flipped = isinstance(resolved.coord, CoordFlip)

    if is_flipped:
        resolved = _flip_resolved(resolved)

    panel = resolved.panels[0]
    _render_panel(panel, ax, resolved, theme)
    _apply_scales(ax, resolved.scales, polar=_is_polar(resolved.coord))
    _apply_coord_limits(ax, resolved.coord, is_flipped)

    # Apply labs directly to axes
    labs = resolved.labs
    if labs is not None:
        if not _is_polar(resolved.coord):
            axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
            axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size
            if labs.x is not None:
                ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
            if labs.y is not None:
                ax.set_ylabel(labs.y, fontsize=axis_title_y_size)
        if labs.title is not None:
            ax.set_title(labs.title, fontsize=theme.title_size)


def _is_polar(coord: Any) -> bool:
    from plotten.coords._polar import CoordPolar

    return isinstance(coord, CoordPolar)


def _create_axes(coord: Any, **kwargs: Any) -> tuple[Any, Any]:
    """Create fig/ax, using polar projection if needed."""
    if _is_polar(coord):
        return plt.subplots(subplot_kw={"projection": "polar"}, **kwargs)
    return plt.subplots(**kwargs)


def _transform_data_for_polar(data: dict[str, Any], coord: Any, scales: dict) -> dict[str, Any]:
    """Convert x/y data to theta/r for polar coordinates.

    For discrete theta scales, map category indices to evenly-spaced angles.
    For continuous theta data, pass values through as-is (matplotlib polar
    projection treats x as theta in radians natively).
    When theta="y", swap x and y so matplotlib gets theta in x and r in y.
    """
    import numpy as np

    data = dict(data)
    theta_aes = coord.theta  # "x" or "y"

    theta_vals = data.get(theta_aes)
    if theta_vals is None:
        return data

    theta_vals = np.asarray(theta_vals, dtype=float)

    # Discrete: map category indices to evenly-spaced angles around the circle
    from plotten.scales._position import ScaleDiscrete

    if theta_aes in scales and isinstance(scales[theta_aes], ScaleDiscrete):
        n = len(scales[theta_aes]._levels)
        if n > 0:
            theta_vals = theta_vals * 2 * np.pi / n
        data[theta_aes] = theta_vals.tolist()

    # When theta="y", polar projection expects theta=x, r=y — swap
    if theta_aes == "y" and "x" in data and "y" in data:
        data["x"], data["y"] = data["y"], data["x"]

    return data


def render(plot: Any) -> Figure:
    """Render a Plot spec to a matplotlib Figure."""
    from plotten.coords._flip import CoordFlip

    resolved = resolve(plot)
    theme: Theme = resolved.theme or Theme()
    is_flipped = isinstance(resolved.coord, CoordFlip)
    is_polar = _is_polar(resolved.coord)

    # If flipped, swap x/y in scales and layer data
    if is_flipped:
        resolved = _flip_resolved(resolved)

    if resolved.facet is None:
        # Single panel
        fig, ax = _create_axes(resolved.coord, figsize=(8, 6))
        fig.patch.set_facecolor(theme.background)
        panel = resolved.panels[0]
        _render_panel(panel, ax, resolved, theme)
        _apply_scales(ax, resolved.scales, polar=is_polar)
        _apply_coord_limits(ax, resolved.coord, is_flipped)
        _apply_axis_labs(ax, resolved, theme)
        fig.tight_layout(pad=theme.margin * 10)
        _apply_title(fig, resolved, theme)
        draw_legend(fig, [ax], resolved.scales, resolved.labs, theme, resolved.guides)
    else:
        # Faceted
        n_panels = len(resolved.panels)
        nrow, ncol = resolved.facet.layout(n_panels)
        subplot_kw = {"projection": "polar"} if is_polar else {}
        fig, axes = plt.subplots(
            nrow,
            ncol,
            figsize=(4 * ncol, 3.5 * nrow),
            squeeze=False,
            subplot_kw=subplot_kw,
        )
        fig.patch.set_facecolor(theme.background)

        free_scales = getattr(resolved.facet, "scales", "fixed")

        for idx, panel in enumerate(resolved.panels):
            r, c = divmod(idx, ncol)
            ax = axes[r][c]

            _render_panel(panel, ax, resolved, theme)

            # Scales: use panel-specific if free, else global
            if free_scales == "fixed":
                _apply_scales(ax, resolved.scales, polar=is_polar)
            else:
                panel_sc = dict(resolved.scales)
                panel_sc.update(panel.scales)
                _apply_scales(ax, panel_sc, polar=is_polar)

            _apply_coord_limits(ax, resolved.coord, is_flipped)

            # Panel strip title
            strip_bg = getattr(theme, "strip_background", "#d9d9d9")
            strip_text_size = getattr(theme, "strip_text_size", None) or theme.label_size
            strip_text_color = getattr(theme, "strip_text_color", "#000000")
            ax.set_title(
                panel.label,
                fontsize=strip_text_size,
                color=strip_text_color,
                pad=6,
                bbox={"facecolor": strip_bg, "edgecolor": "none", "pad": 3},
            )

        # Hide empty axes
        for idx in range(n_panels, nrow * ncol):
            r, c = divmod(idx, ncol)
            axes[r][c].set_visible(False)

        _apply_axis_labs(axes[0][0], resolved, theme)
        fig.tight_layout(pad=theme.margin * 10)
        _apply_title(fig, resolved, theme)

        visible_axes = [axes[r][c] for idx in range(n_panels) for r, c in [divmod(idx, ncol)]]
        draw_legend(fig, visible_axes, resolved.scales, resolved.labs, theme, resolved.guides)

    return fig


def _render_panel(
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

    grid_major_x = getattr(theme, "grid_major_x", True)
    grid_major_y = getattr(theme, "grid_major_y", True)
    grid_minor_x = getattr(theme, "grid_minor_x", False)
    grid_minor_y = getattr(theme, "grid_minor_y", False)

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
        axis_line_x = getattr(theme, "axis_line_x", True)
        axis_line_y = getattr(theme, "axis_line_y", True)
        ax.spines["bottom"].set_visible(axis_line_x)
        ax.spines["top"].set_visible(axis_line_x)
        ax.spines["left"].set_visible(axis_line_y)
        ax.spines["right"].set_visible(axis_line_y)

    # Panel border
    panel_border_color = getattr(theme, "panel_border_color", None)
    panel_border_width = getattr(theme, "panel_border_width", 1.0)
    if panel_border_color is not None:
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(panel_border_color)
            spine.set_linewidth(panel_border_width)

    # Tick styling — per-axis sizes and rotation
    axis_text_x_size = getattr(theme, "axis_text_x_size", None) or theme.tick_size
    axis_text_y_size = getattr(theme, "axis_text_y_size", None) or theme.tick_size
    axis_text_x_rotation = getattr(theme, "axis_text_x_rotation", 0)
    axis_text_y_rotation = getattr(theme, "axis_text_y_rotation", 0)

    ax.tick_params(
        axis="x",
        labelsize=axis_text_x_size,
        labelrotation=axis_text_x_rotation,
        length=theme.tick_length,
    )
    ax.tick_params(
        axis="y",
        labelsize=axis_text_y_size,
        labelrotation=axis_text_y_rotation,
        length=theme.tick_length,
    )

    # Draw layers
    for layer in panel.layers:
        draw_data = layer.data
        if _is_polar(resolved.coord):
            draw_data = _transform_data_for_polar(draw_data, resolved.coord, resolved.scales)
        layer.geom.draw(draw_data, ax, layer.params)

    # Font — per-axis title sizes
    axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
    axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size

    ax.xaxis.label.set_fontfamily(theme.font_family)
    ax.yaxis.label.set_fontfamily(theme.font_family)
    ax.xaxis.label.set_fontsize(axis_title_x_size)
    ax.yaxis.label.set_fontsize(axis_title_y_size)


def _apply_scales(ax: Axes, scales: dict, *, polar: bool = False) -> None:
    """Apply scale limits, breaks, and labels to axes."""
    from plotten.scales._log import ScaleLog
    from plotten.scales._position import ScaleContinuous
    from plotten.scales._reverse import ScaleReverse
    from plotten.scales._sqrt import ScaleSqrt

    if "x" in scales and not polar:
        x_scale = scales["x"]
        match x_scale:
            case ScaleLog():
                ax.set_xscale("log", base=x_scale._base)
            case ScaleSqrt():
                import numpy as _np

                ax.set_xscale("function", functions=(_np.sqrt, _np.square))
                _apply_continuous_scale(ax, x_scale, axis="x")
            case _ if _is_date_scale(x_scale):
                _apply_date_scale(ax, x_scale, axis="x")
            case ScaleReverse():
                _apply_continuous_scale(ax, x_scale, axis="x")
            case ScaleDiscrete():
                ax.set_xlim(x_scale.get_limits())
                ax.set_xticks(x_scale.get_breaks())
                ax.set_xticklabels(x_scale.get_labels())
            case ScaleContinuous() if x_scale._breaks is not None or callable(x_scale._labels):
                _apply_continuous_scale(ax, x_scale, axis="x")
            case _:
                ax.set_xlim(x_scale.get_limits())
        ax.set_xlabel("x")
        _apply_sec_axis(ax, x_scale, axis="x")

    if "y" in scales:
        y_scale = scales["y"]
        match y_scale:
            case ScaleLog():
                ax.set_yscale("log", base=y_scale._base)
            case ScaleSqrt():
                import numpy as _np

                ax.set_yscale("function", functions=(_np.sqrt, _np.square))
                _apply_continuous_scale(ax, y_scale, axis="y")
            case _ if _is_date_scale(y_scale):
                _apply_date_scale(ax, y_scale, axis="y")
            case ScaleReverse():
                _apply_continuous_scale(ax, y_scale, axis="y")
            case ScaleDiscrete():
                ax.set_ylim(y_scale.get_limits())
                ax.set_yticks(y_scale.get_breaks())
                ax.set_yticklabels(y_scale.get_labels())
            case ScaleContinuous() if y_scale._breaks is not None or callable(y_scale._labels):
                _apply_continuous_scale(ax, y_scale, axis="y")
            case _:
                ax.set_ylim(y_scale.get_limits())
        if not polar:
            ax.set_ylabel("y")
        _apply_sec_axis(ax, y_scale, axis="y")


def _apply_sec_axis(ax: Axes, scale: Any, axis: str) -> None:
    """Apply a secondary axis if the scale has one configured."""
    sec = getattr(scale, "_sec_axis", None)
    if sec is None:
        return
    if axis == "y":
        sec_ax = ax.secondary_yaxis("right", functions=(sec.trans, sec.inverse))
    else:
        sec_ax = ax.secondary_xaxis("top", functions=(sec.trans, sec.inverse))
    if sec.name is not None:
        sec_ax.set_label(sec.name) if axis == "x" else sec_ax.set_ylabel(sec.name)
    if sec.breaks is not None:
        if axis == "y":
            sec_ax.set_yticks(sec.breaks)
        else:
            sec_ax.set_xticks(sec.breaks)
    if sec.labels is not None:
        if axis == "y":
            sec_ax.set_yticklabels(sec.labels)
        else:
            sec_ax.set_xticklabels(sec.labels)


def _apply_continuous_scale(ax: Axes, scale: Any, axis: str) -> None:
    """Apply limits, breaks, and labels for a continuous scale."""
    limits = scale.get_limits()
    if axis == "x":
        ax.set_xlim(limits)
        ax.set_xticks(scale.get_breaks())
        ax.set_xticklabels(scale.get_labels())
    else:
        ax.set_ylim(limits)
        ax.set_yticks(scale.get_breaks())
        ax.set_yticklabels(scale.get_labels())


def _is_date_scale(scale: Any) -> bool:
    try:
        from plotten.scales._date import ScaleDateContinuous

        return isinstance(scale, ScaleDateContinuous)
    except ImportError:
        return False


def _apply_date_scale(ax: Axes, scale: Any, axis: str) -> None:
    import matplotlib.dates as mdates

    locator = mdates.AutoDateLocator()
    formatter = mdates.AutoDateFormatter(locator)

    match axis:
        case "x":
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            ax.set_xlim(scale.get_limits())
            ax.figure.autofmt_xdate()
        case "y":
            ax.yaxis.set_major_locator(locator)
            ax.yaxis.set_major_formatter(formatter)
            ax.set_ylim(scale.get_limits())


def _flip_resolved(resolved: ResolvedPlot) -> ResolvedPlot:
    """Swap x/y in all panel layer data and scales for CoordFlip."""
    new_scales = {}
    for k, v in resolved.scales.items():
        if k == "x":
            new_scales["y"] = v
        elif k == "y":
            new_scales["x"] = v
        else:
            new_scales[k] = v

    new_panels = []
    for panel in resolved.panels:
        new_layers = []
        for layer in panel.layers:
            new_data = dict(layer.data)
            # Swap x and y
            if "x" in new_data and "y" in new_data:
                new_data["x"], new_data["y"] = new_data["y"], new_data["x"]
            elif "x" in new_data:
                new_data["y"] = new_data.pop("x")
            elif "y" in new_data:
                new_data["x"] = new_data.pop("y")
            new_layers.append(ResolvedLayer(geom=layer.geom, data=new_data, params=layer.params))
        new_panels.append(ResolvedPanel(label=panel.label, layers=new_layers, scales=panel.scales))

    return ResolvedPlot(
        panels=new_panels,
        scales=new_scales,
        coord=resolved.coord,
        theme=resolved.theme,
        labs=resolved.labs,
        facet=resolved.facet,
        guides=resolved.guides,
    )


def _apply_coord_limits(ax: Axes, coord: Any, is_flipped: bool) -> None:
    """Apply coordinate limits."""
    from plotten.coords._flip import CoordFlip

    if isinstance(coord, CoordFlip):
        # Limits were specified as original x/y, but data is now swapped
        if coord.xlim is not None:
            ax.set_ylim(coord.xlim)
        if coord.ylim is not None:
            ax.set_xlim(coord.ylim)
    elif _is_polar(coord) or coord is not None:
        coord.transform(None, ax)


def _apply_axis_labs(ax: Axes, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply axis labels from labs. Call before tight_layout."""
    labs = resolved.labs
    if labs is None:
        return
    # Polar axes don't use x/y axis labels — they overlap with angle/radius ticks
    if _is_polar(resolved.coord):
        return

    axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
    axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size

    if labs.x is not None:
        ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
    if labs.y is not None:
        ax.set_ylabel(labs.y, fontsize=axis_title_y_size)


def _apply_title(fig: Figure, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply title, subtitle, and caption. Call after tight_layout."""
    from plotten.themes._elements import ElementBlank, ElementText

    labs = resolved.labs
    if labs is None:
        return

    polar = _is_polar(resolved.coord)
    title_color = getattr(theme, "title_color", "#000000")
    title_size = theme.title_size
    title_family = theme.font_family
    subtitle_size = getattr(theme, "subtitle_size", None) or theme.label_size
    subtitle_color = getattr(theme, "subtitle_color", "#555555")

    # Apply element overrides
    if isinstance(theme.plot_title, ElementText):
        if theme.plot_title.size is not None:
            title_size = theme.plot_title.size
        if theme.plot_title.color is not None:
            title_color = theme.plot_title.color
        if theme.plot_title.family is not None:
            title_family = theme.plot_title.family

    if isinstance(theme.plot_subtitle, ElementText):
        if theme.plot_subtitle.size is not None:
            subtitle_size = theme.plot_subtitle.size
        if theme.plot_subtitle.color is not None:
            subtitle_color = theme.plot_subtitle.color

    has_title = labs.title is not None and not isinstance(theme.plot_title, ElementBlank)
    has_subtitle = labs.subtitle is not None and not isinstance(theme.plot_subtitle, ElementBlank)

    # Polar axes need more top margin since tick labels extend above the circle
    top_both = 0.78 if polar else 0.88
    top_single = 0.84 if polar else 0.93

    if has_title and has_subtitle:
        sub_y = 0.915 if not polar else 0.88
        fig.suptitle(
            labs.title,
            fontsize=title_size,
            fontfamily=title_family,
            color=title_color,
            y=0.98,
        )
        fig.text(
            0.5,
            sub_y,
            labs.subtitle,
            ha="center",
            va="top",
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
            transform=fig.transFigure,
        )
        fig.subplots_adjust(top=top_both)
    elif has_title:
        fig.suptitle(
            labs.title,
            fontsize=title_size,
            fontfamily=title_family,
            color=title_color,
        )
        fig.subplots_adjust(top=top_single)
    elif has_subtitle:
        fig.suptitle(
            labs.subtitle,
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
        )
        fig.subplots_adjust(top=top_single)

    if labs.caption is not None and not isinstance(theme.plot_caption, ElementBlank):
        cur_bottom = fig.subplotpars.bottom
        fig.subplots_adjust(bottom=cur_bottom + 0.03)
        fig.text(
            0.99,
            0.005,
            labs.caption,
            ha="right",
            va="bottom",
            fontsize=theme.tick_size,
            fontfamily=theme.font_family,
        )
