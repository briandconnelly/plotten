from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import draw_bars


class GeomCol(GeomRepr):
    """Draw bars with pre-computed heights (uses StatIdentity)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "width", "hatch"})

    def __init__(self, orientation: str = "x") -> None:
        self._orientation = orientation

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        draw_bars(data, ax, params, orientation=self._orientation)
