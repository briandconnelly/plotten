from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_GEOM_FILL
from plotten.geoms._base import GeomRepr

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomTile(GeomRepr):
    """Draw rectangular tiles (heatmap cells)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset(
        {"fill", "color", "alpha", "width", "height", "hatch"}
    )

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.patches import Rectangle

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
                fc = params.get("fill", DEFAULT_GEOM_FILL)

            rect_kwargs: dict[str, Any] = {
                "facecolor": fc,
                "alpha": alpha,
                "edgecolor": params.get("color", "white"),
                "linewidth": params.get("linewidth", 0.5),
            }
            hatch = data.get("hatch", params.get("hatch"))
            if hatch is not None:
                rect_kwargs["hatch"] = hatch[i] if isinstance(hatch, list) else hatch
            rect = Rectangle(
                (x - width / 2, y - height / 2),
                width,
                height,
                **rect_kwargs,
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
