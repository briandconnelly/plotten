from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomRect:
    """Draw rectangles defined by xmin, xmax, ymin, ymax."""

    required_aes: frozenset[str] = frozenset({"xmin", "xmax", "ymin", "ymax"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.patches import Rectangle

        xmins = data["xmin"]
        xmaxs = data["xmax"]
        ymins = data["ymin"]
        ymaxs = data["ymax"]

        default_fill = params.get("fill", "#4C72B0")
        default_color = params.get("color", "none")
        default_alpha = params.get("alpha", 0.5)

        fill_vals = data.get("fill")
        color_vals = data.get("color")
        alpha_vals = data.get("alpha")
        hatch_vals = data.get("hatch", params.get("hatch"))

        for i in range(len(xmins)):
            fc = fill_vals[i] if isinstance(fill_vals, list) else (fill_vals or default_fill)
            ec = color_vals[i] if isinstance(color_vals, list) else (color_vals or default_color)
            a = alpha_vals[i] if isinstance(alpha_vals, list) else (alpha_vals or default_alpha)

            width = xmaxs[i] - xmins[i]
            height = ymaxs[i] - ymins[i]

            rect_kwargs: dict[str, Any] = {
                "facecolor": fc,
                "edgecolor": ec,
                "alpha": a,
            }
            if hatch_vals is not None:
                h = hatch_vals[i] if isinstance(hatch_vals, list) else hatch_vals
                rect_kwargs["hatch"] = h
            rect = Rectangle(
                (xmins[i], ymins[i]),
                width,
                height,
                **rect_kwargs,
            )
            ax.add_patch(rect)

        ax.autoscale_view()
