from __future__ import annotations

from typing import Any

from plotten.scales._base import LegendEntry
from plotten.scales._color import ScaleColorContinuous


class ScaleGradient(ScaleColorContinuous):
    """Two-color linear gradient scale."""

    def __init__(
        self,
        aesthetic: str = "color",
        low: str = "#132B43",
        high: str = "#56B1F7",
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        from matplotlib.colors import LinearSegmentedColormap

        super().__init__(aesthetic=aesthetic, cmap_name="viridis", breaks=breaks, limits=limits)
        self._low = low
        self._high = high
        self._cmap = LinearSegmentedColormap.from_list("gradient2", [low, high], N=256)

    def legend_entries(self) -> list[LegendEntry]:
        import matplotlib.colors as mcolors

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


class ScaleGradient2(ScaleColorContinuous):
    """Diverging three-color gradient scale with a midpoint."""

    def __init__(
        self,
        aesthetic: str = "color",
        low: str = "#67001F",
        mid: str = "#FFFFFF",
        high: str = "#053061",
        midpoint: float = 0,
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        from matplotlib.colors import LinearSegmentedColormap

        super().__init__(aesthetic=aesthetic, cmap_name="viridis", breaks=breaks, limits=limits)
        self._low = low
        self._mid = mid
        self._high = high
        self._midpoint = midpoint
        self._cmap = LinearSegmentedColormap.from_list("gradient3", [low, mid, high], N=256)

    def map_data(self, values: Any) -> Any:
        import matplotlib.colors as mcolors
        import narwhals as nw

        s = nw.from_native(values, series_only=True)
        lo, hi = self.get_limits()
        mid = self._midpoint
        result = []
        for v in s.to_list():
            if v <= mid:
                span = mid - lo if mid != lo else 1.0
                norm = (v - lo) / span * 0.5
            else:
                span = hi - mid if hi != mid else 1.0
                norm = 0.5 + (v - mid) / span * 0.5
            norm = max(0.0, min(1.0, norm))
            result.append(mcolors.to_hex(self._cmap(norm)))
        return result

    def legend_entries(self) -> list[LegendEntry]:
        import matplotlib.colors as mcolors

        breaks = self.get_breaks()
        lo, hi = self.get_limits()
        mid = self._midpoint
        entries = []
        for b in breaks:
            if b <= mid:
                span = mid - lo if mid != lo else 1.0
                norm = (b - lo) / span * 0.5
            else:
                span = hi - mid if hi != mid else 1.0
                norm = 0.5 + (b - mid) / span * 0.5
            norm = max(0.0, min(1.0, norm))
            hex_color = mcolors.to_hex(self._cmap(norm))
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=f"{b:.3g}", fill=hex_color))
            else:
                entries.append(LegendEntry(label=f"{b:.3g}", color=hex_color))
        return entries


def scale_color_gradient(
    low: str = "#132B43", high: str = "#56B1F7", **kwargs: Any
) -> ScaleGradient:
    return ScaleGradient(aesthetic="color", low=low, high=high, **kwargs)


def scale_fill_gradient(
    low: str = "#132B43", high: str = "#56B1F7", **kwargs: Any
) -> ScaleGradient:
    return ScaleGradient(aesthetic="fill", low=low, high=high, **kwargs)


def scale_color_gradient2(
    low: str = "#67001F",
    mid: str = "#FFFFFF",
    high: str = "#053061",
    midpoint: float = 0,
    **kwargs: Any,
) -> ScaleGradient2:
    return ScaleGradient2(
        aesthetic="color", low=low, mid=mid, high=high, midpoint=midpoint, **kwargs
    )


def scale_fill_gradient2(
    low: str = "#67001F",
    mid: str = "#FFFFFF",
    high: str = "#053061",
    midpoint: float = 0,
    **kwargs: Any,
) -> ScaleGradient2:
    return ScaleGradient2(
        aesthetic="fill", low=low, mid=mid, high=high, midpoint=midpoint, **kwargs
    )
