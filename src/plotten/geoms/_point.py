from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase


class GeomPoint(GeomBase):
    """Draw points using ax.scatter."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "color" in data:
            kwargs["c"] = data["color"]
        if "size" in data:
            kwargs["s"] = data["size"]
        elif "size" in params:
            kwargs["s"] = params["size"]
        if "alpha" in data:
            kwargs["alpha"] = data["alpha"]
        elif "alpha" in params:
            kwargs["alpha"] = params["alpha"]
        ax.scatter(data["x"], data["y"], **kwargs)
