from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from plotten._render._legend import draw_legend
from plotten._render._resolve import ResolvedLayer, ResolvedPanel, ResolvedPlot, resolve
from plotten.scales._position import ScaleDiscrete
from plotten.themes._theme import Theme


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
        _apply_labs(fig, ax, resolved, theme)
        fig.tight_layout(pad=theme.margin * 10)
        draw_legend(fig, [ax], resolved.scales, resolved.labs, theme)
    else:
        # Faceted
        n_panels = len(resolved.panels)
        nrow, ncol = resolved.facet.layout(n_panels)
        fig, axes = plt.subplots(
            nrow, ncol, figsize=(4 * ncol, 3.5 * nrow), squeeze=False
        )
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
            ax.set_title(panel.label, fontsize=theme.label_size, pad=6)

        # Hide empty axes
        for idx in range(n_panels, nrow * ncol):
            r, c = divmod(idx, ncol)
            axes[r][c].set_visible(False)

        _apply_labs(fig, axes[0][0], resolved, theme)
        fig.tight_layout(pad=theme.margin * 10)

        visible_axes = [
            axes[r][c] for idx in range(n_panels) for r, c in [divmod(idx, ncol)]
        ]
        draw_legend(fig, visible_axes, resolved.scales, resolved.labs, theme)

    return fig


def _render_panel(
    panel: ResolvedPanel,
    ax: Any,
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Draw layers and apply theme to a single axes."""
    # Background
    if theme.panel_background != "none":
        ax.set_facecolor(theme.panel_background)
    else:
        ax.set_facecolor("none")

    # Grid
    ax.grid(True, color=theme.grid_color, linewidth=theme.grid_line_width)
    ax.set_axisbelow(True)

    # Spine styling
    for spine in ax.spines.values():
        spine.set_linewidth(theme.axis_line_width)

    # Tick styling
    ax.tick_params(labelsize=theme.tick_size, length=theme.tick_length)

    # Draw layers
    for layer in panel.layers:
        layer.geom.draw(layer.data, ax, layer.params)

    # Font
    ax.xaxis.label.set_fontfamily(theme.font_family)
    ax.yaxis.label.set_fontfamily(theme.font_family)
    ax.xaxis.label.set_fontsize(theme.label_size)
    ax.yaxis.label.set_fontsize(theme.label_size)


def _apply_scales(ax: Any, scales: dict) -> None:
    """Apply scale limits, breaks, and labels to axes."""
    from plotten.scales._log import ScaleLog
    from plotten.scales._position import ScaleContinuous

    if "x" in scales:
        x_scale = scales["x"]
        if isinstance(x_scale, ScaleLog):
            ax.set_xscale("log", base=x_scale._base)
        else:
            ax.set_xlim(x_scale.get_limits())
            if isinstance(x_scale, ScaleDiscrete):
                ax.set_xticks(x_scale.get_breaks())
                ax.set_xticklabels(x_scale.get_labels())
            elif isinstance(x_scale, ScaleContinuous) and x_scale._breaks is not None:
                ax.set_xticks(x_scale.get_breaks())
                ax.set_xticklabels(x_scale.get_labels())
        ax.set_xlabel("x")

    if "y" in scales:
        y_scale = scales["y"]
        if isinstance(y_scale, ScaleLog):
            ax.set_yscale("log", base=y_scale._base)
        else:
            ax.set_ylim(y_scale.get_limits())
            if isinstance(y_scale, ScaleDiscrete):
                ax.set_yticks(y_scale.get_breaks())
                ax.set_yticklabels(y_scale.get_labels())
            elif isinstance(y_scale, ScaleContinuous) and y_scale._breaks is not None:
                ax.set_yticks(y_scale.get_breaks())
                ax.set_yticklabels(y_scale.get_labels())
        ax.set_ylabel("y")


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
            new_layers.append(
                ResolvedLayer(geom=layer.geom, data=new_data, params=layer.params)
            )
        new_panels.append(
            ResolvedPanel(label=panel.label, layers=new_layers, scales=panel.scales)
        )

    return ResolvedPlot(
        panels=new_panels,
        scales=new_scales,
        coord=resolved.coord,
        theme=resolved.theme,
        labs=resolved.labs,
        facet=resolved.facet,
    )


def _apply_coord_limits(ax: Any, coord: Any, is_flipped: bool) -> None:
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


def _apply_labs(fig: Figure, ax: Any, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply title, subtitle, and axis labels from labs."""
    labs = resolved.labs
    if labs is None:
        return

    # Axis labels (fallback to column name "x"/"y" already set by _apply_scales)
    if labs.x is not None:
        ax.set_xlabel(labs.x, fontsize=theme.label_size)
    if labs.y is not None:
        ax.set_ylabel(labs.y, fontsize=theme.label_size)

    if labs.title is not None and labs.subtitle is not None:
        fig.suptitle(
            labs.title,
            fontsize=theme.title_size,
            fontfamily=theme.font_family,
            y=0.98,
        )
        fig.text(
            0.5,
            0.91,
            labs.subtitle,
            ha="center",
            fontsize=theme.label_size,
            fontfamily=theme.font_family,
        )
    elif labs.title is not None:
        fig.suptitle(
            labs.title, fontsize=theme.title_size, fontfamily=theme.font_family
        )
    elif labs.subtitle is not None:
        fig.suptitle(
            labs.subtitle, fontsize=theme.label_size, fontfamily=theme.font_family
        )

    if labs.caption is not None:
        fig.text(
            0.99,
            0.01,
            labs.caption,
            ha="right",
            va="bottom",
            fontsize=theme.tick_size,
            fontfamily=theme.font_family,
        )
