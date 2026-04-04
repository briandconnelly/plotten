from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomContour(GeomRepr):
    """Draw contour lines from gridded x, y, z data."""

    required_aes: frozenset[str] = frozenset({"x", "y", "z"})
    supports_group_splitting: bool = False
    legend_key: str = "line"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linewidth"})

    def default_stat(self) -> Any:
        from plotten.stats._contour import StatContour

        return StatContour()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        import numpy as np

        x = np.asarray(data["x"], dtype=float)
        y = np.asarray(data["y"], dtype=float)
        z = np.asarray(data["z"], dtype=float)

        xi = np.sort(np.unique(x))
        yi = np.sort(np.unique(y))
        zz = z.reshape(len(yi), len(xi))

        levels = params.get("bins", 10)
        colors = params.get("color")
        linewidths = params.get("linewidth", 0.5)
        ax.contour(xi, yi, zz, levels=levels, colors=colors, linewidths=linewidths)


class GeomContourFilled(GeomRepr):
    """Draw filled contours from gridded x, y, z data."""

    required_aes: frozenset[str] = frozenset({"x", "y", "z"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"fill", "alpha"})

    def default_stat(self) -> Any:
        from plotten.stats._contour import StatContour

        return StatContour()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        import numpy as np

        x = np.asarray(data["x"], dtype=float)
        y = np.asarray(data["y"], dtype=float)
        z = np.asarray(data["z"], dtype=float)

        xi = np.sort(np.unique(x))
        yi = np.sort(np.unique(y))
        zz = z.reshape(len(yi), len(xi))

        levels = params.get("bins", 10)
        alpha = params.get("alpha", 1.0)
        cmap = params.get("cmap", "viridis")
        ax.contourf(xi, yi, zz, levels=levels, alpha=alpha, cmap=cmap)
