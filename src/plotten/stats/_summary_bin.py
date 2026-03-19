"""StatSummaryBin — bin continuous x, then summarize y within each bin."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import narwhals as nw
import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable


class StatSummaryBin:
    """Bin continuous x and compute summary statistics of y per bin."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        bins: int = 30,
        fun_y: str | Callable = "mean",
        fun_ymin: str | Callable = "mean_se_lower",
        fun_ymax: str | Callable = "mean_se_upper",
    ) -> None:
        from plotten.stats._summary import _resolve_fun

        self.bins = bins
        self._fun_y = _resolve_fun(fun_y)
        self._fun_ymin = _resolve_fun(fun_ymin)
        self._fun_ymax = _resolve_fun(fun_ymax)

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_values = frame.get_column("x").to_list()
        y_values = frame.get_column("y").to_list()

        xmin, xmax = min(x_values), max(x_values)
        edges = np.linspace(xmin, xmax, self.bins + 1)
        centers = ((edges[:-1] + edges[1:]) / 2).tolist()

        # Assign y values to bins
        bin_ys: dict[int, list[float]] = {}
        for xv, yv in zip(x_values, y_values, strict=True):
            bin_idx = int(np.searchsorted(edges[1:], xv, side="right"))
            bin_idx = min(bin_idx, len(centers) - 1)
            bin_ys.setdefault(bin_idx, []).append(float(yv))

        result: dict[str, list] = {"x": [], "y": [], "ymin": [], "ymax": []}
        for idx in range(len(centers)):
            vals = bin_ys.get(idx)
            if not vals:
                continue
            arr = np.array(vals)
            result["x"].append(centers[idx])
            result["y"].append(self._fun_y(arr))
            result["ymin"].append(self._fun_ymin(arr))
            result["ymax"].append(self._fun_ymax(arr))

        native = nw.to_native(frame)
        if "polars" in str(type(native)):
            import polars as pl

            return pl.DataFrame(result)
        else:
            import pandas as pd

            return pd.DataFrame(result)
