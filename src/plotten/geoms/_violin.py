from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from plotten._defaults import DEFAULT_GEOM_FILL

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomViolin:
    """Draw violin plots (mirrored KDE per group)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "width", "hatch"})

    def default_stat(self) -> Any:
        from plotten.stats._violin import StatViolin

        return StatViolin()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        fill_color = params.get("fill", DEFAULT_GEOM_FILL)
        alpha = params.get("alpha", 0.7)
        line_color = params.get("color", "black")

        x_vals = data["x"]
        n = len(x_vals)

        # Use integer positions for categorical x
        positions = list(range(n))

        for i in range(n):
            pos = positions[i]
            y_grid = cast("list[float]", data["y_grid"][i])
            density = cast("list[float]", data["density"][i])

            if not y_grid or not density:
                continue

            # Mirror the density around the position
            fill_kw: dict[str, Any] = {
                "alpha": alpha,
                "color": fill_color,
                "edgecolor": line_color,
                "linewidth": 1,
            }
            hatch = params.get("hatch")
            if hatch is not None:
                fill_kw["hatch"] = hatch
            ax.fill_betweenx(
                y_grid,
                [pos - d for d in density],
                [pos + d for d in density],
                **fill_kw,
            )
