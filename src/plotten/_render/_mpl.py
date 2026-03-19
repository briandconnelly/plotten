from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._render._layout import (
    apply_facet_decorations,
    create_axes,
    create_figure,
    render_caption,
)
from plotten._render._legend import draw_legend
from plotten._render._mpl_labels import apply_axis_labs
from plotten._render._mpl_scales import apply_scales
from plotten._render._mpl_theme import render_panel
from plotten._render._resolve import ResolvedPlot, resolve
from plotten.themes._theme import Theme, theme_get

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def render_single(
    plot: Any,
    resolved: ResolvedPlot,
    fig: Any,
    ax: Any,
    *,
    draw_legend: bool = True,
) -> None:
    """Render a single-panel resolved plot onto an existing fig/ax pair."""
    from plotten.coords._flip import CoordFlip
    from plotten.coords._polar import CoordPolar

    theme: Theme = theme_get() + (resolved.theme or Theme())
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
            axis_title_x_size = theme.axis_title_x_size or theme.label_size
            axis_title_y_size = theme.axis_title_y_size or theme.label_size
            if labs.x is not None:
                ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
            if labs.y is not None:
                ax.set_ylabel(labs.y, fontsize=axis_title_y_size)
        if labs.title is not None:
            ax.set_title(labs.title, fontsize=theme.title_size)


def render(plot: Any) -> Figure:
    """Render a Plot spec to a matplotlib Figure."""
    from plotten.coords._flip import CoordFlip
    from plotten.coords._polar import CoordPolar

    resolved = resolve(plot)
    theme: Theme = theme_get() + (resolved.theme or Theme())
    is_flipped = isinstance(resolved.coord, CoordFlip)
    is_polar = isinstance(resolved.coord, CoordPolar)

    # If flipped, swap x/y in scales and layer data
    if is_flipped:
        resolved = CoordFlip.flip_resolved(resolved)

    # Create figure with constrained_layout and optional header/caption regions
    fig, main_subfig, caption_subfig = create_figure(resolved, theme)

    if resolved.facet is None:
        # Single panel
        ax = create_axes(main_subfig, resolved, theme)
        panel = resolved.panels[0]
        render_panel(panel, ax, resolved, theme)
        apply_scales(ax, resolved.scales, polar=is_polar)
        _apply_coord_limits(ax, resolved.coord, is_flipped)
        apply_axis_labs(ax, resolved, theme)

        # Render insets
        for inset in plot._insets:
            inset_ax = fig.add_axes((inset.left, inset.bottom, inset.width, inset.height))
            inset_resolved = resolve(inset.plot)
            render_single(inset.plot, inset_resolved, fig, inset_ax)

        # Caption
        render_caption(caption_subfig, resolved, theme)

        # Legend — make room by adjusting constrained rect, then draw on top-level fig
        _apply_legend(fig, [ax], resolved, theme)
    else:
        # Faceted
        n_panels = len(resolved.panels)
        nrow, ncol = resolved.facet.layout(n_panels)
        axes = create_axes(main_subfig, resolved, theme)

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

        # Apply strip labels, shared axis labels, hide empty axes
        apply_facet_decorations(main_subfig, axes, resolved, theme, n_panels, nrow, ncol)

        # Caption
        render_caption(caption_subfig, resolved, theme)

        # Legend
        visible_axes = [axes[idx // ncol][idx % ncol] for idx in range(n_panels)]
        _apply_legend(fig, visible_axes, resolved, theme)

    return fig


def _apply_legend(
    fig: Figure,
    axes: list[Any],
    resolved: ResolvedPlot,
    theme: Theme,
) -> None:
    """Adjust layout rect and draw legend."""
    from plotten._enums import LegendPosition

    position = theme.legend_position
    if isinstance(position, str) and position == LegendPosition.NONE:
        return

    # Check if there are any legend entries before adjusting layout
    has_legend = False
    for aes_name in ("color", "fill", "size", "alpha", "shape", "linetype"):
        if aes_name in resolved.scales and resolved.scales[aes_name].legend_entries():
            has_legend = True
            break

    if not has_legend:
        return

    # Adjust constrained layout rect to make room for legend
    engine = fig.get_layout_engine()
    if engine is not None:
        pos = position
        if isinstance(pos, tuple):
            pass  # Inside legend, no rect adjustment needed
        elif pos == LegendPosition.RIGHT:
            engine.set(rect=[0, 0, 0.85, 1])  # type: ignore[union-attr]
        elif pos == LegendPosition.LEFT:
            engine.set(rect=[0.15, 0, 1, 1])  # type: ignore[union-attr]
        elif pos == LegendPosition.TOP:
            engine.set(rect=[0, 0, 1, 0.85])  # type: ignore[union-attr]
        elif pos == LegendPosition.BOTTOM:
            engine.set(rect=[0, 0.15, 1, 1])  # type: ignore[union-attr]

    # Draw legend on the top-level figure (not subfigure)
    draw_legend(fig, axes, resolved.scales, resolved.labs, theme, resolved.guides)


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
