from __future__ import annotations

from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, ScaleBase


class ScaleSizeContinuous(ScaleBase):
    """Map numeric values to point sizes."""

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
        self._domain_min: float | None = None
        self._domain_max: float | None = None

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        vmin = s.min()
        vmax = s.max()
        if self._domain_min is None or vmin < self._domain_min:
            self._domain_min = vmin
        if self._domain_max is None or vmax > self._domain_max:
            self._domain_max = vmax

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        slo, shi = self._range
        return [slo + (v - lo) / span * (shi - slo) for v in s.to_list()]

    def get_limits(self) -> tuple[float, float]:
        if self._limits is not None:
            return self._limits
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        return (lo, hi)

    def get_breaks(self) -> list:
        if self._breaks is not None:
            return list(self._breaks)
        import numpy as np

        lo, hi = self.get_limits()
        return np.linspace(lo, hi, 5).tolist()

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


class ScaleSizeDiscrete(ScaleBase):
    """Map categories to sizes."""

    def __init__(
        self,
        aesthetic: str = "size",
        values: dict[str, float] | None = None,
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
            return [self._manual_values.get(str(v), 5.0) for v in s.to_list()]
        n = max(len(self._levels), 1)
        size_map = {lev: 1 + 9 * i / max(n - 1, 1) for i, lev in enumerate(self._levels)}
        return [size_map[v] for v in s.to_list()]

    def get_limits(self) -> tuple[float, float]:
        return (0, len(self._levels))

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        return [str(lev) for lev in self._levels]

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
    return ScaleSizeContinuous(**kwargs)


def scale_size_discrete(**kwargs: Any) -> ScaleSizeDiscrete:
    return ScaleSizeDiscrete(**kwargs)


def scale_size_manual(values: dict[str, float]) -> ScaleSizeDiscrete:
    return ScaleSizeDiscrete(values=values)
