from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import narwhals as nw
    import narwhals.typing


class StatDensity2d:
    """Compute 2D kernel density estimation."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(self, n: int = 100) -> None:
        self._n = n

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        import narwhals as nw
        import numpy as np
        from scipy.stats import gaussian_kde

        frame = cast("nw.DataFrame", nw.from_native(df))
        x = frame.get_column("x").to_numpy().astype(float)
        y = frame.get_column("y").to_numpy().astype(float)

        kde = gaussian_kde(np.vstack([x, y]))

        xi = np.linspace(x.min(), x.max(), self._n)
        yi = np.linspace(y.min(), y.max(), self._n)
        xx, yy = np.meshgrid(xi, yi)
        zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)

        result = {
            "x": xx.ravel().tolist(),
            "y": yy.ravel().tolist(),
            "z": zz.ravel().tolist(),
        }
        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
