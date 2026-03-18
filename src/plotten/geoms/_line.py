from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class GeomLine:
    """Draw lines using ax.plot."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: dict[str, Any], ax: Axes, params: dict) -> None:
        kwargs: dict[str, Any] = {}
        if "color" in data and isinstance(data["color"], str):
            kwargs["color"] = data["color"]
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
        ax.plot(data["x"], data["y"], **kwargs)
