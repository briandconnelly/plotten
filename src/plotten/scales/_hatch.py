from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedDiscreteScale

DEFAULT_HATCH_CYCLE = ["/", "\\", "|", "-", "+", "x", "o", ".", "*"]


class ScaleHatchDiscrete(MappedDiscreteScale):
    """Map categories to hatch patterns."""

    __slots__ = ("_manual_values",)

    def __init__(
        self,
        aesthetic: str = "hatch",
        values: dict[str, str] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._levels: list = []
        self._manual_values = values

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        if self._manual_values:
            return [self._manual_values.get(str(v), "/") for v in s.to_list()]
        return [
            DEFAULT_HATCH_CYCLE[self._levels.index(v) % len(DEFAULT_HATCH_CYCLE)]
            for v in s.to_list()
        ]

    def legend_entries(self) -> list[LegendEntry]:
        entries = []
        for i, lev in enumerate(self._levels):
            if self._manual_values:
                h = self._manual_values.get(str(lev), "/")
            else:
                h = DEFAULT_HATCH_CYCLE[i % len(DEFAULT_HATCH_CYCLE)]
            entries.append(LegendEntry(label=str(lev), hatch=h))
        return entries


def scale_hatch_discrete(**kwargs: Any) -> ScaleHatchDiscrete:
    """Map discrete values to hatch patterns.

    Parameters
    ----------
    values : dict of str to str, optional
        Manual mapping from category names to hatch patterns.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_hatch_discrete
    >>> df = pd.DataFrame({"x": ["a", "b", "c"], "y": [1, 2, 3]})
    >>> ggplot(df, aes(x="x", y="y", hatch="x")) + geom_bar() + scale_hatch_discrete()
    Plot(...)
    """
    return ScaleHatchDiscrete(**kwargs)


def scale_hatch_manual(values: dict[str, str]) -> ScaleHatchDiscrete:
    """Map discrete values to manually specified hatch patterns.

    Parameters
    ----------
    values : dict of str to str
        Mapping from category names to matplotlib hatch patterns
        (e.g. ``"/"``, ``"\\\\"``, ``"|"``, ``"-"``, ``"+"``, ``"x"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar, scale_hatch_manual
    >>> df = pd.DataFrame({"x": ["a", "b"], "y": [1, 2]})
    >>> ggplot(df, aes(x="x", y="y", hatch="x")) + geom_bar() + scale_hatch_manual({"a": "//", "b": "xx"})
    Plot(...)
    """
    return ScaleHatchDiscrete(values=values)
