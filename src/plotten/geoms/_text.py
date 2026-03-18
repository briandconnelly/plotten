from __future__ import annotations

from typing import Any

from plotten.geoms._base import GeomBase
from plotten.stats._identity import StatIdentity


class GeomText(GeomBase):
    """Draw text at each point."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    default_stat: type = StatIdentity

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
        color = params.get("color", "black")
        fontsize = params.get("size", 10)
        ha = params.get("ha", "center")
        va = params.get("va", "center")

        for x, y, label in zip(data["x"], data["y"], data["label"]):
            ax.text(x, y, str(label), color=color, fontsize=fontsize, ha=ha, va=va)


class GeomLabel(GeomBase):
    """Draw text with a background box at each point."""

    required_aes: frozenset[str] = frozenset({"x", "y", "label"})
    default_stat: type = StatIdentity

    def draw(self, data: dict[str, Any], ax: Any, params: dict) -> None:
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

        for x, y, label in zip(data["x"], data["y"], data["label"]):
            ax.text(
                x, y, str(label),
                color=color, fontsize=fontsize, ha=ha, va=va, bbox=bbox,
            )
