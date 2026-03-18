from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomLinerange:
    """Draw vertical lines from ymin to ymax."""

    required_aes: frozenset[str] = frozenset({"x", "ymin", "ymax"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        color = params.get("color", "black")
        linewidth = params.get("linewidth", 1)

        ax.vlines(data["x"], data["ymin"], data["ymax"], colors=color, linewidth=linewidth)
