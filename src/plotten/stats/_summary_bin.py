"""StatSummaryBin — bin continuous x, then summarize y within each bin."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import narwhals as nw
import narwhals.typing
import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable


class StatSummaryBin:
    """Bin continuous x and compute summary statistics of y per bin."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        bins: int = 30,
        center: str | Callable = "mean",
        lower: str | Callable = "mean_se_lower",
        upper: str | Callable = "mean_se_upper",
        # Deprecated aliases
        fun_y: str | Callable | None = None,
        fun_ymin: str | Callable | None = None,
        fun_ymax: str | Callable | None = None,
    ) -> None:
        from plotten.stats._summary import _resolve_fun

        if fun_y is not None:
            center = fun_y
        if fun_ymin is not None:
            lower = fun_ymin
        if fun_ymax is not None:
            upper = fun_ymax
        self.bins = bins
        self._fun_y = _resolve_fun(center)
        self._fun_ymin = _resolve_fun(lower)
        self._fun_ymax = _resolve_fun(upper)

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))

        # Extract as numpy arrays via narwhals Series
        x_arr = frame.get_column("x").to_numpy()
        y_arr = frame.get_column("y").to_numpy()

        x_arr = np.asarray(x_arr, dtype=float)
        y_arr = np.asarray(y_arr, dtype=float)

        edges = np.linspace(x_arr.min(), x_arr.max(), self.bins + 1)
        centers = (edges[:-1] + edges[1:]) / 2

        # Assign each observation to a bin
        bin_indices = np.searchsorted(edges[1:], x_arr, side="right")
        bin_indices = np.clip(bin_indices, 0, len(centers) - 1)

        result: dict[str, list] = {"x": [], "y": [], "ymin": [], "ymax": []}
        for idx in range(len(centers)):
            mask = bin_indices == idx
            if not mask.any():
                continue
            vals = y_arr[mask]
            result["x"].append(float(centers[idx]))
            result["y"].append(self._fun_y(vals))
            result["ymin"].append(self._fun_ymin(vals))
            result["ymax"].append(self._fun_ymax(vals))

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
