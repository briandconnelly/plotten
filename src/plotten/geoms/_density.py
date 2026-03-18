from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomDensity:
    """Draw density curves."""

    required_aes: frozenset[str] = frozenset({"x"})

    def __init__(self, fill: bool = True, alpha: float = 0.3) -> None:
        self._fill = fill
        self._alpha = alpha

    def default_stat(self) -> Any:
        from plotten.stats._density import StatDensity

        return StatDensity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        alpha = params.get("alpha", self._alpha)
        fill = params.get("fill", self._fill)

        color_vals = data.get("color")

        if color_vals and isinstance(color_vals, list):
            # Check if these are hex color strings (grouped data)
            unique_colors = list(dict.fromkeys(color_vals))  # preserve order
            x_vals = data["x"]
            y_vals = data["y"]

            for hex_color in unique_colors:
                # Extract points for this group
                gx = [x_vals[i] for i, c in enumerate(color_vals) if c == hex_color]
                gy = [y_vals[i] for i, c in enumerate(color_vals) if c == hex_color]
                ax.plot(gx, gy, color=hex_color)
                if fill:
                    ax.fill_between(gx, gy, 0, alpha=alpha, color=hex_color)
        else:
            color = params.get("color", "#3366CC")
            ax.plot(data["x"], data["y"], color=color)
            if fill:
                ax.fill_between(data["x"], data["y"], 0, alpha=alpha, color=color)
