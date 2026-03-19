from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten.stats._quantile import StatQuantile

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomQuantile:
    """Draw quantile regression lines."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True

    def __init__(
        self,
        quantiles: list[float] | None = None,
        n_points: int = 100,
    ) -> None:
        self._quantiles = quantiles if quantiles is not None else [0.25, 0.5, 0.75]
        self._n_points = n_points

    def default_stat(self) -> StatQuantile:
        return StatQuantile(quantiles=self._quantiles, n_points=self._n_points)

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "color" in data:
            color = data["color"]
            kwargs["color"] = color[0] if isinstance(color, list) else color
        elif "color" in params:
            kwargs["color"] = params["color"]
        if "alpha" in data:
            alpha = data["alpha"]
            kwargs["alpha"] = alpha[0] if isinstance(alpha, list) else alpha
        elif "alpha" in params:
            kwargs["alpha"] = params["alpha"]
        if "linetype" in data:
            lt = data["linetype"]
            kwargs["linestyle"] = lt[0] if isinstance(lt, list) else lt
        elif "linetype" in params:
            kwargs["linestyle"] = params["linetype"]
        if "size" in data:
            size = data["size"]
            kwargs["linewidth"] = size[0] if isinstance(size, list) else size
        elif "size" in params:
            kwargs["linewidth"] = params["size"]

        ax.plot(data["x"], data["y"], **kwargs)
