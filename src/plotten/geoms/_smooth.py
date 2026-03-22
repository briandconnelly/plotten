from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.stats._smooth import StatSmooth

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomSmooth:
    """Draw a smooth fit line with optional CI ribbon."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True
    legend_key: str = "line"
    known_params: frozenset[str] = frozenset({"color", "alpha", "linetype"})

    def __init__(
        self, method: str = "loess", se: bool = True, degree: int = 2, **kwargs: Any
    ) -> None:
        self._method = method
        self._se = se
        self._degree = degree

    def default_stat(self) -> StatSmooth:
        return StatSmooth(method=self._method, se=self._se, degree=self._degree)

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}
        color = params.get("color", "#3366CC")
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]

        ax.plot(data["x"], data["y"], color=color, **kwargs)

        # CI ribbon
        se = params.get("se", self._se)
        if se and "ymin" in data and "ymax" in data and data["ymin"] != data["ymax"]:
            ax.fill_between(
                data["x"],
                data["ymin"],
                data["ymax"],
                alpha=0.2,
                color=color,
            )
