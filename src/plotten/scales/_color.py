from __future__ import annotations

from typing import Any

import matplotlib
import matplotlib.colors as mcolors
import narwhals as nw

from plotten.scales._base import ScaleBase


class ScaleColorContinuous(ScaleBase):
    """Map numeric values to a matplotlib colormap."""

    def __init__(self, aesthetic: str = "color", cmap_name: str = "viridis") -> None:
        super().__init__(aesthetic)
        self._cmap_name = cmap_name
        self._cmap = matplotlib.colormaps[cmap_name]
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
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        span = hi - lo if hi != lo else 1.0
        normalized = [(v - lo) / span for v in s.to_list()]
        return [mcolors.to_hex(self._cmap(n)) for n in normalized]

    def get_limits(self) -> tuple[float, float]:
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        return (lo, hi)

    def get_breaks(self) -> list:
        import numpy as np

        lo, hi = self.get_limits()
        return np.linspace(lo, hi, 5).tolist()


class ScaleColorDiscrete(ScaleBase):
    """Map categorical values to distinct colors."""

    def __init__(self, aesthetic: str = "color", palette: str = "tab10") -> None:
        super().__init__(aesthetic)
        self._palette_name = palette
        self._cmap = matplotlib.colormaps[palette]
        self._levels: list = []

    def train(self, values: Any) -> None:
        s = nw.from_native(values, series_only=True)
        new_levels = s.unique().sort().to_list()
        for lev in new_levels:
            if lev not in self._levels:
                self._levels.append(lev)

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        n = max(len(self._levels), 1)
        color_map = {
            lev: mcolors.to_hex(self._cmap(i / max(n - 1, 1)))
            for i, lev in enumerate(self._levels)
        }
        return [color_map[v] for v in s.to_list()]

    def get_limits(self) -> tuple[float, float]:
        return (0, len(self._levels))

    def get_breaks(self) -> list:
        return list(range(len(self._levels)))

    def get_labels(self) -> list[str]:
        return [str(lev) for lev in self._levels]


def scale_color_continuous(cmap: str = "viridis") -> ScaleColorContinuous:
    return ScaleColorContinuous(cmap_name=cmap)


def scale_color_discrete(palette: str = "tab10") -> ScaleColorDiscrete:
    return ScaleColorDiscrete(palette=palette)
