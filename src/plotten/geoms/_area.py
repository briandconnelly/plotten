from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import scalar


class GeomArea:
    """Draw filled area under a curve."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}
        if "fill" in data:
            fill = data["fill"]
            kwargs["color"] = scalar(fill) if isinstance(fill, list) else fill
        elif "color" in params:
            kwargs["color"] = params["color"]
        kwargs["alpha"] = params.get("alpha", 0.5)
        if "linewidth" in data:
            lw = data["linewidth"]
            kwargs["linewidth"] = scalar(lw) if isinstance(lw, list) else lw
        elif "linewidth" in params:
            kwargs["linewidth"] = params["linewidth"]
        hatch = data.get("hatch", params.get("hatch"))
        if hatch is not None:
            kwargs["hatch"] = scalar(hatch) if isinstance(hatch, list) else hatch
        ax.fill_between(data["x"], data["y"], 0, **kwargs)
