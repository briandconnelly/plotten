from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedContinuousScale, MappedDiscreteScale


class ScaleSizeContinuous(MappedContinuousScale):
    """Map numeric values to point sizes."""

    __slots__ = ("_range",)

    def __init__(
        self,
        aesthetic: str = "size",
        range: tuple[float, float] = (1, 10),
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
            size = slo + (b - lo) / span * (shi - slo)
            entries.append(LegendEntry(label=f"{b:.3g}", size=size))
        return entries


class ScaleSizeDiscrete(MappedDiscreteScale):
    """Map categories to sizes."""

    __slots__ = ("_manual_values",)

    def __init__(
        self,
        aesthetic: str = "size",
        values: dict[str, float] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._levels: list = []
        self._manual_values = values

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        if self._manual_values:
            return [self._manual_values.get(str(v), 5.0) for v in s.to_list()]
        n = max(len(self._levels), 1)
        size_map = {lev: 1 + 9 * i / max(n - 1, 1) for i, lev in enumerate(self._levels)}
        return [size_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        entries = []
        n = max(len(self._levels), 1)
        for i, lev in enumerate(self._levels):
            if self._manual_values:
                size = self._manual_values.get(str(lev), 5.0)
            else:
                size = 1 + 9 * i / max(n - 1, 1)
            entries.append(LegendEntry(label=str(lev), size=size))
        return entries


def scale_size_continuous(**kwargs: Any) -> ScaleSizeContinuous:
    """Map continuous values to point sizes.

    Parameters
    ----------
    range : tuple of float, optional
        Output size range as ``(min, max)`` (default ``(1, 10)``).
    breaks : list of float, optional
        Explicit break values for the legend.
    limits : tuple of float, optional
        Fixed ``(min, max)`` domain limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_size_continuous
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", size="v")) + geom_point() + scale_size_continuous()
    Plot(...)
    """
    return ScaleSizeContinuous(**kwargs)


def scale_size_discrete(**kwargs: Any) -> ScaleSizeDiscrete:
    """Map discrete values to evenly spaced point sizes.

    Parameters
    ----------
    values : dict of str to float, optional
        Manual mapping from category names to point sizes.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_size_discrete
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", size="g")) + geom_point() + scale_size_discrete()
    Plot(...)
    """
    return ScaleSizeDiscrete(**kwargs)


class ScaleSizeArea(MappedContinuousScale):
    """Map numeric values to point sizes proportional to area.

    Ensures that a value of 0 maps to size 0 (area-proportional scaling).
    """

    __slots__ = ("_max_size",)

    def __init__(
        self,
        aesthetic: str = "size",
        max_size: float = 10,
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._max_size = max_size
        self._breaks = breaks
        self._limits = limits

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        _, hi = self.get_limits()
        domain_max = hi if hi != 0 else 1.0
        return [self._max_size * max(0, v) / domain_max for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        breaks = self.get_breaks()
        _, hi = self.get_limits()
        domain_max = hi if hi != 0 else 1.0
        entries = []
        for b in breaks:
            size = self._max_size * max(0, b) / domain_max
            entries.append(LegendEntry(label=f"{b:.3g}", size=size))
        return entries


class ScaleRadius(MappedContinuousScale):
    """Map numeric values to point sizes proportional to radius (linear).

    Unlike :class:`ScaleSizeArea`, this maps linearly — the radius (not the
    area) is proportional to the data value.
    """

    __slots__ = ("_range",)

    def __init__(
        self,
        aesthetic: str = "size",
        range: tuple[float, float] = (1, 10),
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
            size = slo + (b - lo) / span * (shi - slo)
            entries.append(LegendEntry(label=f"{b:.3g}", size=size))
        return entries


def scale_size_area(max_size: float = 10, **kwargs: Any) -> ScaleSizeArea:
    """Map continuous values to area-proportional point sizes.

    Value 0 always maps to size 0, making this ideal for bubble charts.

    Parameters
    ----------
    max_size : float, optional
        Maximum point size (default 10).
    breaks : list of float, optional
        Explicit break values for the legend.
    limits : tuple of float, optional
        Fixed ``(min, max)`` domain limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_size_area
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [0, 10, 20]})
    >>> ggplot(df, aes(x="x", y="y", size="v")) + geom_point() + scale_size_area(max_size=15)
    Plot(...)
    """
    return ScaleSizeArea(max_size=max_size, **kwargs)


def scale_radius(range: tuple[float, float] = (1, 10), **kwargs: Any) -> ScaleRadius:
    """Map continuous values to radius-proportional point sizes (linear).

    Parameters
    ----------
    range : tuple of float, optional
        Output size range as ``(min, max)`` (default ``(1, 10)``).
    breaks : list of float, optional
        Explicit break values for the legend.
    limits : tuple of float, optional
        Fixed ``(min, max)`` domain limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_radius
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", size="v")) + geom_point() + scale_radius()
    Plot(...)
    """
    return ScaleRadius(range=range, **kwargs)


def scale_size_manual(values: dict[str, float]) -> ScaleSizeDiscrete:
    """Map discrete values to manually specified point sizes.

    Parameters
    ----------
    values : dict of str to float
        Mapping from category names to point sizes.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_size_manual
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", size="g")) + geom_point() + scale_size_manual({"a": 2, "b": 5, "c": 10})
    Plot(...)
    """
    return ScaleSizeDiscrete(values=values)
