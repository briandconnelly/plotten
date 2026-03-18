from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


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

        if "color" in data and isinstance(data["color"], str):
            kwargs["color"] = data["color"]
        elif "color" in params:
            kwargs["color"] = params["color"]

        if "alpha" in data and not isinstance(data["alpha"], list):
            kwargs["alpha"] = data["alpha"]
        elif "alpha" in params:
            kwargs["alpha"] = params["alpha"]

        if "linetype" in data:
            if isinstance(data["linetype"], list) and data["linetype"]:
                kwargs["linestyle"] = data["linetype"][0]
            elif isinstance(data["linetype"], str):
                kwargs["linestyle"] = data["linetype"]
        elif "linetype" in params:
            kwargs["linestyle"] = params["linetype"]

        if "size" in data:
            if isinstance(data["size"], list) and data["size"]:
                kwargs["linewidth"] = data["size"][0]
            elif isinstance(data["size"], int | float):
                kwargs["linewidth"] = data["size"]
        elif "size" in params:
            kwargs["linewidth"] = params["size"]

        ax.step(data["x"], data["y"], **kwargs)
