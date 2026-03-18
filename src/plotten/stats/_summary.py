from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

import narwhals as nw
import numpy as np

_BUILTIN_FUNS: dict[str, Callable[[np.ndarray], float]] = {
    "mean": lambda v: float(np.mean(v)),
    "median": lambda v: float(np.median(v)),
    "min": lambda v: float(np.min(v)),
    "max": lambda v: float(np.max(v)),
    "mean_se_lower": lambda v: float(np.mean(v) - np.std(v, ddof=1) / np.sqrt(len(v))),
    "mean_se_upper": lambda v: float(np.mean(v) + np.std(v, ddof=1) / np.sqrt(len(v))),
    "mean_sd_lower": lambda v: float(np.mean(v) - np.std(v, ddof=1)),
    "mean_sd_upper": lambda v: float(np.mean(v) + np.std(v, ddof=1)),
}


def _resolve_fun(fun: str | Callable[[np.ndarray], float]) -> Callable[[np.ndarray], float]:
    if callable(fun):
        return fun
    if fun in _BUILTIN_FUNS:
        return _BUILTIN_FUNS[fun]
    msg = f"Unknown summary function: {fun!r}"
    raise ValueError(msg)


class StatSummary:
    """Compute grouped summary statistics (y, ymin, ymax) per x level."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        fun_y: str | Callable = "mean",
        fun_ymin: str | Callable = "mean_se_lower",
        fun_ymax: str | Callable = "mean_se_upper",
    ) -> None:
        self._fun_y = _resolve_fun(fun_y)
        self._fun_ymin = _resolve_fun(fun_ymin)
        self._fun_ymax = _resolve_fun(fun_ymax)

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_vals = frame.get_column("x").to_list()
        y_vals = frame.get_column("y").to_list()

        groups: dict[Any, list[float]] = {}
        for xv, yv in zip(x_vals, y_vals, strict=True):
            groups.setdefault(xv, []).append(float(yv))

        result: dict[str, list] = {"x": [], "y": [], "ymin": [], "ymax": []}

        for x_key in sorted(groups):
            vals = np.array(groups[x_key])
            result["x"].append(x_key)
            result["y"].append(self._fun_y(vals))
            result["ymin"].append(self._fun_ymin(vals))
            result["ymax"].append(self._fun_ymax(vals))

        if "polars" in str(type(df)):
            import polars as pl

            return pl.DataFrame(result)
        else:
            import pandas as pd

            return pd.DataFrame(result)
