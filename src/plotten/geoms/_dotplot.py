"""Dotplot geom — stacked dots replacing histograms."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_GEOM_COLOR

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomDotplot:
    """Draw circles at each (x, y) position for dot plots."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha"})

    def default_stat(self) -> Any:
        from plotten.stats._dotplot import StatDotplot

        return StatDotplot()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        xs = data["x"]
        ys = data["y"]

        color = params.get("color", "black")
        fill = params.get("fill", DEFAULT_GEOM_COLOR)
        alpha = params.get("alpha", 0.7)
        size = params.get("size", 30)

        colors = data.get("color")

        c = colors if isinstance(colors, list) else (fill or color)
        ax.scatter(xs, ys, s=size, c=c, alpha=alpha, edgecolors=color, linewidths=0.5)
