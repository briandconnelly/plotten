from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import build_line_kwargs


class GeomStep(GeomRepr):
    """Draw step lines using ax.step."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True
    legend_key: str = "line"
    known_params: frozenset[str] = frozenset(
        {"color", "alpha", "linetype", "linewidth", "direction", "size"}
    )

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs = build_line_kwargs(data, params)
        kwargs["where"] = params.get("direction", "mid")
        ax.step(data["x"], data["y"], **kwargs)
