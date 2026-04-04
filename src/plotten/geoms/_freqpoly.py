from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import build_line_kwargs


class GeomFreqpoly(GeomRepr):
    """Draw a frequency polygon (line through bin midpoints)."""

    required_aes: frozenset[str] = frozenset({"x"})
    supports_group_splitting: bool = True
    legend_key: str = "line"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linetype", "linewidth", "size"})
    warn_row_threshold: int | None = None

    def default_stat(self) -> Any:
        from plotten.stats._bin import StatBin

        return StatBin()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs = build_line_kwargs(data, params)
        ax.plot(data["x"], data["y"], **kwargs)
