from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import build_fill_kwargs


class GeomBar:
    """Draw bars using ax.bar."""

    required_aes: frozenset[str] = frozenset({"x"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "width", "hatch"})

    def default_stat(self) -> Any:
        from plotten.stats._count import StatCount

        return StatCount()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs = build_fill_kwargs(data, params)
        width = params.get("width", 0.8)
        ax.bar(data["x"], data["y"], width=width, **kwargs)
