from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import build_fill_kwargs


class GeomRibbon(GeomRepr):
    """Draw a filled band between ymin and ymax."""

    required_aes: frozenset[str] = frozenset({"x", "ymin", "ymax"})
    supports_group_splitting: bool = True
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "linewidth", "hatch"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs = build_fill_kwargs(data, params, default_alpha=0.3)
        ax.fill_between(data["x"], data["ymin"], data["ymax"], **kwargs)
