from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _scalar(values: list) -> Any:
    """Extract a single value from a uniform-group list."""
    return values[0]


class GeomStep:
    """Draw step lines using ax.step."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        kwargs: dict[str, Any] = {}

        where = params.get("direction", "mid")
        kwargs["where"] = where

        if "color" in data:
            color = data["color"]
            kwargs["color"] = _scalar(color) if isinstance(color, list) else color
        elif "color" in params:
            kwargs["color"] = params["color"]

        if "alpha" in data:
            alpha = data["alpha"]
            kwargs["alpha"] = _scalar(alpha) if isinstance(alpha, list) else alpha
        elif "alpha" in params:
            kwargs["alpha"] = params["alpha"]

        if "linetype" in data:
            lt = data["linetype"]
            kwargs["linestyle"] = _scalar(lt) if isinstance(lt, list) else lt
        elif "linetype" in params:
            kwargs["linestyle"] = params["linetype"]

        if "size" in data:
            size = data["size"]
            kwargs["linewidth"] = _scalar(size) if isinstance(size, list) else size
        elif "size" in params:
            kwargs["linewidth"] = params["size"]

        ax.step(data["x"], data["y"], **kwargs)
