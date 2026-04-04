"""Greyscale color/fill scales."""

from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedContinuousScale, MappedDiscreteScale


class ScaleGreyDiscrete(MappedDiscreteScale):
    """Map discrete values to shades of grey."""

    __slots__ = ("_end", "_start")

    def __init__(
        self,
        aesthetic: str = "color",
        start: float = 0.2,
        end: float = 0.8,
    ) -> None:
        super().__init__(aesthetic)
        self._start = start
        self._end = end
        self._levels: list = []

    def map_data(self, values: Any) -> list[str]:
        s = nw.from_native(values, series_only=True)
        n = len(self._levels) if self._levels else 1
        if n == 1:
            greys = [self._start]
        else:
            greys = [self._start + i * (self._end - self._start) / (n - 1) for i in range(n)]
        level_map = {
            lev: f"#{int(g * 255):02x}{int(g * 255):02x}{int(g * 255):02x}"
            for lev, g in zip(self._levels, greys, strict=True)
        }
        return [level_map.get(v, "#888888") for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        n = len(self._levels) if self._levels else 1
        if n == 1:
            greys = [self._start]
        else:
            greys = [self._start + i * (self._end - self._start) / (n - 1) for i in range(n)]
        entries = []
        for lev, g in zip(self._levels, greys, strict=True):
            hex_color = f"#{int(g * 255):02x}{int(g * 255):02x}{int(g * 255):02x}"
            entries.append(LegendEntry(label=str(lev), **{self.aesthetic: hex_color}))  # type: ignore[arg-type]
        return entries


class ScaleGreyContinuous(MappedContinuousScale):
    """Map continuous values to shades of grey."""

    __slots__ = ("_end", "_start")

    def __init__(
        self,
        aesthetic: str = "color",
        start: float = 0.2,
        end: float = 0.8,
    ) -> None:
        super().__init__(aesthetic)
        self._start = start
        self._end = end
        self._breaks: list[float] | None = None
        self._limits: tuple[float, float] | None = None

    def map_data(self, values: Any) -> list[str]:
        s = nw.from_native(values, series_only=True)
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        result = []
        for v in s.to_list():
            t = (v - lo) / span
            t = max(0.0, min(1.0, t))
            g = self._start + t * (self._end - self._start)
            result.append(f"#{int(g * 255):02x}{int(g * 255):02x}{int(g * 255):02x}")
        return result

    def legend_entries(self) -> list[LegendEntry]:
        breaks = self.get_breaks()
        labels = self.get_labels()
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        entries = []
        for brk, lab in zip(breaks, labels, strict=True):
            t = (brk - lo) / span
            t = max(0.0, min(1.0, t))
            g = self._start + t * (self._end - self._start)
            hex_color = f"#{int(g * 255):02x}{int(g * 255):02x}{int(g * 255):02x}"
            entries.append(LegendEntry(label=lab, **{self.aesthetic: hex_color}))  # type: ignore[arg-type]
        return entries


def scale_color_gray(
    start: float = 0.2, end: float = 0.8, *, aesthetic: str = "color"
) -> ScaleGreyDiscrete:
    """Map discrete color aesthetic to shades of gray.

    Parameters
    ----------
    start : float, optional
        Gray level for the lightest shade, 0-1 (default ``0.2``).
    end : float, optional
        Gray level for the darkest shade, 0-1 (default ``0.8``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_gray
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "b", "c"]})
    >>> ggplot(df, aes(x="x", y="y", color="g")) + geom_point() + scale_color_gray()
    Plot(...)
    """
    return ScaleGreyDiscrete(aesthetic, start=start, end=end)


def scale_fill_gray(start: float = 0.2, end: float = 0.8) -> ScaleGreyDiscrete:
    """Map discrete fill aesthetic to shades of gray.

    Parameters
    ----------
    start : float, optional
        Gray level for the lightest shade, 0-1 (default ``0.2``).
    end : float, optional
        Gray level for the darkest shade, 0-1 (default ``0.8``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_gray
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y", fill="x")) + geom_bar() + scale_fill_gray()
    Plot(...)
    """
    return ScaleGreyDiscrete("fill", start=start, end=end)


def scale_color_gray_continuous(
    start: float = 0.2, end: float = 0.8, *, aesthetic: str = "color"
) -> ScaleGreyContinuous:
    """Map continuous color aesthetic to shades of gray.

    Parameters
    ----------
    start : float, optional
        Gray level for the low end, 0-1 (default ``0.2``).
    end : float, optional
        Gray level for the high end, 0-1 (default ``0.8``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_color_gray_continuous
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", color="v")) + geom_point() + scale_color_gray_continuous()
    Plot(...)
    """
    return ScaleGreyContinuous(aesthetic, start=start, end=end)


def scale_fill_gray_continuous(start: float = 0.2, end: float = 0.8) -> ScaleGreyContinuous:
    """Map continuous fill aesthetic to shades of gray.

    Parameters
    ----------
    start : float, optional
        Gray level for the low end, 0-1 (default ``0.2``).
    end : float, optional
        Gray level for the high end, 0-1 (default ``0.8``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_fill_gray_continuous
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 4, 9], "v": [10, 20, 30]})
    >>> ggplot(df, aes(x="x", y="y", fill="v")) + geom_bar() + scale_fill_gray_continuous()
    Plot(...)
    """
    return ScaleGreyContinuous("fill", start=start, end=end)


# Aliases (British spelling)
scale_color_grey = scale_color_gray
scale_fill_grey = scale_fill_gray
scale_color_grey_continuous = scale_color_gray_continuous
scale_fill_grey_continuous = scale_fill_gray_continuous
