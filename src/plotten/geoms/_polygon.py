from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import scalar


class GeomPolygon:
    """Draw filled polygons."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "hatch"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.patches import Polygon

        x_vals = data["x"]
        y_vals = data["y"]
        vertices = list(zip(x_vals, y_vals, strict=True))

        fill_color = data.get("fill")
        if isinstance(fill_color, list):
            fill_color = scalar(fill_color)
        if fill_color is None:
            fill_color = params.get("fill", "#3366CC")

        edge_color = data.get("color")
        if isinstance(edge_color, list):
            edge_color = scalar(edge_color)
        if edge_color is None:
            edge_color = params.get("color", "black")

        alpha = params.get("alpha", 0.5)

        hatch = data.get("hatch", params.get("hatch"))
        if isinstance(hatch, list):
            hatch = scalar(hatch)
        patch_kwargs: dict[str, Any] = {
            "closed": True,
            "facecolor": fill_color,
            "edgecolor": edge_color,
            "alpha": alpha,
        }
        if hatch is not None:
            patch_kwargs["hatch"] = hatch
        patch = Polygon(vertices, **patch_kwargs)
        ax.add_patch(patch)
        ax.autoscale_view()
