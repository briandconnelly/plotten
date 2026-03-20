from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomLinerange:
    """Draw vertical lines from ymin to ymax."""

    required_aes: frozenset[str] = frozenset({"x", "ymin", "ymax"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset({"color", "alpha", "linewidth"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        linewidth = params.get("linewidth", 1)

        ax.vlines(data["x"], data["ymin"], data["ymax"], colors=color, linewidth=linewidth)
