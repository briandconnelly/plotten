"""Binning helpers for continuous variables."""

from __future__ import annotations

from typing import Any

import numpy as np


def cut_width(x: Any, width: float, *, center: float | None = None) -> list[str]:
    """Bin a numeric variable into fixed-width bins.

    Parameters
    ----------
    x : array-like
        Numeric values to bin.
    width : float
        Bin width.
    center : float or None, optional
        Center of one bin (default uses the data minimum as the left edge).

    Returns
    -------
    list of str
        Bin labels in ``"[lo, hi)"`` format.

    Examples
    --------
    >>> cut_width([1, 5, 10, 15, 20], 10)
    ['[1, 11)', '[1, 11)', '[1, 11)', '[11, 21)', '[11, 21)']
    """
    arr = np.asarray(x, dtype=float)
    lo, hi = float(arr.min()), float(arr.max())

    if center is not None:
        # Shift so that `center` is the midpoint of a bin
        offset = center - width / 2
        start = offset + np.floor((lo - offset) / width) * width
    else:
        start = lo

    breaks = []
    edge = start
    while edge <= hi:
        breaks.append(edge)
        edge += width
    breaks.append(edge)  # ensure the last value is captured

    breaks_arr = np.array(breaks)
    indices = np.searchsorted(breaks_arr, arr, side="right") - 1
    indices = np.clip(indices, 0, len(breaks_arr) - 2)

    return [f"[{breaks_arr[i]:.6g}, {breaks_arr[i + 1]:.6g})" for i in indices]


def cut_interval(x: Any, n: int = 10) -> list[str]:
    """Bin a numeric variable into *n* bins of equal range.

    Parameters
    ----------
    x : array-like
        Numeric values to bin.
    n : int, optional
        Number of bins (default 10).

    Returns
    -------
    list of str
        Bin labels in ``"[lo, hi)"`` format.

    Examples
    --------
    >>> cut_interval([1, 2, 3, 4, 5], 2)
    ['[1, 3)', '[1, 3)', '[1, 3)', '[3, 5.1)', '[3, 5.1)']
    """
    arr = np.asarray(x, dtype=float)
    lo, hi = float(arr.min()), float(arr.max())
    width = (hi - lo) / n if hi != lo else 1.0
    return cut_width(arr, width)


def cut_number(x: Any, n: int = 10) -> list[str]:
    """Bin a numeric variable into *n* bins with roughly equal counts.

    Uses quantile-based bin edges so each bin has approximately the same
    number of observations.

    Parameters
    ----------
    x : array-like
        Numeric values to bin.
    n : int, optional
        Target number of bins (default 10).

    Returns
    -------
    list of str
        Bin labels in ``"[lo, hi)"`` format.

    Examples
    --------
    >>> cut_number([1, 2, 3, 4, 5, 6], 3)
    ['[1, 3)', '[1, 3)', '[3, 5)', '[3, 5)', '[5, 6.01)', '[5, 6.01)']
    """
    arr = np.asarray(x, dtype=float)
    quantiles = np.linspace(0, 100, n + 1)
    breaks = np.unique(np.percentile(arr, quantiles))

    # Ensure we capture the maximum value
    if breaks[-1] == arr.max():
        breaks[-1] = arr.max() + abs(arr.max()) * 0.001 + 0.001

    indices = np.searchsorted(breaks, arr, side="right") - 1
    indices = np.clip(indices, 0, len(breaks) - 2)

    return [f"[{breaks[i]:.6g}, {breaks[i + 1]:.6g})" for i in indices]
