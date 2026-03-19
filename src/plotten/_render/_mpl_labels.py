"""Axis labels application."""

from __future__ import annotations

from typing import TYPE_CHECKING

from plotten.themes._text_props import text_props

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

    axis_title_kw = text_props(
        theme.axis_title,
        theme,
        default_size=theme.label_size,
        default_color="#000000",
    )
    # Remove ha/va/rotation — set_xlabel/set_ylabel don't use them directly
    for k in ("ha", "va", "rotation"):
        axis_title_kw.pop(k, None)

    ax_x_kw = dict(axis_title_kw)
    ax_y_kw = dict(axis_title_kw)
    if theme.axis_title_x_size is not None:
        ax_x_kw["fontsize"] = theme.axis_title_x_size
    if theme.axis_title_y_size is not None:
        ax_y_kw["fontsize"] = theme.axis_title_y_size

    if labs.x is not None:
        ax.set_xlabel(labs.x, **ax_x_kw)
    if labs.y is not None:
        ax.set_ylabel(labs.y, **ax_y_kw)
