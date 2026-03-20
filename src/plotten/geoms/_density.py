from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import scalar


class GeomDensity:
    """Draw density curves."""

    required_aes: frozenset[str] = frozenset({"x"})
    supports_group_splitting: bool = True
    known_params: frozenset[str] = frozenset({"color", "fill", "alpha"})

    def __init__(self, fill: bool = True, alpha: float = 0.3) -> None:
        self._fill = fill
        self._alpha = alpha

    def default_stat(self) -> Any:
        from plotten.stats._density import StatDensity

        return StatDensity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        alpha = params.get("alpha", self._alpha)
        fill = params.get("fill", self._fill)

        color = data.get("color", params.get("color", "#3366CC"))
        if isinstance(color, list):
            color = scalar(color)

        ax.plot(data["x"], data["y"], color=color)
        if fill:
            fill_kw: dict[str, Any] = {"alpha": alpha, "color": color}
            hatch = data.get("hatch", params.get("hatch"))
            if hatch is not None:
                fill_kw["hatch"] = scalar(hatch) if isinstance(hatch, list) else hatch
            ax.fill_between(data["x"], data["y"], 0, **fill_kw)
