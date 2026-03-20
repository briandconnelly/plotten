from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import narwhals as nw


@dataclass(frozen=True, slots=True, kw_only=True)
class LegendEntry:
    """A single entry in a legend."""

    label: str
    color: str | None = None
    fill: str | None = None
    size: float | None = None
    alpha: float | None = None
    shape: str | None = None
    linetype: str | None = None
    linewidth: float | None = None
    hatch: str | None = None


class ScaleBase:
    """Base class for all scales."""

    _domain_min: float | None
    _domain_max: float | None

    def __init__(self, aesthetic: str) -> None:
        self.aesthetic = aesthetic
        self._domain_min = None
        self._domain_max = None
        self._cache: dict[str, Any] = {}

    def _invalidate_cache(self) -> None:
        """Clear cached computation results (called after training)."""
        self._cache.clear()

    def train(self, values: Any) -> None:
        raise NotImplementedError

    def map_data(self, values: Any) -> Any:
        raise NotImplementedError

    def get_limits(self) -> tuple[float, float]:
        raise NotImplementedError

    def get_breaks(self) -> list:
        raise NotImplementedError

    def get_labels(self) -> list[str]:
        return [str(b) for b in self.get_breaks()]

    def legend_entries(self) -> list[LegendEntry] | None:
        """Return legend entries for this scale, or None if not applicable."""
        return None


class MappedContinuousScale(ScaleBase):
    """Base class for non-position continuous scales (color, size, alpha).

    Provides shared train/get_limits/get_breaks logic.
    Subclasses must set ``_breaks``, ``_limits`` in their ``__init__``.
    """

    _breaks: list[float] | None
    _limits: tuple[float, float] | None

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        vmin = s.min()
        vmax = s.max()
        if self._domain_min is None or vmin < self._domain_min:
            self._domain_min = vmin
        if self._domain_max is None or vmax > self._domain_max:
            self._domain_max = vmax
        self._invalidate_cache()

    def get_limits(self) -> tuple[float, float]:
        if self._limits is not None:
            return self._limits
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        return (lo, hi)

    def get_breaks(self) -> list:
        cached = self._cache.get("breaks")
        if cached is not None:
            return cached
        lo, hi = self.get_limits()
        if self._breaks is None:
            import numpy as np

            from plotten._defaults import DEFAULT_CONTINUOUS_BREAK_COUNT

            result = np.linspace(lo, hi, DEFAULT_CONTINUOUS_BREAK_COUNT).tolist()
        elif callable(self._breaks):
            result = list(self._breaks((lo, hi)))  # type: ignore[operator]
        else:
            result = list(self._breaks)
        self._cache["breaks"] = result
        return result


class MappedDiscreteScale(ScaleBase):
    """Base class for non-position discrete scales (color, size, alpha, shape, linetype).

    Provides shared train/get_limits/get_breaks/get_labels logic.
    Subclasses must set ``_levels`` in their ``__init__``.
    """

    _levels: list

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        new_levels = s.unique().sort().to_list()
        for lev in new_levels:
            if lev not in self._levels:
                self._levels.append(lev)
        self._invalidate_cache()

    def get_limits(self) -> tuple[float, float]:
        return (0, len(self._levels))

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        cached = self._cache.get("labels")
        if cached is not None:
            return cached
        result = [str(lev) for lev in self._levels]
        self._cache["labels"] = result
        return result


def auto_scale(aesthetic: str, series: Any) -> ScaleBase:
    """Pick the right scale based on narwhals dtype."""
    from plotten.scales._alpha import ScaleAlphaContinuous, ScaleAlphaDiscrete
    from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete
    from plotten.scales._date import ScaleDateContinuous
    from plotten.scales._linetype import ScaleLinetypeDiscrete
    from plotten.scales._position import ScaleContinuous, ScaleDiscrete
    from plotten.scales._shape import ScaleShapeDiscrete
    from plotten.scales._size import ScaleSizeContinuous, ScaleSizeDiscrete

    s = nw.from_native(series, series_only=True)

    match aesthetic:
        case "color" | "fill":
            if s.dtype.is_numeric():
                return ScaleColorContinuous(aesthetic=aesthetic)
            return ScaleColorDiscrete(aesthetic=aesthetic)

        case "size":
            if s.dtype.is_numeric():
                return ScaleSizeContinuous(aesthetic=aesthetic)
            return ScaleSizeDiscrete(aesthetic=aesthetic)

        case "alpha":
            if s.dtype.is_numeric():
                return ScaleAlphaContinuous(aesthetic=aesthetic)
            return ScaleAlphaDiscrete(aesthetic=aesthetic)

        case "shape":
            return ScaleShapeDiscrete(aesthetic=aesthetic)

        case "linetype":
            return ScaleLinetypeDiscrete(aesthetic=aesthetic)

        case "linewidth":
            from plotten.scales._linewidth import (
                ScaleLinewidthContinuous,
                ScaleLinewidthDiscrete,
            )

            if s.dtype.is_numeric():
                return ScaleLinewidthContinuous(aesthetic=aesthetic)
            return ScaleLinewidthDiscrete(aesthetic=aesthetic)

        case "hatch":
            from plotten.scales._hatch import ScaleHatchDiscrete

            return ScaleHatchDiscrete(aesthetic=aesthetic)

    # Detect temporal dtypes before numeric check
    if s.dtype.is_temporal():
        return ScaleDateContinuous(aesthetic=aesthetic)

    if s.dtype.is_numeric():
        return ScaleContinuous(aesthetic=aesthetic)
    return ScaleDiscrete(aesthetic=aesthetic)
