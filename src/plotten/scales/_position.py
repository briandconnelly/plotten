from __future__ import annotations

from typing import Any

import narwhals as nw
import numpy as np

from plotten.scales._base import ScaleBase


class ScaleContinuous(ScaleBase):
    """Linear scale for numeric position aesthetics."""

    def __init__(
        self,
        aesthetic: str = "x",
        padding: float = 0.05,
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
        labels: list[str] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._padding = padding
        self._breaks = breaks
        self._limits = limits
        self._labels = labels
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
        return values  # identity — matplotlib handles position mapping

    def get_limits(self) -> tuple[float, float]:
        if self._limits is not None:
            return self._limits
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        span = hi - lo
        pad = span * self._padding if span > 0 else 0.5
        return (lo - pad, hi + pad)

    def get_breaks(self) -> list:
        if self._breaks is not None:
            return list(self._breaks)
        lo, hi = self.get_limits()
        return np.linspace(lo, hi, 6).tolist()

    def get_labels(self) -> list[str]:
        if self._labels is not None:
            return list(self._labels)
        return [str(b) for b in self.get_breaks()]


class ScaleDiscrete(ScaleBase):
    """Scale for categorical position aesthetics."""

    def __init__(
        self,
        aesthetic: str = "x",
        labels: dict[str, str] | list[str] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._levels: list = []
        self._manual_labels = labels

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        new_levels = s.unique().sort().to_list()
        for lev in new_levels:
            if lev not in self._levels:
                self._levels.append(lev)

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        mapping = {lev: i for i, lev in enumerate(self._levels)}
        return [mapping[v] for v in s.to_list()]

    def get_limits(self) -> tuple[float, float]:
        n = len(self._levels)
        return (-0.5, n - 0.5) if n > 0 else (-0.5, 0.5)

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        if self._manual_labels is not None:
            if isinstance(self._manual_labels, dict):
                return [
                    self._manual_labels.get(str(lev), str(lev)) for lev in self._levels
                ]
            return list(self._manual_labels)
        return [str(lev) for lev in self._levels]


def scale_x_continuous(**kwargs: Any) -> ScaleContinuous:
    """Create a continuous x scale."""
    return ScaleContinuous(aesthetic="x", **kwargs)


def scale_y_continuous(**kwargs: Any) -> ScaleContinuous:
    """Create a continuous y scale."""
    return ScaleContinuous(aesthetic="y", **kwargs)


def scale_x_discrete(**kwargs: Any) -> ScaleDiscrete:
    """Create a discrete x scale."""
    return ScaleDiscrete(aesthetic="x", **kwargs)


def scale_y_discrete(**kwargs: Any) -> ScaleDiscrete:
    """Create a discrete y scale."""
    return ScaleDiscrete(aesthetic="y", **kwargs)
