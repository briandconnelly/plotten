from __future__ import annotations

from typing import Any

from plotten._aes import Aes
from plotten._layer import Layer
from plotten.geoms._base import GeomBase
from plotten.geoms._text import GeomText


class _GeomAnnotRect(GeomBase):
    """Internal geom for annotate("rect")."""

    required_aes: frozenset[str] = frozenset()

    def __init__(
        self, xmin: float, xmax: float, ymin: float, ymax: float, **kwargs: Any
    ) -> None:
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.kwargs = kwargs

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        from matplotlib.patches import Rectangle

        alpha = self.kwargs.get("alpha", params.get("alpha", 0.3))
        color = self.kwargs.get("color", params.get("color", "gray"))
        fill = self.kwargs.get("fill", params.get("fill", color))
        rect = Rectangle(
            (self.xmin, self.ymin),
            self.xmax - self.xmin,
            self.ymax - self.ymin,
            facecolor=fill,
            edgecolor=color,
            alpha=alpha,
        )
        ax.add_patch(rect)


class _GeomAnnotSegment(GeomBase):
    """Internal geom for annotate("segment")."""

    required_aes: frozenset[str] = frozenset()

    def __init__(
        self, x: float, y: float, xend: float, yend: float, **kwargs: Any
    ) -> None:
        self._x = x
        self._y = y
        self._xend = xend
        self._yend = yend
        self.kwargs = kwargs

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        color = self.kwargs.get("color", params.get("color", "black"))
        linestyle = self.kwargs.get("linetype", params.get("linetype", "solid"))
        linewidth = self.kwargs.get("size", params.get("size", 1))
        ax.plot(
            [self._x, self._xend],
            [self._y, self._yend],
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
        )


def annotate(
    geom_type: str,
    x: float | None = None,
    y: float | None = None,
    xmin: float | None = None,
    xmax: float | None = None,
    ymin: float | None = None,
    ymax: float | None = None,
    label: str | None = None,
    **params: Any,
) -> Layer:
    """Create an annotation layer.

    Supports geom_type="text", "rect", or "segment".
    """
    if geom_type == "text":
        import polars as pl

        inline_data = pl.DataFrame({"x": [x], "y": [y], "label": [label]})
        return Layer(geom=GeomText(), mapping=Aes(), params=params, data=inline_data)

    if geom_type == "rect":
        geom = _GeomAnnotRect(
            xmin=xmin or 0,
            xmax=xmax or 0,
            ymin=ymin or 0,
            ymax=ymax or 0,
            **params,
        )
        return Layer(geom=geom, mapping=Aes(), params={})

    if geom_type == "segment":
        xend = params.pop("xend", x)
        yend = params.pop("yend", y)
        geom = _GeomAnnotSegment(
            x=x or 0,
            y=y or 0,
            xend=xend or 0,
            yend=yend or 0,
            **params,
        )
        return Layer(geom=geom, mapping=Aes(), params={})

    msg = f"Unknown annotation geom_type: {geom_type!r}. Use 'text', 'rect', or 'segment'."
    raise ValueError(msg)
