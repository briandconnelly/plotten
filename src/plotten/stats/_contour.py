from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import narwhals as nw
    import narwhals.typing


class StatContour:
    """Compute contour levels from x, y, z data via grid interpolation."""

    required_aes: frozenset[str] = frozenset({"x", "y", "z"})

    def __init__(self, bins: int = 10) -> None:
        self._bins = bins

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        import narwhals as nw
        import numpy as np

        try:
            from scipy.interpolate import griddata
        except ImportError:
            msg = "geom_contour() requires scipy. Install it with: uv add scipy"
            raise ImportError(msg) from None

        frame = cast("nw.DataFrame", nw.from_native(df))
        x = frame.get_column("x").to_numpy().astype(float)
        y = frame.get_column("y").to_numpy().astype(float)
        z = frame.get_column("z").to_numpy().astype(float)

        n = self._bins * 10
        xi = np.linspace(x.min(), x.max(), n)
        yi = np.linspace(y.min(), y.max(), n)
        xx, yy = np.meshgrid(xi, yi)
        zz = griddata(np.column_stack([x, y]), z, (xx, yy), method="cubic")

        result = {
            "x": xx.ravel().tolist(),
            "y": yy.ravel().tolist(),
            "z": zz.ravel().tolist(),
        }
        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
