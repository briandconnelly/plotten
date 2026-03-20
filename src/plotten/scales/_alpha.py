from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedContinuousScale, MappedDiscreteScale


class ScaleAlphaContinuous(MappedContinuousScale):
    """Map numeric values to alpha transparency."""

    def __init__(
        self,
        aesthetic: str = "alpha",
        range: tuple[float, float] = (0.1, 1.0),
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
        alo, ahi = self._range
        return [alo + (v - lo) / span * (ahi - alo) for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        breaks = self.get_breaks()
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        alo, ahi = self._range
        entries = []
        for b in breaks:
            alpha = alo + (b - lo) / span * (ahi - alo)
            entries.append(LegendEntry(label=f"{b:.3g}", alpha=alpha))
        return entries


class ScaleAlphaDiscrete(MappedDiscreteScale):
    """Map categories to fixed alpha values."""

    def __init__(
        self,
        aesthetic: str = "alpha",
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
        alpha_map = {lev: 0.1 + 0.9 * i / max(n - 1, 1) for i, lev in enumerate(self._levels)}
        return [alpha_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        entries = []
        n = max(len(self._levels), 1)
        for i, lev in enumerate(self._levels):
            if self._manual_values:
                alpha = self._manual_values.get(str(lev), 1.0)
            else:
                alpha = 0.1 + 0.9 * i / max(n - 1, 1)
            entries.append(LegendEntry(label=str(lev), alpha=alpha))
        return entries


def scale_alpha_continuous(**kwargs: Any) -> ScaleAlphaContinuous:
    """Map continuous values to alpha transparency levels.

    Parameters
    ----------
    range : tuple of float, optional
        Output alpha range as ``(min, max)`` (default ``(0.1, 1.0)``).
    breaks : list of float, optional
        Explicit break values for the legend.
    limits : tuple of float, optional
        Fixed ``(min, max)`` domain limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_alpha_continuous
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", alpha="v")) + geom_point() + scale_alpha_continuous()
    Plot(...)
    """
    return ScaleAlphaContinuous(**kwargs)


def scale_alpha_discrete(**kwargs: Any) -> ScaleAlphaDiscrete:
    """Map discrete values to evenly spaced alpha transparency levels.

    Parameters
    ----------
    values : dict of str to float, optional
        Manual mapping from category names to alpha values.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_alpha_discrete
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", alpha="g")) + geom_point() + scale_alpha_discrete()
    Plot(...)
    """
    return ScaleAlphaDiscrete(**kwargs)


def scale_alpha_manual(values: dict[str, float]) -> ScaleAlphaDiscrete:
    """Map discrete values to manually specified alpha transparency levels.

    Parameters
    ----------
    values : dict of str to float
        Mapping from category names to alpha values (0-1).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_alpha_manual
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", alpha="g")) + geom_point() + scale_alpha_manual({"a": 0.2, "b": 0.6, "c": 1.0})
    Plot(...)
    """
    return ScaleAlphaDiscrete(values=values)
