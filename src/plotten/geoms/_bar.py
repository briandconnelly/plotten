from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase


class GeomBar(GeomBase):
    """Draw bars using ax.bar."""

    required_aes: frozenset[str] = frozenset({"x"})

    def default_stat(self) -> Any:
        from plotten.stats._count import StatCount

        return StatCount()

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "fill" in data:
            kwargs["color"] = data["fill"]
        elif "color" in data and isinstance(data["color"], str):
            kwargs["color"] = data["color"]
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]
        width = params.get("width", 0.8)
        ax.bar(data["x"], data["y"], width=width, **kwargs)
