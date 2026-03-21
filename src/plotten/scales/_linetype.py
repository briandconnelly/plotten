from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten._linetypes import resolve_linetype
from plotten.scales._base import LegendEntry, MappedDiscreteScale

DEFAULT_LINETYPES = ["solid", "dashed", "dotted", "dashdot"]


class ScaleLinetypeDiscrete(MappedDiscreteScale):
    """Map categories to matplotlib linestyle strings."""

    __slots__ = ("_manual_values",)

    def __init__(
        self,
        aesthetic: str = "linetype",
        values: dict[str, str] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._levels: list = []
        self._manual_values = values

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        if self._manual_values:
            return [
                resolve_linetype(self._manual_values.get(str(v), "solid")) for v in s.to_list()
            ]
        lt_map = {
            lev: DEFAULT_LINETYPES[i % len(DEFAULT_LINETYPES)]
            for i, lev in enumerate(self._levels)
        }
        return [lt_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        entries = []
        for i, lev in enumerate(self._levels):
            if self._manual_values:
                lt = resolve_linetype(self._manual_values.get(str(lev), "solid"))
            else:
                lt = DEFAULT_LINETYPES[i % len(DEFAULT_LINETYPES)]
            entries.append(LegendEntry(label=str(lev), linetype=lt))
        return entries


def scale_linetype_discrete(**kwargs: Any) -> ScaleLinetypeDiscrete:
    """Map discrete values to matplotlib linestyle strings.

    Parameters
    ----------
    values : dict of str to str, optional
        Manual mapping from category names to linestyle strings.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_line, scale_linetype_discrete
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "a", "a"]})
    >>> ggplot(df, aes(x="x", y="y", linetype="g")) + geom_line() + scale_linetype_discrete()
    Plot(...)
    """
    return ScaleLinetypeDiscrete(**kwargs)


def scale_linetype_manual(values: dict[str, str]) -> ScaleLinetypeDiscrete:
    """Map discrete values to manually specified linestyle strings.

    Parameters
    ----------
    values : dict of str to str
        Mapping from category names to matplotlib linestyle strings
        (e.g. ``"solid"``, ``"dashed"``, ``"dotted"``, ``"dashdot"``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_line, scale_linetype_manual
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9], "g": ["a", "a", "a"]})
    >>> ggplot(df, aes(x="x", y="y", linetype="g")) + geom_line() + scale_linetype_manual({"a": "dashed"})
    Plot(...)
    """
    return ScaleLinetypeDiscrete(values=values)
