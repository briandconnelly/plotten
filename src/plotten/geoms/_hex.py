from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomHex:
    """Draw hexagonal bin plots using matplotlib's hexbin."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "bins"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        gridsize = params.get("bins", 30)
        cmap = params.get("cmap", "viridis")
        alpha = params.get("alpha", 1.0)
        ax.hexbin(data["x"], data["y"], gridsize=gridsize, cmap=cmap, alpha=alpha)
