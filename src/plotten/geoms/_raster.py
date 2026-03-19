from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomRaster:
    """Draw a raster (grid of colored cells) using pcolormesh."""

    required_aes: frozenset[str] = frozenset({"x", "y", "z"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        x = np.asarray(data["x"], dtype=float)
        y = np.asarray(data["y"], dtype=float)
        z = np.asarray(data["z"], dtype=float)

        xi = np.sort(np.unique(x))
        yi = np.sort(np.unique(y))
        zz = z.reshape(len(yi), len(xi))

        cmap = params.get("cmap", "viridis")
        alpha = params.get("alpha", 1.0)
        ax.pcolormesh(xi, yi, zz, cmap=cmap, alpha=alpha, shading="auto")
