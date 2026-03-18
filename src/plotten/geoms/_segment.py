from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomSegment:
    """Draw line segments from (x, y) to (xend, yend)."""

    required_aes: frozenset[str] = frozenset({"x", "y", "xend", "yend"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        xs = data["x"]
        ys = data["y"]
        xends = data["xend"]
        yends = data["yend"]

        default_color = params.get("color", "#333333")
        default_alpha = params.get("alpha", 1.0)
        default_linestyle = params.get("linetype", "-")
        default_linewidth = params.get("size", 0.8)
        arrow = params.get("arrow", False)

        colors = data.get("color")
        alphas = data.get("alpha")
        linetypes = data.get("linetype")
        sizes = data.get("size")

        per_segment = (
            (isinstance(colors, list) and len(set(colors)) > 1)
            or (isinstance(alphas, list) and len(set(alphas)) > 1)
            or (isinstance(linetypes, list) and len(set(linetypes)) > 1)
            or (isinstance(sizes, list) and len(set(sizes)) > 1)
            or arrow
        )

        if per_segment or arrow:
            for i in range(len(xs)):
                c = colors[i] if isinstance(colors, list) else (colors or default_color)
                a = alphas[i] if isinstance(alphas, list) else (alphas or default_alpha)
                ls = (
                    linetypes[i]
                    if isinstance(linetypes, list)
                    else (linetypes or default_linestyle)
                )
                lw = sizes[i] if isinstance(sizes, list) else (sizes or default_linewidth)

                if arrow:
                    ax.annotate(
                        "",
                        xy=(xends[i], yends[i]),
                        xytext=(xs[i], ys[i]),
                        arrowprops={
                            "arrowstyle": "->",
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

            c = colors[0] if isinstance(colors, list) else (colors or default_color)
            a = alphas[0] if isinstance(alphas, list) else (alphas or default_alpha)
            ls = linetypes[0] if isinstance(linetypes, list) else (linetypes or default_linestyle)
            lw = sizes[0] if isinstance(sizes, list) else (sizes or default_linewidth)

            segments = [[(xs[i], ys[i]), (xends[i], yends[i])] for i in range(len(xs))]
            lc = LineCollection(segments, colors=c, alpha=a, linestyles=ls, linewidths=lw)
            ax.add_collection(lc)
            ax.autoscale_view()
