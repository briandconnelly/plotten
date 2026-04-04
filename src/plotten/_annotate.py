from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from plotten._aes import Aes
from plotten._enums import AnnotationType
from plotten._layer import Layer
from plotten.geoms._text import GeomText

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


@dataclass(frozen=True, slots=True)
class _GeomAnnotRect:
    """Internal geom for annotate("rect")."""

    xmin: float
    xmax: float
    ymin: float
    ymax: float
    coord: str = "data"
    kwargs: dict[str, Any] = field(default_factory=dict)

    required_aes: ClassVar[frozenset[str]] = frozenset()
    supports_group_splitting: ClassVar[bool] = False
    legend_key: ClassVar[str] = "rect"
    known_params: ClassVar[frozenset[str]] = frozenset()

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        from matplotlib.patches import Rectangle

        alpha = self.kwargs.get("alpha", params.get("alpha", 0.3))
        color = self.kwargs.get("color", params.get("color", "gray"))
        fill = self.kwargs.get("fill", params.get("fill", color))
        transform = ax.transAxes if self.coord == "npc" else ax.transData
        rect = Rectangle(
            (self.xmin, self.ymin),
            self.xmax - self.xmin,
            self.ymax - self.ymin,
            facecolor=fill,
            edgecolor=color,
            alpha=alpha,
            transform=transform,
        )
        ax.add_patch(rect)


@dataclass(frozen=True, slots=True)
class _GeomAnnotSegment:
    """Internal geom for annotate("segment")."""

    x: float
    y: float
    xend: float
    yend: float
    coord: str = "data"
    kwargs: dict[str, Any] = field(default_factory=dict)

    required_aes: ClassVar[frozenset[str]] = frozenset()
    supports_group_splitting: ClassVar[bool] = False
    legend_key: ClassVar[str] = "line"
    known_params: ClassVar[frozenset[str]] = frozenset()

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
            xycoords = "axes fraction" if self.coord == "npc" else "data"
            ax.annotate(
                "",
                xy=(self.xend, self.yend),
                xytext=(self.x, self.y),
                xycoords=xycoords,
                textcoords=xycoords,
                arrowprops={
                    "arrowstyle": arrowstyle,
                    "color": color,
                    "linestyle": linestyle,
                    "linewidth": linewidth,
                },
            )
        else:
            transform = ax.transAxes if self.coord == "npc" else ax.transData
            ax.plot(
                [self.x, self.xend],
                [self.y, self.yend],
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                transform=transform,
            )


@dataclass(frozen=True, slots=True)
class _GeomAnnotCurve:
    """Internal geom for annotate("curve")."""

    x: float
    y: float
    xend: float
    yend: float
    coord: str = "data"
    kwargs: dict[str, Any] = field(default_factory=dict)

    required_aes: ClassVar[frozenset[str]] = frozenset()
    supports_group_splitting: ClassVar[bool] = False
    legend_key: ClassVar[str] = "line"
    known_params: ClassVar[frozenset[str]] = frozenset()

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

        patch_kwargs: dict[str, Any] = {
            "connectionstyle": f"arc3,rad={curvature}",
            "arrowstyle": arrowstyle,
            "color": color,
            "linewidth": linewidth,
        }
        if self.coord == "npc":
            patch_kwargs["transform"] = ax.transAxes
        patch = FancyArrowPatch(
            posA=(self.x, self.y),
            posB=(self.xend, self.yend),
            **patch_kwargs,
        )
        ax.add_patch(patch)


@dataclass(frozen=True, slots=True)
class _GeomAnnotBracket:
    """Internal geom for annotate("bracket")."""

    xmin: float
    xmax: float
    y: float
    label: str | None = None
    coord: str = "data"
    kwargs: dict[str, Any] = field(default_factory=dict)

    required_aes: ClassVar[frozenset[str]] = frozenset()
    supports_group_splitting: ClassVar[bool] = False
    legend_key: ClassVar[str] = "rect"
    known_params: ClassVar[frozenset[str]] = frozenset()

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = self.kwargs.get("color", params.get("color", "black"))
        linewidth = self.kwargs.get("size", params.get("size", 1))
        direction = self.kwargs.get("direction", "up")
        tip_length = self.kwargs.get("tip_length", 0.02)

        transform = ax.transAxes if self.coord == "npc" else ax.transData

        if self.coord == "npc":
            # In NPC mode, tip_length is already in axes fraction
            tip = tip_length * (1 if direction == "up" else -1)
        else:
            # Get axis range for tip_length scaling
            ylo, yhi = ax.get_ylim()
            tip = tip_length * (yhi - ylo) * (1 if direction == "up" else -1)

        # Vertical ticks + horizontal bar
        ax.plot(
            [self.xmin, self.xmin, self.xmax, self.xmax],
            [self.y, self.y + tip, self.y + tip, self.y],
            color=color,
            linewidth=linewidth,
            clip_on=False,
            transform=transform,
        )

        # Optional label centered above/below
        if self.label:
            label_y = self.y + tip * 1.5
            va = "bottom" if direction == "up" else "top"
            ax.text(
                (self.xmin + self.xmax) / 2,
                label_y,
                self.label,
                ha="center",
                va=va,
                color=color,
                fontsize=params.get("fontsize", 10),
                transform=transform,
            )


