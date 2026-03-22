from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_GEOM_COLOR
from plotten._linetypes import resolve_linetype

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


def _per_value[T](values: list[T] | T | None, index: int, default: T) -> T:
    """Get per-element value from a list, scalar, or default."""
    if isinstance(values, list):
        return values[index]
    return values if values is not None else default


class GeomSegment:
    """Draw line segments from (x, y) to (xend, yend)."""

    required_aes: frozenset[str] = frozenset({"x", "y", "xend", "yend"})
    supports_group_splitting: bool = False
    legend_key: str = "line"
    known_params: frozenset[str] = frozenset(
        {"color", "alpha", "linetype", "linewidth", "size", "arrow"}
    )

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        xs = data["x"]
        ys = data["y"]
        xends = data["xend"]
        yends = data["yend"]

        default_color = params.get("color", DEFAULT_GEOM_COLOR)
        default_alpha = params.get("alpha", 1.0)
        default_linestyle = resolve_linetype(params.get("linetype", "-"))
        default_linewidth = params.get("size", 0.8)
        arrow = params.get("arrow", False)

        colors = data.get("color")
        alphas = data.get("alpha")
        linetypes = data.get("linetype")
        sizes = data.get("size")

        has_varying = any(
            isinstance(v, list) and len(set(v)) > 1 for v in (colors, alphas, linetypes, sizes)
        )

        if has_varying or arrow:
            for i in range(len(xs)):
                c = _per_value(colors, i, default_color)
                a = _per_value(alphas, i, default_alpha)
                ls = resolve_linetype(_per_value(linetypes, i, default_linestyle))
                lw = _per_value(sizes, i, default_linewidth)

                if arrow:
                    from plotten._arrow import Arrow

                    arrowstyle = arrow.to_arrowstyle() if isinstance(arrow, Arrow) else "->"
                    ax.annotate(
                        "",
                        xy=(xends[i], yends[i]),
                        xytext=(xs[i], ys[i]),
                        arrowprops={
                            "arrowstyle": arrowstyle,
                            "color": c,
                            "alpha": a,
                            "linestyle": ls,
                            "linewidth": lw,
                        },
                    )
                else:
                    ax.plot(
                        [xs[i], xends[i]],
                        [ys[i], yends[i]],
                        color=c,
                        alpha=a,
                        linestyle=ls,
                        linewidth=lw,
                    )
        else:
            from matplotlib.collections import LineCollection

            c = _per_value(colors, 0, default_color)
            a = _per_value(alphas, 0, default_alpha)
            ls = resolve_linetype(_per_value(linetypes, 0, default_linestyle))
            lw = _per_value(sizes, 0, default_linewidth)

            segments = [[(xs[i], ys[i]), (xends[i], yends[i])] for i in range(len(xs))]
            lc = LineCollection(segments, colors=c, alpha=a, linestyles=ls, linewidths=lw)
            ax.add_collection(lc)
            ax.autoscale_view()
