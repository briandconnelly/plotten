from __future__ import annotations

from typing import TYPE_CHECKING, Any

from matplotlib.patches import Rectangle

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomTile:
    """Draw rectangular tiles (heatmap cells)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        width = params.get("width", 1.0)
        height = params.get("height", 1.0)
        text_color = params.get("text_color", "black")
        text_size = params.get("text_size", 10)
        alpha = params.get("alpha", 1.0)

        x_vals = data["x"]
        y_vals = data["y"]
        fill_vals = data.get("fill")
        label_vals = data.get("label")

        for i in range(len(x_vals)):
            x = x_vals[i]
            y = y_vals[i]

            # Determine fill color
            if fill_vals is not None:
                fc = fill_vals[i] if isinstance(fill_vals, list) else fill_vals
            else:
                fc = params.get("fill", "#4C72B0")

            rect = Rectangle(
                (x - width / 2, y - height / 2),
                width,
                height,
                facecolor=fc,
                alpha=alpha,
                edgecolor=params.get("color", "white"),
                linewidth=params.get("linewidth", 0.5),
            )
            ax.add_patch(rect)

            if label_vals is not None:
                lbl = label_vals[i]
                ax.text(
                    x,
                    y,
                    str(lbl),
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=text_size,
                )

        ax.autoscale_view()
