from __future__ import annotations

from typing import TYPE_CHECKING, Any

from matplotlib.patches import Polygon

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _scalar(values: list) -> Any:
    """Extract a single value from a uniform-group list."""
    return values[0]


class GeomPolygon:
    """Draw filled polygons."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        x_vals = data["x"]
        y_vals = data["y"]
        vertices = list(zip(x_vals, y_vals, strict=True))

        fill_color = data.get("fill")
        if isinstance(fill_color, list):
            fill_color = _scalar(fill_color)
        if fill_color is None:
            fill_color = params.get("fill", "#3366CC")

        edge_color = data.get("color")
        if isinstance(edge_color, list):
            edge_color = _scalar(edge_color)
        if edge_color is None:
            edge_color = params.get("color", "black")

        alpha = params.get("alpha", 0.5)

        patch = Polygon(
            vertices, closed=True, facecolor=fill_color, edgecolor=edge_color, alpha=alpha
        )
        ax.add_patch(patch)
        ax.autoscale_view()
