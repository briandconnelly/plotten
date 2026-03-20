"""Binned position scales — discretize continuous data into bins."""

from __future__ import annotations

import bisect
from typing import Any

import narwhals as nw
import numpy as np

from plotten.scales._base import ScaleBase


class ScaleBinnedPosition(ScaleBase):
    """Position scale that snaps continuous values to bin centers."""

    def __init__(
        self,
        aesthetic: str = "x",
        n_bins: int = 10,
        breaks: list[float] | None = None,
        limits: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(aesthetic)
        self._n_bins = n_bins
        self._breaks_arg = breaks
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
        self._invalidate_cache()

    def _bin_edges(self) -> list[float]:
        cached = self._cache.get("edges")
        if cached is not None:
            return cached
        lo, hi = self.get_limits()
        edges = np.linspace(lo, hi, self._n_bins + 1).tolist()
        self._cache["edges"] = edges
        return edges

    def _bin_centers(self) -> list[float]:
        cached = self._cache.get("centers")
        if cached is not None:
            return cached
        edges = self._bin_edges()
        centers = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
        self._cache["centers"] = centers
        return centers

    def map_data(self, values: Any) -> Any:
        s = nw.from_native(values, series_only=True)
        edges = self._bin_edges()
        centers = self._bin_centers()
        result = []
        for v in s.to_list():
            idx = bisect.bisect_right(edges, v) - 1
            idx = max(0, min(idx, len(centers) - 1))
            result.append(centers[idx])
        return result

    def get_limits(self) -> tuple[float, float]:
        if self._limits is not None:
            return self._limits
        lo = self._domain_min if self._domain_min is not None else 0.0
        hi = self._domain_max if self._domain_max is not None else 1.0
        span = hi - lo
        pad = span * 0.05 if span > 0 else 0.5
        return (lo - pad, hi + pad)

    def get_breaks(self) -> list:
        if self._breaks_arg is not None:
            return list(self._breaks_arg)
        return self._bin_centers()

    def get_labels(self) -> list[str]:
        cached = self._cache.get("labels")
        if cached is not None:
            return cached
        edges = self._bin_edges()
        labels = [f"[{edges[i]:.3g}, {edges[i + 1]:.3g})" for i in range(len(edges) - 1)]
        self._cache["labels"] = labels
        return labels


def scale_x_binned(n_bins: int = 10, **kwargs: Any) -> ScaleBinnedPosition:
    """Bin continuous x-axis data into discrete bins.

    Parameters
    ----------
    n_bins : int, optional
        Number of bins (default 10).
    breaks : list of float, optional
        Explicit break values.
    limits : tuple of float, optional
        Fixed ``(min, max)`` domain limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_x_binned
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_binned(n_bins=3)
    Plot(...)
    """
    return ScaleBinnedPosition(aesthetic="x", n_bins=n_bins, **kwargs)


def scale_y_binned(n_bins: int = 10, **kwargs: Any) -> ScaleBinnedPosition:
    """Bin continuous y-axis data into discrete bins.

    Parameters
    ----------
    n_bins : int, optional
        Number of bins (default 10).
    breaks : list of float, optional
        Explicit break values.
    limits : tuple of float, optional
        Fixed ``(min, max)`` domain limits.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_y_binned
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_binned(n_bins=3)
    Plot(...)
    """
    return ScaleBinnedPosition(aesthetic="y", n_bins=n_bins, **kwargs)
