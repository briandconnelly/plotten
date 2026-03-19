from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _scalar(values: list) -> Any:
    """Extract a single value from a uniform-group list."""
    return values[0]


class GeomRibbon:
    """Draw a filled band between ymin and ymax."""

    required_aes: frozenset[str] = frozenset({"x", "ymin", "ymax"})
    supports_group_splitting: bool = True

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "fill" in data:
            fill = data["fill"]
            kwargs["color"] = _scalar(fill) if isinstance(fill, list) else fill
        elif "color" in params:
            kwargs["color"] = params["color"]
        kwargs["alpha"] = params.get("alpha", 0.3)
        ax.fill_between(data["x"], data["ymin"], data["ymax"], **kwargs)
