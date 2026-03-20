from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import scalar


class GeomStep:
    """Draw step lines using ax.step."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = True
    known_params: frozenset[str] = frozenset(
        {"color", "alpha", "linetype", "linewidth", "direction", "size"}
    )

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        kwargs: dict[str, Any] = {}

        where = params.get("direction", "mid")
        kwargs["where"] = where

        if "color" in data:
            color = data["color"]
            kwargs["color"] = scalar(color) if isinstance(color, list) else color
        elif "color" in params:
            kwargs["color"] = params["color"]

        if "alpha" in data:
            alpha = data["alpha"]
            kwargs["alpha"] = scalar(alpha) if isinstance(alpha, list) else alpha
        elif "alpha" in params:
            kwargs["alpha"] = params["alpha"]

        if "linetype" in data:
            lt = data["linetype"]
            kwargs["linestyle"] = scalar(lt) if isinstance(lt, list) else lt
        elif "linetype" in params:
            kwargs["linestyle"] = params["linetype"]

        if "linewidth" in data:
            lw = data["linewidth"]
            kwargs["linewidth"] = scalar(lw) if isinstance(lw, list) else lw
        elif "linewidth" in params:
            kwargs["linewidth"] = params["linewidth"]
        elif "size" in data:
            size = data["size"]
            kwargs["linewidth"] = scalar(size) if isinstance(size, list) else size
        elif "size" in params:
            kwargs["linewidth"] = params["size"]

        ax.step(data["x"], data["y"], **kwargs)
