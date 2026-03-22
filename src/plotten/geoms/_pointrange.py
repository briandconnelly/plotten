from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomPointrange:
    """Draw point with vertical line from ymin to ymax."""

    required_aes: frozenset[str] = frozenset({"x", "y", "ymin", "ymax"})
    supports_group_splitting: bool = False
    legend_key: str = "point"
    known_params: frozenset[str] = frozenset({"color", "alpha", "size"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        size = params.get("size", 30)
        linewidth = params.get("linewidth", 1)

        x_vals = data["x"]
        y_vals = data["y"]
        ymin_vals = data["ymin"]
        ymax_vals = data["ymax"]

        ax.vlines(x_vals, ymin_vals, ymax_vals, colors=color, linewidth=linewidth)
        ax.scatter(x_vals, y_vals, s=size, c=color, zorder=5)
