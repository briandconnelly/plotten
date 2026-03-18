from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase
from plotten.stats._bin import StatBin


class GeomHistogram(GeomBase):
    """Draw histogram bars."""

    required_aes: frozenset[str] = frozenset({"x"})
    default_stat: type = StatBin

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
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
