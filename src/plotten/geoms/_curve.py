"""Curved line segments using FancyArrowPatch."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_GEOM_COLOR
from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomCurve(GeomRepr):
    """Draw curved line segments from (x, y) to (xend, yend)."""

    required_aes: frozenset[str] = frozenset({"x", "y", "xend", "yend"})
    supports_group_splitting: bool = False
    legend_key: str = "line"
    known_params: frozenset[str] = frozenset(
        {"color", "alpha", "linewidth", "curvature", "arrow", "size"}
    )

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.patches import FancyArrowPatch

        xs = data["x"]
        ys = data["y"]
        xends = data["xend"]
        yends = data["yend"]

        curvature = params.get("curvature", 0.3)
        arrow = params.get("arrow", False)
        default_color = params.get("color", DEFAULT_GEOM_COLOR)
        default_alpha = params.get("alpha", 1.0)
        default_linewidth = params.get("size", 0.8)

        colors = data.get("color")
        alphas = data.get("alpha")

        for i in range(len(xs)):
            c = colors[i] if isinstance(colors, list) else (colors or default_color)
            a = alphas[i] if isinstance(alphas, list) else (alphas or default_alpha)
            lw = default_linewidth

            if arrow is True:
                arrowstyle = "->"
            elif arrow is False:
                arrowstyle = "-"
            else:
                # Arrow object — use its to_arrowstyle()
                arrowstyle = arrow.to_arrowstyle()

            patch = FancyArrowPatch(
                posA=(xs[i], ys[i]),
                posB=(xends[i], yends[i]),
                connectionstyle=f"arc3,rad={curvature}",
                arrowstyle=arrowstyle,
                color=c,
                alpha=a,
                linewidth=lw,
            )
            ax.add_patch(patch)

        ax.autoscale_view()
