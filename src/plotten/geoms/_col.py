from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomCol:
    """Draw bars with pre-computed heights (uses StatIdentity)."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "fill" in data:
            kwargs["color"] = data["fill"]
        elif "color" in data and isinstance(data["color"], str):
            kwargs["color"] = data["color"]
        if "alpha" in params:
            kwargs["alpha"] = params["alpha"]
        width = params.get("width", 0.8)
        ax.bar(data["x"], data["y"], width=width, **kwargs)
