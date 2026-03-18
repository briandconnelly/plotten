from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase


class GeomLine(GeomBase):
    """Draw lines using ax.plot."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "color" in data and isinstance(data["color"], str):
            kwargs["color"] = data["color"]
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]
        if "linetype" in params:
            kwargs["linestyle"] = params["linetype"]
        ax.plot(data["x"], data["y"], **kwargs)
