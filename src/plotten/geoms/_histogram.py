from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomHistogram:
    """Draw histogram bars."""

    required_aes: frozenset[str] = frozenset({"x"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._bin import StatBin

        return StatBin()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}
        if "fill" in data:
            kwargs["color"] = data["fill"]
        elif "color" in params:
            kwargs["color"] = params["color"]
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]

        x_vals = data["x"]
        y_vals = data["y"]
        # Compute width from bin spacing
        if len(x_vals) > 1:
            width = x_vals[1] - x_vals[0]
        else:
            width = 1.0
        width = params.get("width", width)

        ax.bar(x_vals, y_vals, width=width, **kwargs)
