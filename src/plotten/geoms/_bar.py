from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomBar:
    """Draw bars using ax.bar."""

    required_aes: frozenset[str] = frozenset({"x"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "width", "hatch"})

    def default_stat(self) -> Any:
        from plotten.stats._count import StatCount

        return StatCount()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}
        if "fill" in data:
            kwargs["color"] = data["fill"]
        elif "color" in data and isinstance(data["color"], str):
            kwargs["color"] = data["color"]
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]
        hatch = data.get("hatch", params.get("hatch"))
        if hatch is not None:
            if isinstance(hatch, list):
                hatch = hatch[0] if hatch else None
            if hatch is not None:
                kwargs["hatch"] = hatch
        width = params.get("width", 0.8)
        ax.bar(data["x"], data["y"], width=width, **kwargs)
