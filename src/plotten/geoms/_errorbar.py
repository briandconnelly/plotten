from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomErrorbar:
    """Draw error bars (ymin to ymax whiskers)."""

    required_aes: frozenset[str] = frozenset({"x", "ymin", "ymax"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"color", "alpha", "width", "linewidth"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        linewidth = params.get("linewidth", 1)
        width = params.get("width", 0.2)
        hw = width / 2

        x_vals = data["x"]
        ymin_vals = data["ymin"]
        ymax_vals = data["ymax"]

        for i in range(len(x_vals)):
            x = x_vals[i]
            ymin = ymin_vals[i]
            ymax = ymax_vals[i]

            # Vertical stem
            ax.vlines(x, ymin, ymax, colors=color, linewidth=linewidth)
            # Caps
            ax.hlines(ymin, x - hw, x + hw, colors=color, linewidth=linewidth)
            ax.hlines(ymax, x - hw, x + hw, colors=color, linewidth=linewidth)
