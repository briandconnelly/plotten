from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_GEOM_FILL
from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomBoxplot(GeomRepr):
    """Draw boxplots."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"fill", "color", "alpha", "width", "hatch"})
    warn_row_threshold: int | None = None

    def __init__(self, orientation: str = "x") -> None:
        self._orientation = orientation

    def default_stat(self) -> Any:
        from plotten.stats._boxplot import StatBoxplot

        return StatBoxplot()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        width = params.get("width", 0.7)
        fill_color = params.get("fill", DEFAULT_GEOM_FILL)
        alpha = params.get("alpha", 0.7)
        line_color = params.get("color", "black")

        x_vals = data["x"]
        n = len(x_vals)
        horizontal = self._orientation == "y"

        for i in range(n):
            lower = data["lower"][i]
            upper = data["upper"][i]
            median = data["middle"][i]
            ymin = data["ymin"][i]
            ymax = data["ymax"][i]
            outliers = data["outliers_y"][i]
            hw = width / 2

            # Box body
            bar_kw: dict[str, Any] = {
                "color": fill_color,
                "alpha": alpha,
                "edgecolor": line_color,
                "linewidth": 1,
            }
            hatch = params.get("hatch")
            if hatch is not None:
                bar_kw["hatch"] = hatch

            if horizontal:
                ax.barh(i, upper - lower, left=lower, height=width, **bar_kw)
                ax.vlines(median, i - hw, i + hw, colors=line_color, linewidth=2)
                ax.hlines(i, ymin, lower, colors=line_color, linewidth=1)
                ax.hlines(i, upper, ymax, colors=line_color, linewidth=1)
                cap_hw = hw * 0.5
                ax.vlines(ymin, i - cap_hw, i + cap_hw, colors=line_color, linewidth=1)
                ax.vlines(ymax, i - cap_hw, i + cap_hw, colors=line_color, linewidth=1)
                if outliers:
                    ax.scatter(outliers, [i] * len(outliers), color=line_color, s=20, zorder=5)
            else:
                ax.bar(i, upper - lower, bottom=lower, width=width, **bar_kw)
                ax.hlines(median, i - hw, i + hw, colors=line_color, linewidth=2)
                ax.vlines(i, ymin, lower, colors=line_color, linewidth=1)
                ax.vlines(i, upper, ymax, colors=line_color, linewidth=1)
                cap_hw = hw * 0.5
                ax.hlines(ymin, i - cap_hw, i + cap_hw, colors=line_color, linewidth=1)
                ax.hlines(ymax, i - cap_hw, i + cap_hw, colors=line_color, linewidth=1)
                if outliers:
                    ax.scatter([i] * len(outliers), outliers, color=line_color, s=20, zorder=5)
