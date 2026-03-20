from __future__ import annotations

from typing import Any

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
        import matplotlib.dates as mdates

        s = nw.from_native(values, series_only=True)
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
            import matplotlib.dates as mdates

            return (mdates.date2num(self._limits[0]), mdates.date2num(self._limits[1]))
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        return (lo, hi)

    def get_breaks(self) -> list:
        import numpy as np

        lo, hi = self.get_limits()
        return np.linspace(lo, hi, 6).tolist()


def scale_x_date(**kwargs: Any) -> ScaleDateContinuous:
    """Set x-axis to a date scale for date-valued data.

    Parameters
    ----------
    date_breaks : str, optional
        Break interval specification (e.g. ``"1 month"``).
    date_labels : str, optional
        strftime format string for tick labels.
    limits : tuple, optional
        Fixed ``(min, max)`` date limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_x_date
    >>> df = pd.DataFrame({"x": pd.to_datetime(["2024-01-01", "2024-06-01"]), "y": [1, 2]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_date()
    Plot(...)
    """
    return ScaleDateContinuous(aesthetic="x", **kwargs)


def scale_y_date(**kwargs: Any) -> ScaleDateContinuous:
    """Set y-axis to a date scale for date-valued data.

    Parameters
    ----------
    date_breaks : str, optional
        Break interval specification (e.g. ``"1 month"``).
    date_labels : str, optional
        strftime format string for tick labels.
    limits : tuple, optional
        Fixed ``(min, max)`` date limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_y_date
    >>> df = pd.DataFrame({"x": [1, 2], "y": pd.to_datetime(["2024-01-01", "2024-06-01"])})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_date()
    Plot(...)
    """
    return ScaleDateContinuous(aesthetic="y", **kwargs)


def scale_x_datetime(**kwargs: Any) -> ScaleDateContinuous:
    """Set x-axis to a datetime scale for datetime-valued data.

    Parameters
    ----------
    date_breaks : str, optional
        Break interval specification (e.g. ``"6 hours"``).
    date_labels : str, optional
        strftime format string for tick labels.
    limits : tuple, optional
        Fixed ``(min, max)`` datetime limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_x_datetime
    >>> df = pd.DataFrame({"x": pd.to_datetime(["2024-01-01 08:00", "2024-01-01 16:00"]), "y": [1, 2]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_datetime()
    Plot(...)
    """
    return ScaleDateContinuous(aesthetic="x", **kwargs)


def scale_y_datetime(**kwargs: Any) -> ScaleDateContinuous:
    """Set y-axis to a datetime scale for datetime-valued data.

    Parameters
    ----------
    date_breaks : str, optional
        Break interval specification (e.g. ``"6 hours"``).
    date_labels : str, optional
        strftime format string for tick labels.
    limits : tuple, optional
        Fixed ``(min, max)`` datetime limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_y_datetime
    >>> df = pd.DataFrame({"x": [1, 2], "y": pd.to_datetime(["2024-01-01 08:00", "2024-01-01 16:00"])})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_datetime()
    Plot(...)
    """
    return ScaleDateContinuous(aesthetic="y", **kwargs)
