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


class ScaleBase:
    """Base class for all scales."""

    _domain_min: float | None
    _domain_max: float | None

    def __init__(self, aesthetic: str) -> None:
        self.aesthetic = aesthetic
        self._domain_min = None
        self._domain_max = None

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


def auto_scale(aesthetic: str, series: Any) -> ScaleBase:
    """Pick the right scale based on narwhals dtype."""
    from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete
    from plotten.scales._position import ScaleContinuous, ScaleDiscrete

    s = nw.from_native(series, series_only=True)

    match aesthetic:
        case "color" | "fill":
            if s.dtype.is_numeric():
                return ScaleColorContinuous(aesthetic=aesthetic)
            return ScaleColorDiscrete(aesthetic=aesthetic)

        case "size":
            try:
                from plotten.scales._size import ScaleSizeContinuous, ScaleSizeDiscrete

                if s.dtype.is_numeric():
                    return ScaleSizeContinuous(aesthetic=aesthetic)
                return ScaleSizeDiscrete(aesthetic=aesthetic)
            except ImportError:
                pass

        case "alpha":
            try:
                from plotten.scales._alpha import (
                    ScaleAlphaContinuous,
                    ScaleAlphaDiscrete,
                )

                if s.dtype.is_numeric():
                    return ScaleAlphaContinuous(aesthetic=aesthetic)
                return ScaleAlphaDiscrete(aesthetic=aesthetic)
            except ImportError:
                pass

        case "shape":
            try:
                from plotten.scales._shape import ScaleShapeDiscrete

                return ScaleShapeDiscrete(aesthetic=aesthetic)
            except ImportError:
                pass

        case "linetype":
            try:
                from plotten.scales._linetype import ScaleLinetypeDiscrete

                return ScaleLinetypeDiscrete(aesthetic=aesthetic)
            except ImportError:
                pass

    # Detect temporal dtypes before numeric check
    dtype_str = str(s.dtype).lower()
    if any(t in dtype_str for t in ("date", "datetime", "timestamp")):
        try:
            from plotten.scales._date import ScaleDateContinuous

            return ScaleDateContinuous(aesthetic=aesthetic)
        except ImportError:
            pass

    if s.dtype.is_numeric():
        return ScaleContinuous(aesthetic=aesthetic)
    return ScaleDiscrete(aesthetic=aesthetic)