def annotate(
    geom_type: str | AnnotationType,
    x: float | None = None,
    y: float | None = None,
    xmin: float | None = None,
    xmax: float | None = None,
    ymin: float | None = None,
    ymax: float | None = None,
    label: str | None = None,
    coord: str = "data",
    **params: Any,
) -> Layer:
    """Create an annotation layer.

    Parameters
    ----------
    geom_type : str or AnnotationType
        Annotation type: ``AnnotationType.TEXT``, ``AnnotationType.RECT``,
        ``AnnotationType.SEGMENT``, ``AnnotationType.CURVE``, or
        ``AnnotationType.BRACKET``. Plain strings are also accepted.
    x, y : float, optional
        Position coordinates.
    xmin, xmax, ymin, ymax : float, optional
        Boundary coordinates for ``"rect"`` and ``"bracket"`` types.
    label : str, optional
        Text label for ``"text"`` and ``"bracket"`` types.
    coord : str, optional
        Coordinate system: ``"data"`` (default) uses data coordinates,
        ``"npc"`` uses Normalized Panel Coordinates where (0, 0) is the
        bottom-left and (1, 1) is the top-right of the panel.
    **params
        Additional visual properties passed to the underlying geom.

    Raises
    ------
    ConfigError
        If *geom_type* is not a recognized annotation type.

    Examples
    --------
    >>> from plotten import annotate
    >>> annotate("text", x=0.5, y=0.95, label="Top center", coord="npc")
    Layer(...)
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

            if coord == "npc":
                params["_transform"] = "axes"

            from plotten._defaults import detect_backend

            inline_data = nw.from_dict(
                {"x": [x], "y": [y], "label": [label]}, backend=detect_backend()
            )
            return Layer(
                geom=GeomText(), mapping=Aes(), params=params, data=nw.to_native(inline_data)
            )

        case AnnotationType.RECT:
            geom = _GeomAnnotRect(
                xmin=xmin if xmin is not None else 0,
                xmax=xmax if xmax is not None else 0,
                ymin=ymin if ymin is not None else 0,
                ymax=ymax if ymax is not None else 0,
                coord=coord,
                kwargs=params,
            )
            return Layer(geom=geom, mapping=Aes(), params={})

        case AnnotationType.SEGMENT:
            xend = params.pop("xend", x)
            yend = params.pop("yend", y)
            geom = _GeomAnnotSegment(
                x=x if x is not None else 0,
                y=y if y is not None else 0,
                xend=xend if xend is not None else 0,
                yend=yend if yend is not None else 0,
                coord=coord,
                kwargs=params,
            )
            return Layer(geom=geom, mapping=Aes(), params={})

        case AnnotationType.CURVE:
            xend = params.pop("xend", x)
            yend = params.pop("yend", y)
            geom = _GeomAnnotCurve(
                x=x if x is not None else 0,
                y=y if y is not None else 0,
                xend=xend if xend is not None else 0,
                yend=yend if yend is not None else 0,
                coord=coord,
                kwargs=params,
            )
            return Layer(geom=geom, mapping=Aes(), params={})

        case AnnotationType.BRACKET:
            geom_b = _GeomAnnotBracket(
                xmin=xmin if xmin is not None else 0,
                xmax=xmax if xmax is not None else 0,
                y=y if y is not None else 0,
                label=label,
                coord=coord,
                kwargs=params,
            )
            return Layer(geom=geom_b, mapping=Aes(), params={})

        case _:
            from plotten._validation import ConfigError

            msg = (
                f"Unknown annotation geom_type: {geom_type!r}. "
                f"Valid types: 'text', 'rect', 'segment', 'curve', 'bracket'."
            )
            raise ConfigError(msg)
