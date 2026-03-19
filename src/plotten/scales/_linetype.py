from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedDiscreteScale

DEFAULT_LINETYPES = ["solid", "dashed", "dotted", "dashdot"]


class ScaleLinetypeDiscrete(MappedDiscreteScale):
    """Map categories to matplotlib linestyle strings."""

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
            return [self._manual_values.get(str(v), "solid") for v in s.to_list()]
        lt_map = {
            lev: DEFAULT_LINETYPES[i % len(DEFAULT_LINETYPES)]
            for i, lev in enumerate(self._levels)
        }
        return [lt_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        entries = []
        for i, lev in enumerate(self._levels):
            if self._manual_values:
                lt = self._manual_values.get(str(lev), "solid")
            else:
                lt = DEFAULT_LINETYPES[i % len(DEFAULT_LINETYPES)]
            entries.append(LegendEntry(label=str(lev), linetype=lt))
        return entries


def scale_linetype_discrete(**kwargs: Any) -> ScaleLinetypeDiscrete:
    return ScaleLinetypeDiscrete(**kwargs)


def scale_linetype_manual(values: dict[str, str]) -> ScaleLinetypeDiscrete:
    return ScaleLinetypeDiscrete(values=values)
