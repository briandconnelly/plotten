"""Ridge plot geom -- stacked density curves."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

# Default discrete palette for ridge groups.
_RIDGE_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


class GeomDensityRidges:
    """Draw filled density curves stacked vertically by group."""

    required_aes: frozenset[str] = frozenset({"x", "ymin", "ymax"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        x = data["x"]
        ymin = data["ymin"]
        ymax = data["ymax"]
        groups = data.get("group", [None] * len(x))

        fill = params.get("fill")
        alpha = params.get("alpha", 0.6)
        color = params.get("color", "black")
        linewidth = params.get("linewidth", 0.5)

        unique_groups = sorted(set(groups), key=lambda g: str(g))

        for i, group in enumerate(unique_groups):
            indices = [j for j, g in enumerate(groups) if g == group]
            gx = [x[j] for j in indices]
            gymin = [ymin[j] for j in indices]
            gymax = [ymax[j] for j in indices]

            group_fill = fill if fill else _RIDGE_PALETTE[i % len(_RIDGE_PALETTE)]
            ax.fill_between(gx, gymin, gymax, alpha=alpha, color=group_fill, linewidth=0)
            ax.plot(gx, gymax, color=color, linewidth=linewidth)

        # Set y-ticks to group names
        if unique_groups and unique_groups[0] is not None:
            group_positions = list(range(len(unique_groups)))
            ax.set_yticks(group_positions)
            ax.set_yticklabels([str(g) for g in unique_groups])
