from __future__ import annotations

from typing import Any

import matplotlib
import matplotlib.colors as mcolors

from plotten.scales._base import LegendEntry
from plotten.scales._color import ScaleColorContinuous, ScaleColorDiscrete


class ScaleBrewerDiscrete(ScaleColorDiscrete):
    """Discrete ColorBrewer palette scale."""

    def __init__(
        self,
        aesthetic: str = "color",
        palette: str = "Set1",
        direction: int = 1,
    ) -> None:
        super().__init__(aesthetic=aesthetic, palette=palette)
        self._direction = direction

    def map_data(self, values: Any) -> Any:
        import narwhals as nw

        s = nw.from_native(values, series_only=True)
        n = max(len(self._levels), 1)
        indices = list(range(n))
        if self._direction == -1:
            indices = indices[::-1]
        color_map = {
            lev: mcolors.to_hex(self._cmap(indices[i] / max(n - 1, 1)))
            for i, lev in enumerate(self._levels)
        }
        return [color_map[v] for v in s.to_list()]

    def legend_entries(self) -> list[LegendEntry]:
        n = max(len(self._levels), 1)
        indices = list(range(n))
        if self._direction == -1:
            indices = indices[::-1]
        entries = []
        for i, lev in enumerate(self._levels):
            hex_color = mcolors.to_hex(self._cmap(indices[i] / max(n - 1, 1)))
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=str(lev), fill=hex_color))
            else:
                entries.append(LegendEntry(label=str(lev), color=hex_color))
        return entries


class ScaleBrewerContinuous(ScaleColorContinuous):
    """Continuous ColorBrewer palette scale (distiller)."""

    def __init__(
        self,
        aesthetic: str = "color",
        palette: str = "RdYlBu",
        direction: int = 1,
    ) -> None:
        super().__init__(aesthetic=aesthetic, cmap_name=palette)
        self._direction = direction
        if direction == -1:
            self._cmap = matplotlib.colormaps[palette].reversed()

    def legend_entries(self) -> list[LegendEntry]:
        breaks = self.get_breaks()
        lo, hi = self.get_limits()
        span = hi - lo if hi != lo else 1.0
        entries = []
        for b in breaks:
            norm = (b - lo) / span
            hex_color = mcolors.to_hex(self._cmap(norm))
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=f"{b:.3g}", fill=hex_color))
            else:
                entries.append(LegendEntry(label=f"{b:.3g}", color=hex_color))
        return entries


def scale_color_brewer(palette: str = "Set1", direction: int = 1) -> ScaleBrewerDiscrete:
    return ScaleBrewerDiscrete(aesthetic="color", palette=palette, direction=direction)


def scale_fill_brewer(palette: str = "Set1", direction: int = 1) -> ScaleBrewerDiscrete:
    return ScaleBrewerDiscrete(aesthetic="fill", palette=palette, direction=direction)


def scale_color_distiller(palette: str = "RdYlBu", direction: int = 1) -> ScaleBrewerContinuous:
    return ScaleBrewerContinuous(aesthetic="color", palette=palette, direction=direction)


def scale_fill_distiller(palette: str = "RdYlBu", direction: int = 1) -> ScaleBrewerContinuous:
    return ScaleBrewerContinuous(aesthetic="fill", palette=palette, direction=direction)
