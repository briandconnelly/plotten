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
    return ScaleAlphaContinuous(**kwargs)


def scale_alpha_discrete(**kwargs: Any) -> ScaleAlphaDiscrete:
    return ScaleAlphaDiscrete(**kwargs)


def scale_alpha_manual(values: dict[str, float]) -> ScaleAlphaDiscrete:
    return ScaleAlphaDiscrete(values=values)
