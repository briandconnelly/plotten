from __future__ import annotations

import bisect
from typing import Any

import narwhals as nw

from plotten.scales._base import LegendEntry, MappedContinuousScale


class ScaleColorBinned(MappedContinuousScale):
    """Map continuous values to discrete color bins.

    Parameters
    ----------
    aesthetic
        The aesthetic this scale maps (``"color"`` or ``"fill"``).
    breaks
        Explicit bin boundaries (list of floats) or number of bins (int).
        When an int, evenly-spaced boundaries are computed from the trained
        data range.  Default is 5 bins.
    cmap
        Matplotlib colormap name.  Default ``"viridis"``.
    na_value
        Color used for ``NaN`` / out-of-range values.
    limits
        Optional fixed (lo, hi) domain limits.
    """

    def __init__(
        self,
        aesthetic: str = "color",
        breaks: list[float] | int = 5,
        cmap: str = "viridis",
        na_value: str = "#cccccc",
        limits: tuple[float, float] | None = None,
    ) -> None:
        import matplotlib

        super().__init__(aesthetic)
        self._breaks_spec = breaks
        self._cmap_name = cmap
        self._cmap = matplotlib.colormaps[cmap]
        self._na_value = na_value
        self._limits = limits
        # _breaks is used by MappedContinuousScale.get_breaks(); we override
        # get_breaks() so set this to None.
        self._breaks = None

    # ------------------------------------------------------------------
    # Bin computation
    # ------------------------------------------------------------------

    def _compute_boundaries(self) -> list[float]:
        """Return sorted internal bin boundaries (excluding domain min/max)."""
        import numpy as np

        lo, hi = self.get_limits()
        spec = self._breaks_spec
        if isinstance(spec, int):
            n_bins = max(spec, 1)
            return np.linspace(lo, hi, n_bins + 1).tolist()
        # spec is a list - treat as explicit boundaries including edges
        return sorted(spec)

    def _bin_edges(self) -> list[float]:
        """Full list of bin edges from lo to hi."""
        return self._compute_boundaries()

    # ------------------------------------------------------------------
    # Scale API
    # ------------------------------------------------------------------

    def get_breaks(self) -> list[float]:
        return self._bin_edges()

    def map_data(self, values: Any) -> Any:
        import math

        import matplotlib.colors as mcolors

        s = nw.from_native(values, series_only=True)
        edges = self._bin_edges()
        n_bins = len(edges) - 1
        if n_bins < 1:
            return [self._na_value] * len(s)

        # Pre-compute one color per bin (sample at bin midpoint in colormap)
        bin_colors: list[str] = []
        for i in range(n_bins):
            norm = i / max(n_bins - 1, 1)
            bin_colors.append(mcolors.to_hex(self._cmap(norm)))

        result: list[str] = []
        for v in s.to_list():
            if v is None or (isinstance(v, float) and math.isnan(v)):
                result.append(self._na_value)
                continue
            # bisect_right gives the index of the first edge > v
            idx = bisect.bisect_right(edges, v) - 1
            # clamp to valid bin range
            idx = max(0, min(idx, n_bins - 1))
            result.append(bin_colors[idx])
        return result

    def legend_entries(self) -> list[LegendEntry]:
        import matplotlib.colors as mcolors

        edges = self._bin_edges()
        n_bins = len(edges) - 1
        entries: list[LegendEntry] = []
        for i in range(n_bins):
            norm = i / max(n_bins - 1, 1)
            hex_color = mcolors.to_hex(self._cmap(norm))
            label = f"{edges[i]:.3g}\u2013{edges[i + 1]:.3g}"
            if self.aesthetic == "fill":
                entries.append(LegendEntry(label=label, fill=hex_color))
            else:
                entries.append(LegendEntry(label=label, color=hex_color))
        return entries


class ScaleFillBinned(ScaleColorBinned):
    """Binned continuous scale for the *fill* aesthetic."""

    def __init__(
        self,
        breaks: list[float] | int = 5,
        cmap: str = "viridis",
        na_value: str = "#cccccc",
        limits: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(
            aesthetic="fill",
            breaks=breaks,
            cmap=cmap,
            na_value=na_value,
            limits=limits,
        )


# ------------------------------------------------------------------
# 4B: Convenience factories
# ------------------------------------------------------------------


def scale_color_steps(n: int = 5, cmap: str = "viridis") -> ScaleColorBinned:
    """Binned color scale with *n* evenly-spaced bins."""
    return ScaleColorBinned(aesthetic="color", breaks=n, cmap=cmap)


def scale_fill_steps(n: int = 5, cmap: str = "viridis") -> ScaleFillBinned:
    """Binned fill scale with *n* evenly-spaced bins."""
    return ScaleFillBinned(breaks=n, cmap=cmap)


def scale_color_fermenter(n: int = 5, palette: str = "Blues") -> ScaleColorBinned:
    """Binned color scale using a Brewer / matplotlib palette."""
    return ScaleColorBinned(aesthetic="color", breaks=n, cmap=palette)


def scale_fill_fermenter(n: int = 5, palette: str = "Blues") -> ScaleFillBinned:
    """Binned fill scale using a Brewer / matplotlib palette."""
    return ScaleFillBinned(breaks=n, cmap=palette)
