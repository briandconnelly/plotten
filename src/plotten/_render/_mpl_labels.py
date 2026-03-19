"""Axis labels application."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._render._resolve import ResolvedPlot
    from plotten.themes._theme import Theme


def apply_axis_labs(ax: Axes, resolved: ResolvedPlot, theme: Theme) -> None:
    """Apply axis labels from labs. Call before tight_layout."""
    from plotten.coords._polar import CoordPolar

    labs = resolved.labs
    if labs is None:
        return
    # Polar axes don't use x/y axis labels — they overlap with angle/radius ticks
    if isinstance(resolved.coord, CoordPolar):
        return

    axis_title_x_size = theme.axis_title_x_size or theme.label_size
    axis_title_y_size = theme.axis_title_y_size or theme.label_size

    if labs.x is not None:
        ax.set_xlabel(labs.x, fontsize=axis_title_x_size)
    if labs.y is not None:
        ax.set_ylabel(labs.y, fontsize=axis_title_y_size)
