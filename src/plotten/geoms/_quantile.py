from __future__ import annotations

from typing import TYPE_CHECKING

from plotten.stats._quantile import StatQuantile

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import build_line_kwargs


class GeomQuantile:
    """Draw quantile regression lines."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True
    known_params: frozenset[str] = frozenset({"color", "alpha", "linetype"})

    def __init__(
        self,
        quantiles: list[float] | None = None,
        n_points: int = 100,
    ) -> None:
        self._quantiles = quantiles if quantiles is not None else [0.25, 0.5, 0.75]
        self._n_points = n_points

    def default_stat(self) -> StatQuantile:
        return StatQuantile(quantiles=self._quantiles, n_points=self._n_points)

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs = build_line_kwargs(data, params)
        ax.plot(data["x"], data["y"], **kwargs)
