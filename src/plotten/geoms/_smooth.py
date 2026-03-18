from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase
from plotten.stats._smooth import StatSmooth


class GeomSmooth(GeomBase):
    """Draw a smooth fit line with optional CI ribbon."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(self, method: str = "loess", se: bool = True, **kwargs: Any) -> None:
        self._method = method
        self._se = se

    def default_stat(self) -> StatSmooth:
        return StatSmooth(method=self._method, se=self._se)

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        color = params.get("color", "#3366CC")
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]

        ax.plot(data["x"], data["y"], color=color, **kwargs)

        # CI ribbon
        se = params.get("se", self._se)
        if se and "ymin" in data and "ymax" in data:
            if data["ymin"] != data["ymax"]:
                ax.fill_between(
                    data["x"],
                    data["ymin"],
                    data["ymax"],
                    alpha=0.2,
                    color=color,
                )
