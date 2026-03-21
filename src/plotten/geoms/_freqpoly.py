from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import build_line_kwargs


class GeomFreqpoly:
    """Draw a frequency polygon (line through bin midpoints)."""

    required_aes: frozenset[str] = frozenset({"x"})
    supports_group_splitting: bool = True
    known_params: frozenset[str] = frozenset({"color", "alpha", "linetype", "linewidth"})

    def default_stat(self) -> Any:
        from plotten.stats._bin import StatBin

        return StatBin()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs = build_line_kwargs(data, params)
        ax.plot(data["x"], data["y"], **kwargs)
