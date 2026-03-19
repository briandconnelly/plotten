from __future__ import annotations

from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt

from plotten._defaults import (
    DEFAULT_FACET_CELL_HEIGHT,
    DEFAULT_FACET_CELL_WIDTH,
    DEFAULT_FIGSIZE,
    DEFAULT_STRIP_BOX_PAD,
    DEFAULT_STRIP_PAD,
)
from plotten._render._legend import draw_legend
from plotten._render._mpl_labels import apply_axis_labs, apply_title
from plotten._render._mpl_scales import apply_scales
from plotten._render._mpl_theme import render_panel
from plotten._render._resolve import ResolvedPlot, resolve
from plotten.themes._theme import Theme

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def render_single(plot: Any, resolved: ResolvedPlot, fig: Any, ax: Any) -> None:
    """Render a single-panel resolved plot onto an existing fig/ax pair."""
    from plotten.coords._flip import CoordFlip
    from plotten.coords._polar import CoordPolar

    theme: Theme = resolved.theme or Theme()
    is_flipped = isinstance(resolved.coord, CoordFlip)

    if is_flipped:
        resolved = CoordFlip.flip_resolved(resolved)

    panel = resolved.panels[0]
    render_panel(panel, ax, resolved, theme)
    apply_scales(ax, resolved.scales, polar=isinstance(resolved.coord, CoordPolar))
    _apply_coord_limits(ax, resolved.coord, is_flipped)

    # Apply labs directly to axes
    labs = resolved.labs
    if labs is not None:
        if not isinstance(resolved.coord, CoordPolar):
            axis_title_x_size = getattr(theme, "axis_title_x_size", None) or theme.label_size
            axis_title_y_size = getattr(theme, "axis_title_y_size", None) or theme.label_size
            if labs.x is not None:
                ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
            if labs.y is not None:
                ax.set_ylabel(labs.y, fontsize=axis_title_y_size)
        if labs.title is not None:
            ax.set_title(labs.title, fontsize=theme.title_size)


def _create_axes(coord: Any, **kwargs: Any) -> tuple[Any, Any]:
    """Create fig/ax, using polar projection if needed."""
    from plotten.coords._polar import CoordPolar

    if isinstance(coord, CoordPolar):
        return plt.subplots(subplot_kw={"projection": "polar"}, **kwargs)
    return plt.subplots(**kwargs)


def render(plot: Any) -> Figure:
    """Render a Plot spec to a matplotlib Figure."""
    from plotten.coords._flip import CoordFlip
    from plotten.coords._polar import CoordPolar

    resolved = resolve(plot)
    theme: Theme = resolved.theme or Theme()
    is_flipped = isinstance(resolved.coord, CoordFlip)
    is_polar = isinstance(resolved.coord, CoordPolar)

    # If flipped, swap x/y in scales and layer data
    if is_flipped:
        resolved = CoordFlip.flip_resolved(resolved)

    if resolved.facet is None:
        # Single panel
        fig, ax = _create_axes(resolved.coord, figsize=DEFAULT_FIGSIZE)
        fig.patch.set_facecolor(theme.background)
        panel = resolved.panels[0]
        render_panel(panel, ax, resolved, theme)
        apply_scales(ax, resolved.scales, polar=is_polar)
        _apply_coord_limits(ax, resolved.coord, is_flipped)
        apply_axis_labs(ax, resolved, theme)
        fig.tight_layout(pad=theme.margin * 10)
        apply_title(fig, resolved, theme)
        draw_legend(fig, [ax], resolved.scales, resolved.labs, theme, resolved.guides)
    else:
        # Faceted
        n_panels = len(resolved.panels)
        nrow, ncol = resolved.facet.layout(n_panels)
        subplot_kw = {"projection": "polar"} if is_polar else {}
        fig, axes = plt.subplots(
            nrow,
            ncol,
            figsize=(DEFAULT_FACET_CELL_WIDTH * ncol, DEFAULT_FACET_CELL_HEIGHT * nrow),
            squeeze=False,
            subplot_kw=subplot_kw,
        )
        fig.patch.set_facecolor(theme.background)

        free_scales = getattr(resolved.facet, "scales", "fixed")

        for idx, panel in enumerate(resolved.panels):
            r, c = divmod(idx, ncol)
            ax = axes[r][c]

            render_panel(panel, ax, resolved, theme)

            # Scales: use panel-specific if free, else global
            if free_scales == "fixed":
                apply_scales(ax, resolved.scales, polar=is_polar)
            else:
                panel_sc = dict(resolved.scales)
                panel_sc.update(panel.scales)
                apply_scales(ax, panel_sc, polar=is_polar)

            _apply_coord_limits(ax, resolved.coord, is_flipped)

            # Panel strip title
            strip_bg = getattr(theme, "strip_background", "#d9d9d9")
            strip_text_size = getattr(theme, "strip_text_size", None) or theme.label_size
            strip_text_color = getattr(theme, "strip_text_color", "#000000")
            ax.set_title(
                panel.label,
                fontsize=strip_text_size,
                color=strip_text_color,
                pad=DEFAULT_STRIP_PAD,
                bbox={"facecolor": strip_bg, "edgecolor": "none", "pad": DEFAULT_STRIP_BOX_PAD},
            )

        # Hide empty axes
        for idx in range(n_panels, nrow * ncol):
            r, c = divmod(idx, ncol)
            axes[r][c].set_visible(False)

        apply_axis_labs(axes[0][0], resolved, theme)
        fig.tight_layout(pad=theme.margin * 10)
        apply_title(fig, resolved, theme)

        visible_axes = [axes[r][c] for idx in range(n_panels) for r, c in [divmod(idx, ncol)]]
        draw_legend(fig, visible_axes, resolved.scales, resolved.labs, theme, resolved.guides)

    return fig


def _apply_coord_limits(ax: Any, coord: Any, is_flipped: bool) -> None:
    """Apply coordinate limits."""
    from plotten.coords._flip import CoordFlip
    from plotten.coords._polar import CoordPolar

    if isinstance(coord, CoordFlip):
        # Limits were specified as original x/y, but data is now swapped
        if coord.xlim is not None:
            ax.set_ylim(coord.xlim)
        if coord.ylim is not None:
            ax.set_xlim(coord.ylim)
    elif isinstance(coord, CoordPolar) or coord is not None:
        coord.transform(None, ax)
