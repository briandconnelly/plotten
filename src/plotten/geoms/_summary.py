from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomSummary(GeomRepr):
    """Draw summary points with error bars (y with ymin/ymax whiskers)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset(
        {"color", "fill", "alpha", "size", "linewidth", "width"}
    )
    warn_row_threshold: int | None = None

    def default_stat(self) -> Any:
        from plotten.stats._summary import StatSummary

        return StatSummary()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        size = params.get("size", 30)
        linewidth = params.get("linewidth", 1)
        width = params.get("width", 0.2)
        hw = width / 2

        x_vals = data["x"]
        y_vals = data["y"]
        ymin_vals = data["ymin"]
        ymax_vals = data["ymax"]

        # Error bars
        for i in range(len(x_vals)):
            x = x_vals[i]
            ymin = ymin_vals[i]
            ymax = ymax_vals[i]
            ax.vlines(x, ymin, ymax, colors=color, linewidth=linewidth)
            ax.hlines(ymin, x - hw, x + hw, colors=color, linewidth=linewidth)
            ax.hlines(ymax, x - hw, x + hw, colors=color, linewidth=linewidth)

        # Points at y
        ax.scatter(x_vals, y_vals, s=size, c=color, zorder=5)
