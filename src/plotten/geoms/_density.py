from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _scalar(values: list) -> Any:
    """Extract a single value from a uniform-group list."""
    return values[0]


class GeomDensity:
    """Draw density curves."""

    required_aes: frozenset[str] = frozenset({"x"})
    supports_group_splitting: bool = True

    def __init__(self, fill: bool = True, alpha: float = 0.3) -> None:
        self._fill = fill
        self._alpha = alpha

    def default_stat(self) -> Any:
        from plotten.stats._density import StatDensity

        return StatDensity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        alpha = params.get("alpha", self._alpha)
        fill = params.get("fill", self._fill)

        color = data.get("color", params.get("color", "#3366CC"))
        if isinstance(color, list):
            color = _scalar(color)

        ax.plot(data["x"], data["y"], color=color)
        if fill:
            ax.fill_between(data["x"], data["y"], 0, alpha=alpha, color=color)
