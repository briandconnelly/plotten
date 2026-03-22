from __future__ import annotations

from typing import TYPE_CHECKING, Any

from plotten._defaults import DEFAULT_POINT_SIZE
from plotten._shapes import resolve_shape

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams

from plotten.geoms._draw_helpers import extract_per_index


class GeomPoint:
    """Draw points using ax.scatter."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    legend_key: str = "point"
    known_params: frozenset[str] = frozenset({"color", "size", "alpha", "shape"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        xs = data["x"]
        ys = data["y"]

        # Per-point shapes require grouping by shape
        if "shape" in data and isinstance(data["shape"], list):
            shapes = [resolve_shape(s) for s in data["shape"]]
            for shape in sorted(set(shapes)):
                indices = [i for i, s in enumerate(shapes) if s == shape]
                kwargs: dict[str, Any] = {"marker": shape}
                gx = [xs[i] for i in indices]
                gy = [ys[i] for i in indices]
                if "color" in data:
                    kwargs["c"] = extract_per_index(data["color"], indices)
                if "size" in data:
                    kwargs["s"] = extract_per_index(data["size"], indices)
                elif "size" in params:
                    kwargs["s"] = params["size"]
                else:
                    kwargs["s"] = DEFAULT_POINT_SIZE
                if "alpha" in data:
                    kwargs["alpha"] = extract_per_index(data["alpha"], indices)
                elif "alpha" in params:
                    kwargs["alpha"] = params["alpha"]
                ax.scatter(gx, gy, **kwargs)
        else:
            kwargs = {}
            if "shape" in data and isinstance(data["shape"], str):
                kwargs["marker"] = resolve_shape(data["shape"])
            elif "shape" in params:
                kwargs["marker"] = resolve_shape(params["shape"])
            if "color" in data:
                kwargs["c"] = data["color"]
            if "size" in data:
                kwargs["s"] = data["size"]
            elif "size" in params:
                kwargs["s"] = params["size"]
            else:
                kwargs["s"] = DEFAULT_POINT_SIZE
            if "alpha" in data:
                kwargs["alpha"] = data["alpha"]
            elif "alpha" in params:
                kwargs["alpha"] = params["alpha"]
            ax.scatter(xs, ys, **kwargs)
