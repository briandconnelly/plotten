from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._aes import Aes
from plotten._enums import AnnotationType
from plotten._layer import Layer
from plotten.geoms._text import GeomText

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class _GeomAnnotRect:
    """Internal geom for annotate("rect")."""

    required_aes: frozenset[str] = frozenset()

    def __init__(self, xmin: float, xmax: float, ymin: float, ymax: float, **kwargs: Any) -> None:
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.kwargs = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
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


class _GeomAnnotSegment:
    """Internal geom for annotate("segment")."""

    required_aes: frozenset[str] = frozenset()

    def __init__(self, x: float, y: float, xend: float, yend: float, **kwargs: Any) -> None:
        self._x = x
        self._y = y
        self._xend = xend
        self._yend = yend
        self.kwargs = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from plotten._arrow import Arrow

        color = self.kwargs.get("color", params.get("color", "black"))
        linestyle = self.kwargs.get("linetype", params.get("linetype", "solid"))
        linewidth = self.kwargs.get("size", params.get("size", 1))
        arrow_param = self.kwargs.get("arrow", params.get("arrow", False))

        if arrow_param:
            if isinstance(arrow_param, Arrow):
                arrowstyle = arrow_param.to_arrowstyle()
            else:
                arrowstyle = "->"
            ax.annotate(
                "",
                xy=(self._xend, self._yend),
                xytext=(self._x, self._y),
                arrowprops={
                    "arrowstyle": arrowstyle,
                    "color": color,
                    "linestyle": linestyle,
                    "linewidth": linewidth,
                },
            )
        else:
            ax.plot(
                [self._x, self._xend],
                [self._y, self._yend],
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
            )


class _GeomAnnotCurve:
    """Internal geom for annotate("curve")."""

    required_aes: frozenset[str] = frozenset()

    def __init__(self, x: float, y: float, xend: float, yend: float, **kwargs: Any) -> None:
        self._x = x
        self._y = y
        self._xend = xend
        self._yend = yend
        self.kwargs = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.patches import FancyArrowPatch

        from plotten._arrow import Arrow

        color = self.kwargs.get("color", params.get("color", "black"))
        linewidth = self.kwargs.get("size", params.get("size", 1))
        curvature = self.kwargs.get("curvature", 0.3)
        arrow_param = self.kwargs.get("arrow", params.get("arrow", False))

        if isinstance(arrow_param, Arrow):
            arrowstyle = arrow_param.to_arrowstyle()
        elif arrow_param:
            arrowstyle = "->"
        else:
            arrowstyle = "-"

        patch = FancyArrowPatch(
            posA=(self._x, self._y),
            posB=(self._xend, self._yend),
            connectionstyle=f"arc3,rad={curvature}",
            arrowstyle=arrowstyle,
            color=color,
            linewidth=linewidth,
        )
        ax.add_patch(patch)


class _GeomAnnotBracket:
    """Internal geom for annotate("bracket")."""

    required_aes: frozenset[str] = frozenset()

    def __init__(
        self,
        xmin: float,
        xmax: float,
        y: float,
        label: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._xmin = xmin
        self._xmax = xmax
        self._y = y
        self._label = label
        self.kwargs = kwargs

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = self.kwargs.get("color", params.get("color", "black"))
        linewidth = self.kwargs.get("size", params.get("size", 1))
        direction = self.kwargs.get("direction", "up")
        tip_length = self.kwargs.get("tip_length", 0.02)

        # Get axis range for tip_length scaling
        ylo, yhi = ax.get_ylim()
        tip = tip_length * (yhi - ylo) * (1 if direction == "up" else -1)

        # Vertical ticks + horizontal bar
        ax.plot(
            [self._xmin, self._xmin, self._xmax, self._xmax],
            [self._y, self._y + tip, self._y + tip, self._y],
            color=color,
            linewidth=linewidth,
            clip_on=False,
        )

        # Optional label centered above/below
        if self._label:
            label_y = self._y + tip * 1.5
            va = "bottom" if direction == "up" else "top"
            ax.text(
                (self._xmin + self._xmax) / 2,
                label_y,
                self._label,
                ha="center",
                va=va,
                color=color,
                fontsize=params.get("fontsize", 10),
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
    match geom_type:
        case AnnotationType.TEXT:
            import narwhals as nw

            # Support text box styling
            bbox_props = {}
            box_fill = params.pop("box_fill", None)
            box_color = params.pop("box_color", None)
            box_pad = params.pop("box_pad", None)
            if box_fill is not None or box_color is not None:
                bbox_props["boxstyle"] = f"round,pad={box_pad or 0.3}"
                if box_fill is not None:
                    bbox_props["facecolor"] = box_fill
                if box_color is not None:
                    bbox_props["edgecolor"] = box_color
                params["bbox"] = bbox_props

            for _backend in ("polars", "pandas"):
                try:
                    inline_data = nw.from_dict(
                        {"x": [x], "y": [y], "label": [label]}, backend=_backend
                    )
                    break
                except ImportError:
                    continue
            else:
                msg = "Either polars or pandas must be installed"
                raise ImportError(msg)
            return Layer(
                geom=GeomText(), mapping=Aes(), params=params, data=nw.to_native(inline_data)
            )

        case AnnotationType.RECT:
            geom = _GeomAnnotRect(
                xmin=xmin or 0,
                xmax=xmax or 0,
                ymin=ymin or 0,
                ymax=ymax or 0,
                **params,
            )
            return Layer(geom=geom, mapping=Aes(), params={})

        case AnnotationType.SEGMENT:
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

        case AnnotationType.CURVE:
            xend = params.pop("xend", x)
            yend = params.pop("yend", y)
            geom = _GeomAnnotCurve(
                x=x or 0,
                y=y or 0,
                xend=xend or 0,
                yend=yend or 0,
                **params,
            )
            return Layer(geom=geom, mapping=Aes(), params={})

        case AnnotationType.BRACKET:
            geom = _GeomAnnotBracket(
                xmin=xmin or 0,
                xmax=xmax or 0,
                y=y or 0,
                label=label,
                **params,
            )
            return Layer(geom=geom, mapping=Aes(), params={})

        case _:
            msg = (
                f"Unknown annotation geom_type: {geom_type!r}. "
                f"Use 'text', 'rect', 'segment', 'curve', or 'bracket'."
            )
            raise ValueError(msg)
