from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase


class GeomArea(GeomBase):
    """Draw filled area under a curve."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "fill" in data:
            kwargs["color"] = data["fill"]
        elif "color" in params:
            kwargs["color"] = params["color"]
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]
        else:
            kwargs["alpha"] = 0.5
        ax.fill_between(data["x"], data["y"], 0, **kwargs)
