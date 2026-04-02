from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import narwhals as nw
import narwhals.typing

if TYPE_CHECKING:
    from collections.abc import Callable

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

FunDataResult = dict[str, float] | tuple[float, float, float]

_BUILTIN_FUN_DATA: dict[str, Callable[[np.ndarray], FunDataResult]] = {
    "median_hilow": lambda v: {
        "y": float(np.median(v)),
        "ymin": float(np.percentile(v, 25)),
        "ymax": float(np.percentile(v, 75)),
    },
    "mean_range": lambda v: {
        "y": float(np.mean(v)),
        "ymin": float(np.min(v)),
        "ymax": float(np.max(v)),
    },
}


def _resolve_fun(fun: str | Callable[[np.ndarray], float]) -> Callable[[np.ndarray], float]:
    if not isinstance(fun, str):
        return fun
    if fun in _BUILTIN_FUNS:
        return _BUILTIN_FUNS[fun]
    from plotten._validation import StatError

    msg = f"Unknown summary function: {fun!r}. Valid functions: {sorted(_BUILTIN_FUNS)}."
    raise StatError(msg)


def _resolve_fun_data(
    fun_data: str | Callable[[np.ndarray], FunDataResult],
) -> Callable[[np.ndarray], FunDataResult]:
    if not isinstance(fun_data, str):
        return fun_data
    if fun_data in _BUILTIN_FUN_DATA:
        return _BUILTIN_FUN_DATA[fun_data]
    from plotten._validation import StatError

    msg = f"Unknown fun_data function: {fun_data!r}. Valid functions: {sorted(_BUILTIN_FUN_DATA)}."
    raise StatError(msg)


def _normalize_fun_data_result(result: FunDataResult) -> tuple[float, float, float]:
    """Convert a fun_data result to (y, ymin, ymax) tuple."""
    if isinstance(result, dict):
        return result["y"], result["ymin"], result["ymax"]
    return result


class StatSummary:
    """Compute grouped summary statistics (y, ymin, ymax) per x level.

    Computed Variables
    ------------------
    y
        Central tendency (default: mean).
    ymin
        Lower error bound (default: mean - SE).
    ymax
        Upper error bound (default: mean + SE).
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        fun_y: str | Callable = "mean",
        fun_ymin: str | Callable = "mean_se_lower",
        fun_ymax: str | Callable = "mean_se_upper",
        fun_data: str | Callable | None = None,
    ) -> None:
        self._fun_data: Callable[[np.ndarray], FunDataResult] | None = None
        if fun_data is not None:
            self._fun_data = _resolve_fun_data(fun_data)
        else:
            self._fun_y = _resolve_fun(fun_y)
            self._fun_ymin = _resolve_fun(fun_ymin)
            self._fun_ymax = _resolve_fun(fun_ymax)

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))

        # Get unique x values sorted via narwhals
        unique_x = frame.select(nw.col("x")).unique().sort("x").get_column("x").to_list()

        result: dict[str, list[Any]] = {"x": [], "y": [], "ymin": [], "ymax": []}

        for x_key in unique_x:
            # Filter group via narwhals expression
            group = frame.filter(nw.col("x") == x_key)
            vals = np.array(group.get_column("y").to_list(), dtype=float)

            result["x"].append(x_key)
            if self._fun_data is not None:
                y, ymin, ymax = _normalize_fun_data_result(self._fun_data(vals))
                result["y"].append(y)
                result["ymin"].append(ymin)
                result["ymax"].append(ymax)
            else:
                result["y"].append(self._fun_y(vals))
                result["ymin"].append(self._fun_ymin(vals))
                result["ymax"].append(self._fun_ymax(vals))

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
