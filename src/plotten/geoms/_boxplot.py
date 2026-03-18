from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomBoxplot:
    """Draw boxplots."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._boxplot import StatBoxplot

        return StatBoxplot()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        width = params.get("width", 0.7)
        fill_color = params.get("fill", "#4C72B0")
        alpha = params.get("alpha", 0.7)
        line_color = params.get("color", "black")

        x_vals = data["x"]
        n = len(x_vals)

        # Use integer positions for categorical x
        positions = list(range(n))

        for i in range(n):
            pos = positions[i]
            lower = data["lower"][i]
            upper = data["upper"][i]
            median = data["middle"][i]
            ymin = data["ymin"][i]
            ymax = data["ymax"][i]
            outliers = data["outliers_y"][i]
            hw = width / 2

            # Box body
            ax.bar(
                pos,
                upper - lower,
                bottom=lower,
                width=width,
                color=fill_color,
                alpha=alpha,
                edgecolor=line_color,
                linewidth=1,
            )

            # Median line
            ax.hlines(median, pos - hw, pos + hw, colors=line_color, linewidth=2)

            # Whiskers
            ax.vlines(pos, ymin, lower, colors=line_color, linewidth=1)
            ax.vlines(pos, upper, ymax, colors=line_color, linewidth=1)

            # Whisker caps
            cap_hw = hw * 0.5
            ax.hlines(ymin, pos - cap_hw, pos + cap_hw, colors=line_color, linewidth=1)
            ax.hlines(ymax, pos - cap_hw, pos + cap_hw, colors=line_color, linewidth=1)

            # Outliers
            if outliers:
                ax.scatter(
                    [pos] * len(outliers),
                    outliers,
                    color=line_color,
                    s=20,
                    zorder=5,
                )
