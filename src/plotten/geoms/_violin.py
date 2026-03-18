from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase


class GeomViolin(GeomBase):
    """Draw violin plots (mirrored KDE per group)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def default_stat(self) -> Any:
        from plotten.stats._violin import StatViolin

        return StatViolin()

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        fill_color = params.get("fill", "#4C72B0")
        alpha = params.get("alpha", 0.7)
        line_color = params.get("color", "black")

        x_vals = data["x"]
        n = len(x_vals)

        # Use integer positions for categorical x
        positions = list(range(n))

        for i in range(n):
            pos = positions[i]
            y_grid = data["y_grid"][i]
            density = data["density"][i]

            if not y_grid or not density:
                continue

            # Mirror the density around the position
            ax.fill_betweenx(
                y_grid,
                [pos - d for d in density],
                [pos + d for d in density],
                alpha=alpha,
                color=fill_color,
                edgecolor=line_color,
                linewidth=1,
            )
