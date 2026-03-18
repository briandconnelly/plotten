from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, ScaleBase

DEFAULT_LINETYPES = ["solid", "dashed", "dotted", "dashdot"]


class ScaleLinetypeDiscrete(ScaleBase):
    """Map categories to matplotlib linestyle strings."""

    def __init__(
        self,
        aesthetic: str = "linetype",
        values: dict[str, str] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._levels: list = []
        self._manual_values = values

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        new_levels = s.unique().sort().to_list()
        for lev in new_levels:
            if lev not in self._levels:
                self._levels.append(lev)

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        if self._manual_values:
            return [self._manual_values.get(str(v), "solid") for v in s.to_list()]
        lt_map = {
            lev: DEFAULT_LINETYPES[i % len(DEFAULT_LINETYPES)]
            for i, lev in enumerate(self._levels)
        }
        return [lt_map[v] for v in s.to_list()]

    def get_limits(self) -> tuple[float, float]:
        return (0, len(self._levels))

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        return [str(lev) for lev in self._levels]

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
