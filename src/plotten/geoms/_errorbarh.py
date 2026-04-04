from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomErrorbarH(GeomRepr):
    """Draw horizontal error bars (xmin to xmax whiskers)."""

    required_aes: frozenset[str] = frozenset({"y", "xmin", "xmax"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"color", "alpha", "height", "linewidth"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        linewidth = params.get("linewidth", 1)
        height = params.get("height", 0.2)
        hh = height / 2

        y_vals = data["y"]
        xmin_vals = data["xmin"]
        xmax_vals = data["xmax"]

        for i in range(len(y_vals)):
            y = y_vals[i]
            xmin = xmin_vals[i]
            xmax = xmax_vals[i]

            # Horizontal stem
            ax.hlines(y, xmin, xmax, colors=color, linewidth=linewidth)
            # Caps
            ax.vlines(xmin, y - hh, y + hh, colors=color, linewidth=linewidth)
            ax.vlines(xmax, y - hh, y + hh, colors=color, linewidth=linewidth)
