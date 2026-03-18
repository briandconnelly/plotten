from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, ScaleBase

DEFAULT_SHAPES = ["o", "s", "^", "D", "v", "p", "h", "*", "X", "P"]


class ScaleShapeDiscrete(ScaleBase):
    """Map categories to matplotlib marker strings."""

    def __init__(
        self,
        aesthetic: str = "shape",
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
            return [self._manual_values.get(str(v), "o") for v in s.to_list()]
        shape_map = {
            lev: DEFAULT_SHAPES[i % len(DEFAULT_SHAPES)]
            for i, lev in enumerate(self._levels)
        }
        return [shape_map[v] for v in s.to_list()]

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
                shape = self._manual_values.get(str(lev), "o")
            else:
                shape = DEFAULT_SHAPES[i % len(DEFAULT_SHAPES)]
            entries.append(LegendEntry(label=str(lev), shape=shape))
        return entries


def scale_shape_discrete(**kwargs: Any) -> ScaleShapeDiscrete:
    return ScaleShapeDiscrete(**kwargs)


def scale_shape_manual(values: dict[str, str]) -> ScaleShapeDiscrete:
    return ScaleShapeDiscrete(values=values)
