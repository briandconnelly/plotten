from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedContinuousScale, MappedDiscreteScale


class ScaleLinewidthContinuous(MappedContinuousScale):
    """Map numeric values to line widths."""

    def __init__(
        self,
        aesthetic: str = "linewidth",
        range: tuple[float, float] = (0.5, 3.0),
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._range = range
        self._breaks = breaks
        self._limits = limits

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        slo, shi = self._range
        return [slo + (v - lo) / span * (shi - slo) for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        breaks = self.get_breaks()
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        slo, shi = self._range
        entries = []
        for b in breaks:
            lw = slo + (b - lo) / span * (shi - slo)
            entries.append(LegendEntry(label=f"{b:.3g}", linewidth=lw))
        return entries


class ScaleLinewidthDiscrete(MappedDiscreteScale):
    """Map categories to line widths."""

    def __init__(
        self,
        aesthetic: str = "linewidth",
        values: dict[str, float] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._levels: list = []
        self._manual_values = values

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        if self._manual_values:
            return [self._manual_values.get(str(v), 1.0) for v in s.to_list()]
        n = max(len(self._levels), 1)
        lw_map = {lev: 0.5 + 2.5 * i / max(n - 1, 1) for i, lev in enumerate(self._levels)}
        return [lw_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        entries = []
        n = max(len(self._levels), 1)
        for i, lev in enumerate(self._levels):
            if self._manual_values:
                lw = self._manual_values.get(str(lev), 1.0)
            else:
                lw = 0.5 + 2.5 * i / max(n - 1, 1)
            entries.append(LegendEntry(label=str(lev), linewidth=lw))
        return entries


def scale_linewidth_continuous(**kwargs: Any) -> ScaleLinewidthContinuous:
    """Map continuous values to line widths.

    Parameters
    ----------
    range : tuple of float, optional
        Output linewidth range as ``(min, max)`` (default ``(0.5, 3.0)``).
    breaks : list of float, optional
        Explicit break values for the legend.
    limits : tuple of float, optional
        Fixed ``(min, max)`` domain limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_line, scale_linewidth_continuous
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", linewidth="v")) + geom_line() + scale_linewidth_continuous()
    Plot(...)
    """
    return ScaleLinewidthContinuous(**kwargs)


def scale_linewidth_discrete(**kwargs: Any) -> ScaleLinewidthDiscrete:
    """Map discrete values to evenly spaced line widths.

    Parameters
    ----------
    values : dict of str to float, optional
        Manual mapping from category names to line widths.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_line, scale_linewidth_discrete
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", linewidth="g")) + geom_line() + scale_linewidth_discrete()
    Plot(...)
    """
    return ScaleLinewidthDiscrete(**kwargs)


def scale_linewidth_manual(values: dict[str, float]) -> ScaleLinewidthDiscrete:
    """Map discrete values to manually specified line widths.

    Parameters
    ----------
    values : dict of str to float
        Mapping from category names to line widths.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_line, scale_linewidth_manual
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", linewidth="g")) + geom_line() + scale_linewidth_manual({"a": 0.5, "b": 1.5, "c": 3.0})
    Plot(...)
    """
    return ScaleLinewidthDiscrete(values=values)
