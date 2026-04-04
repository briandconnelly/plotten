"""Line segments from (x, y) at an angle and radius."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_GEOM_COLOR
from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomSpoke(GeomRepr):
    """Draw line segments from (x, y) at given angle and radius."""

    required_aes: frozenset[str] = frozenset({"x", "y", "angle", "radius"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linewidth", "size", "arrow"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        xs = data["x"]
        ys = data["y"]
        angles = data["angle"]
        radii = data["radius"]

        default_color = params.get("color", DEFAULT_GEOM_COLOR)
        default_alpha = params.get("alpha", 1.0)
        default_linewidth = params.get("size", 0.8)
        arrow = params.get("arrow", False)

        colors = data.get("color")
        alphas = data.get("alpha")

        for i in range(len(xs)):
            xend = xs[i] + radii[i] * math.cos(angles[i])
            yend = ys[i] + radii[i] * math.sin(angles[i])
            c = colors[i] if isinstance(colors, list) else (colors or default_color)
            a = alphas[i] if isinstance(alphas, list) else (alphas or default_alpha)

            if arrow:
                ax.annotate(
                    "",
                    xy=(xend, yend),
                    xytext=(xs[i], ys[i]),
                    arrowprops={
                        "arrowstyle": "->",
                        "color": c,
                        "alpha": a,
                        "linewidth": default_linewidth,
                    },
                )
            else:
                ax.plot(
                    [xs[i], xend],
                    [ys[i], yend],
                    color=c,
                    alpha=a,
                    linewidth=default_linewidth,
                )
