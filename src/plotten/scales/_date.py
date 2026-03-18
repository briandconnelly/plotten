from __future__ import annotations

from typing import Any

import matplotlib.dates as mdates
import narwhals as nw

from plotten.scales._base import ScaleBase


class ScaleDateContinuous(ScaleBase):
    """Scale for date/datetime axes."""

    def __init__(
        self,
        aesthetic: str = "x",
        date_breaks: str | None = None,
        date_labels: str | None = None,
        limits: tuple | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._date_breaks = date_breaks
        self._date_labels = date_labels
        self._limits = limits
        self._domain_min: float | None = None
        self._domain_max: float | None = None

    def _to_mpl_dates(self, values: Any) -> list[float]:
        """Convert temporal values to matplotlib date numbers."""
        s = nw.from_native(values, series_only=True)
        # Cast to datetime then extract Python objects
        try:
            py_values = s.to_list()
        except Exception:
            py_values = s.to_list()
        return [mdates.date2num(v) for v in py_values]

    def train(self, values: Any) -> None:
        mpl_dates = self._to_mpl_dates(values)
        if not mpl_dates:
            return
        vmin = min(mpl_dates)
        vmax = max(mpl_dates)
        if self._domain_min is None or vmin < self._domain_min:
            self._domain_min = vmin
        if self._domain_max is None or vmax > self._domain_max:
            self._domain_max = vmax

    def map_data(self, values: Any) -> Any:
        return self._to_mpl_dates(values)

    def get_limits(self) -> tuple[float, float]:
        if self._limits is not None:
            return (mdates.date2num(self._limits[0]), mdates.date2num(self._limits[1]))
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        return (lo, hi)

    def get_breaks(self) -> list:
        import numpy as np

        lo, hi = self.get_limits()
        return np.linspace(lo, hi, 6).tolist()


def scale_x_date(**kwargs: Any) -> ScaleDateContinuous:
    return ScaleDateContinuous(aesthetic="x", **kwargs)


def scale_y_date(**kwargs: Any) -> ScaleDateContinuous:
    return ScaleDateContinuous(aesthetic="y", **kwargs)


def scale_x_datetime(**kwargs: Any) -> ScaleDateContinuous:
    return ScaleDateContinuous(aesthetic="x", **kwargs)


def scale_y_datetime(**kwargs: Any) -> ScaleDateContinuous:
    return ScaleDateContinuous(aesthetic="y", **kwargs)
