from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomRug:
    """Draw rug marks (marginal tick marks) along axes."""

    required_aes: frozenset[str] = frozenset()
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.transforms import blended_transform_factory

        sides = params.get("sides", "b")
        length = params.get("length", 0.03)
        alpha = params.get("alpha", 0.5)
        color = params.get("color", "black")

        if "color" in data and isinstance(data["color"], str):
            color = data["color"]

        for side in sides:
            if side == "b" and "x" in data:
                trans = blended_transform_factory(ax.transData, ax.transAxes)
                ax.vlines(
                    data["x"],
                    0,
                    length,
                    transform=trans,
                    color=color,
                    alpha=alpha,
                    linewidth=0.5,
                )
            elif side == "t" and "x" in data:
                trans = blended_transform_factory(ax.transData, ax.transAxes)
                ax.vlines(
                    data["x"],
                    1 - length,
                    1,
                    transform=trans,
                    color=color,
                    alpha=alpha,
                    linewidth=0.5,
                )
            elif side == "l" and "y" in data:
                trans = blended_transform_factory(ax.transAxes, ax.transData)
                ax.hlines(
                    data["y"],
                    0,
                    length,
                    transform=trans,
                    color=color,
                    alpha=alpha,
                    linewidth=0.5,
                )
            elif side == "r" and "y" in data:
                trans = blended_transform_factory(ax.transAxes, ax.transData)
                ax.hlines(
                    data["y"],
                    1 - length,
                    1,
                    transform=trans,
                    color=color,
                    alpha=alpha,
                    linewidth=0.5,
                )
