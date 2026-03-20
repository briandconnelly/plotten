from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_GEOM_FILL

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomCrossbar:
    """Draw crossbars (box from ymin to ymax with line at y)."""

    required_aes: frozenset[str] = frozenset({"x", "y", "ymin", "ymax"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.patches import Rectangle

        width = params.get("width", 0.5)
        fill_color = params.get("fill", DEFAULT_GEOM_FILL)
        edge_color = params.get("color", "black")
        alpha = params.get("alpha", 0.7)
        hw = width / 2

        x_vals = data["x"]
        y_vals = data["y"]
        ymin_vals = data["ymin"]
        ymax_vals = data["ymax"]

        for i in range(len(x_vals)):
            x = x_vals[i]
            ymin = ymin_vals[i]
            ymax = ymax_vals[i]
            y = y_vals[i]

            rect = Rectangle(
                (x - hw, ymin),
                width,
                ymax - ymin,
                facecolor=fill_color,
                edgecolor=edge_color,
                alpha=alpha,
            )
            ax.add_patch(rect)
            ax.hlines(y, x - hw, x + hw, colors=edge_color, linewidth=2)

        ax.autoscale_view()
