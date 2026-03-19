from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomText:
    """Draw text at each point."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        fontsize = params.get("size", 10)
        ha = params.get("ha", "center")
        va = params.get("va", "center")
        bbox = params.get("bbox")

        kwargs: dict[str, Any] = {"color": color, "fontsize": fontsize, "ha": ha, "va": va}
        if bbox is not None:
            kwargs["bbox"] = bbox
        if params.get("family") is not None:
            kwargs["fontfamily"] = params["family"]
        if params.get("weight") is not None:
            kwargs["fontweight"] = params["weight"]
        if params.get("style") is not None:
            kwargs["fontstyle"] = params["style"]

        for x, y, label in zip(data["x"], data["y"], data["label"], strict=True):
            ax.text(x, y, str(label), **kwargs)


class GeomLabel:
    """Draw text with a background box at each point."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        color = params.get("color", "black")
        fontsize = params.get("size", 10)
        ha = params.get("ha", "center")
        va = params.get("va", "center")
        bg_color = params.get("fill", "white")
        alpha = params.get("alpha", 0.8)

        bbox = dict(
            boxstyle="round,pad=0.3",
            facecolor=bg_color,
            alpha=alpha,
            edgecolor=color,
        )

        extra: dict[str, Any] = {}
        if params.get("family") is not None:
            extra["fontfamily"] = params["family"]
        if params.get("weight") is not None:
            extra["fontweight"] = params["weight"]
        if params.get("style") is not None:
            extra["fontstyle"] = params["style"]

        for x, y, label in zip(data["x"], data["y"], data["label"], strict=True):
            ax.text(
                x,
                y,
                str(label),
                color=color,
                fontsize=fontsize,
                ha=ha,
                va=va,
                bbox=bbox,
                **extra,
            )
