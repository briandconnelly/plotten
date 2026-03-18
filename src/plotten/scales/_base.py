from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import narwhals as nw


@dataclass(frozen=True)
class LegendEntry:
    """A single entry in a legend."""

    label: str
    color: str | None = None
    fill: str | None = None
    size: float | None = None


class ScaleBase(ABC):
    """Base class for all scales."""

    def __init__(self, aesthetic: str) -> None:
        self.aesthetic = aesthetic

    @abstractmethod
    def train(self, values: Any) -> None: ...

    @abstractmethod
    def map_data(self, values: Any) -> Any: ...

    @abstractmethod
    def get_limits(self) -> tuple[float, float]: ...

    @abstractmethod
    def get_breaks(self) -> list: ...

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

    if aesthetic in ("color", "fill"):
        if s.dtype.is_numeric():
            return ScaleColorContinuous(aesthetic=aesthetic)
        return ScaleColorDiscrete(aesthetic=aesthetic)

    if s.dtype.is_numeric():
        return ScaleContinuous(aesthetic=aesthetic)
    return ScaleDiscrete(aesthetic=aesthetic)
