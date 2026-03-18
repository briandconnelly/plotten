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
    _apply_scales(ax, resolved.scales)
    _apply_coord_limits(ax, resolved.coord, is_flipped)

    # Apply labs directly to axes
    labs = resolved.labs
    if labs is not None:
        axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
        axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size
        if labs.x is not None:
            ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
        if labs.y is not None:
            ax.set_ylabel(labs.y, fontsize=axis_title_y_size)
        if labs.title is not None:
            ax.set_title(labs.title, fontsize=theme.title_size)


def render(plot: Any) -> Figure:
    """Render a Plot spec to a matplotlib Figure."""
    from plotten.coords._flip import CoordFlip

    resolved = resolve(plot)
    theme: Theme = resolved.theme or Theme()
    is_flipped = isinstance(resolved.coord, CoordFlip)

    # If flipped, swap x/y in scales and layer data
    if is_flipped:
        resolved = _flip_resolved(resolved)

    if resolved.facet is None:
        # Single panel
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor(theme.background)
        panel = resolved.panels[0]
        _render_panel(panel, ax, resolved, theme)
        _apply_scales(ax, resolved.scales)
        _apply_coord_limits(ax, resolved.coord, is_flipped)
        _apply_axis_labs(ax, resolved, theme)
        fig.tight_layout(pad=theme.margin * 10)
        _apply_title(fig, resolved, theme)
        draw_legend(fig, [ax], resolved.scales, resolved.labs, theme, resolved.guides)
    else:
        # Faceted
        n_panels = len(resolved.panels)
        nrow, ncol = resolved.facet.layout(n_panels)
        fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3.5 * nrow), squeeze=False)
        fig.patch.set_facecolor(theme.background)

        free_scales = getattr(resolved.facet, "scales", "fixed")

        for idx, panel in enumerate(resolved.panels):
            r, c = divmod(idx, ncol)
            ax = axes[r][c]

            _render_panel(panel, ax, resolved, theme)

            # Scales: use panel-specific if free, else global
            if free_scales == "fixed":
                _apply_scales(ax, resolved.scales)
            else:
                panel_sc = dict(resolved.scales)
                panel_sc.update(panel.scales)
                _apply_scales(ax, panel_sc)

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

    # Grid — per-axis control
    grid_major_x = getattr(theme, "grid_major_x", True)
    grid_major_y = getattr(theme, "grid_major_y", True)
    grid_minor_x = getattr(theme, "grid_minor_x", False)
    grid_minor_y = getattr(theme, "grid_minor_y", False)

    # Clear any default grid, then apply per-axis
    ax.grid(False)
    if grid_major_x:
        ax.xaxis.grid(True, which="major", color=theme.grid_color, linewidth=theme.grid_line_width)
    if grid_major_y:
        ax.yaxis.grid(True, which="major", color=theme.grid_color, linewidth=theme.grid_line_width)
    if grid_minor_x or grid_minor_y:
        ax.minorticks_on()
        if grid_minor_x:
            ax.xaxis.grid(
                True, which="minor", color=theme.grid_color, linewidth=theme.grid_line_width * 0.5
            )
        if grid_minor_y:
            ax.yaxis.grid(
                True, which="minor", color=theme.grid_color, linewidth=theme.grid_line_width * 0.5
            )
    ax.set_axisbelow(True)

    # Spine styling
    for spine in ax.spines.values():
        spine.set_linewidth(theme.axis_line_width)

    # Axis line visibility
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
        layer.geom.draw(layer.data, ax, layer.params)

    # Font — per-axis title sizes
    axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
    axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size

    ax.xaxis.label.set_fontfamily(theme.font_family)
    ax.yaxis.label.set_fontfamily(theme.font_family)
    ax.xaxis.label.set_fontsize(axis_title_x_size)
    ax.yaxis.label.set_fontsize(axis_title_y_size)


def _apply_scales(ax: Axes, scales: dict) -> None:
    """Apply scale limits, breaks, and labels to axes."""
    from plotten.scales._log import ScaleLog
    from plotten.scales._position import ScaleContinuous

    if "x" in scales:
        x_scale = scales["x"]
        match x_scale:
            case ScaleLog():
                ax.set_xscale("log", base=x_scale._base)
            case _ if _is_date_scale(x_scale):
                _apply_date_scale(ax, x_scale, axis="x")
            case ScaleDiscrete():
                ax.set_xlim(x_scale.get_limits())
                ax.set_xticks(x_scale.get_breaks())
                ax.set_xticklabels(x_scale.get_labels())
            case ScaleContinuous() if x_scale._breaks is not None:
                ax.set_xlim(x_scale.get_limits())
                ax.set_xticks(x_scale.get_breaks())
                ax.set_xticklabels(x_scale.get_labels())
            case _:
                ax.set_xlim(x_scale.get_limits())
        ax.set_xlabel("x")

    if "y" in scales:
        y_scale = scales["y"]
        match y_scale:
            case ScaleLog():
                ax.set_yscale("log", base=y_scale._base)
            case _ if _is_date_scale(y_scale):
                _apply_date_scale(ax, y_scale, axis="y")
            case ScaleDiscrete():
                ax.set_ylim(y_scale.get_limits())
                ax.set_yticks(y_scale.get_breaks())
                ax.set_yticklabels(y_scale.get_labels())
            case ScaleContinuous() if y_scale._breaks is not None:
                ax.set_ylim(y_scale.get_limits())
                ax.set_yticks(y_scale.get_breaks())
                ax.set_yticklabels(y_scale.get_labels())
            case _:
                ax.set_ylim(y_scale.get_limits())
        ax.set_ylabel("y")


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
    elif coord is not None:
        coord.transform(None, ax)


def _apply_axis_labs(ax: Axes, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply axis labels from labs. Call before tight_layout."""
    labs = resolved.labs
    if labs is None:
        return

    axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
    axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size

    if labs.x is not None:
        ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
    if labs.y is not None:
        ax.set_ylabel(labs.y, fontsize=axis_title_y_size)


def _apply_title(fig: Figure, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply title, subtitle, and caption. Call after tight_layout."""
    labs = resolved.labs
    if labs is None:
        return

    title_color = getattr(theme, "title_color", "#000000")
    subtitle_size = getattr(theme, "subtitle_size", None) or theme.label_size
    subtitle_color = getattr(theme, "subtitle_color", "#555555")

    has_title = labs.title is not None
    has_subtitle = labs.subtitle is not None

    if has_title and has_subtitle:
        fig.suptitle(
            labs.title,
            fontsize=theme.title_size,
            fontfamily=theme.font_family,
            color=title_color,
            y=0.98,
        )
        fig.text(
            0.5,
            0.915,
            labs.subtitle,
            ha="center",
            va="top",
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
            transform=fig.transFigure,
        )
        fig.subplots_adjust(top=0.88)
    elif has_title:
        fig.suptitle(
            labs.title,
            fontsize=theme.title_size,
            fontfamily=theme.font_family,
            color=title_color,
        )
        fig.subplots_adjust(top=0.93)
    elif has_subtitle:
        fig.suptitle(
            labs.subtitle,
            fontsize=subtitle_size,
            fontfamily=theme.font_family,
            color=subtitle_color,
        )
        fig.subplots_adjust(top=0.93)

    if labs.caption is not None:
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
