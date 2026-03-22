"""Significance bracket geom."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomSignif:
    """Draw significance brackets with p-value labels."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    legend_key: str = "rect"
    known_params: frozenset[str] = frozenset({"color", "size", "fontsize"})

    def __init__(
        self,
        tip_length: float = 0.02,
        text_format: str = "stars",
        **kwargs: Any,
    ) -> None:
        self._tip_length = tip_length
        self._text_format = text_format
        self._kwargs = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        linewidth = params.get("size", 0.8)
        fontsize = params.get("fontsize", 9)

        # _signif_ prefixed columns hold numeric positions (avoid x-scale pollution)
        xmins = data.get("_signif_xmin", data.get("xmin", []))
        xmaxs = data.get("_signif_xmax", data.get("xmax", []))
        ys = data["y"]
        labels = data.get("label", [""] * len(ys))
        p_values = data.get("p_value", [1.0] * len(ys))

        ylo, yhi = ax.get_ylim()
        tip = self._tip_length * (yhi - ylo)

        for i in range(len(xmins)):
            xmin_v = xmins[i] if isinstance(xmins, list) else xmins
            xmax_v = xmaxs[i] if isinstance(xmaxs, list) else xmaxs
            y_v = ys[i]

            # Draw bracket: vertical ticks + horizontal bar
            ax.plot(
                [xmin_v, xmin_v, xmax_v, xmax_v],
                [y_v - tip, y_v, y_v, y_v - tip],
                color=color,
                linewidth=linewidth,
                clip_on=False,
            )

            # Label
            if self._text_format == "p-value":
                lbl = f"p = {p_values[i]:.3g}"
            else:
                lbl = labels[i] if isinstance(labels, list) else labels

            ax.text(
                (xmin_v + xmax_v) / 2,
                y_v + tip * 0.3,
                str(lbl),
                ha="center",
                va="bottom",
                color=color,
                fontsize=fontsize,
            )
