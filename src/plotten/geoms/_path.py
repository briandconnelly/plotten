from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import build_line_kwargs


class GeomPath:
    """Draw lines connecting points in data order (not sorted by x)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True
    legend_key: str = "line"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linetype", "linewidth", "size"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs = build_line_kwargs(data, params)
        ax.plot(data["x"], data["y"], **kwargs)
