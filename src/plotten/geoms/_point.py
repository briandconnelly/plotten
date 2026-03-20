from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from plotten._types import GeomDrawData, GeomParams


class GeomPoint:
    """Draw points using ax.scatter."""

    required_aes: frozenset[str] = frozenset({"x", "y"})
    supports_group_splitting: bool = False
    known_params: frozenset[str] = frozenset({"color", "size", "alpha", "shape"})

    def default_stat(self) -> Any:
        from plotten.stats._identity import StatIdentity

        return StatIdentity()

    def draw(self, data: GeomDrawData, ax: Axes, params: GeomParams) -> None:
        xs = data["x"]
        ys = data["y"]

        # Per-point shapes require grouping by shape
        if "shape" in data and isinstance(data["shape"], list):
            shapes = data["shape"]
            unique_shapes = sorted(set(shapes))
            for shape in unique_shapes:
                indices = [i for i, s in enumerate(shapes) if s == shape]
                kwargs: dict[str, Any] = {"marker": shape}
                gx = [xs[i] for i in indices]
                gy = [ys[i] for i in indices]
                if "color" in data:
                    if isinstance(data["color"], list):
                        kwargs["c"] = [data["color"][i] for i in indices]
                    else:
                        kwargs["c"] = data["color"]
                if "size" in data:
                    if isinstance(data["size"], list):
                        kwargs["s"] = [data["size"][i] for i in indices]
                    else:
                        kwargs["s"] = data["size"]
                elif "size" in params:
                    kwargs["s"] = params["size"]
                if "alpha" in data:
                    if isinstance(data["alpha"], list):
                        kwargs["alpha"] = [data["alpha"][i] for i in indices]
                    else:
                        kwargs["alpha"] = data["alpha"]
                elif "alpha" in params:
                    kwargs["alpha"] = params["alpha"]
                ax.scatter(gx, gy, **kwargs)
        else:
            kwargs = {}
            if "color" in data:
                kwargs["c"] = data["color"]
            if "size" in data:
                kwargs["s"] = data["size"]
            elif "size" in params:
                kwargs["s"] = params["size"]
            if "alpha" in data:
                kwargs["alpha"] = data["alpha"]
            elif "alpha" in params:
                kwargs["alpha"] = params["alpha"]
            ax.scatter(xs, ys, **kwargs)
