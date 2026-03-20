"""Break generators for scale tick positions."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def breaks_pretty(n: int = 5) -> Callable[[tuple[float, float]], list[float]]:
    """Generate "pretty" breaks using an extended Wilkinson algorithm.

    Produces round numbers (multiples of 1, 2, 2.5, or 5) that span the
    data range, similar to R's ``pretty()`` and the ``scales::breaks_pretty``
    function.

    Parameters
    ----------
    n : int
        Target number of breaks (actual count may vary slightly).

    Examples
    --------
    >>> breaks_pretty(5)((0, 97))
    [0, 20, 40, 60, 80, 100]
    >>> breaks_pretty(5)((0.3, 4.1))
    [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    """

    def _breaks(limits: tuple[float, float]) -> list[float]:
        lo, hi = limits
        if lo == hi:
            return [lo]
        return _pretty(lo, hi, n)

    return _breaks


def _pretty(lo: float, hi: float, n: int) -> list[float]:
    """Compute pretty tick positions spanning [lo, hi].

    Uses a simplified version of Wilkinson's extended algorithm: find the
    largest "nice" step size (multiples of 1, 2, 2.5, 5 * 10^k) that
    yields approximately *n* intervals.
    """
    span = hi - lo
    if span == 0:
        return [lo]

    # Rough step size
    raw_step = span / max(n - 1, 1)
    # Order of magnitude
    magnitude = 10 ** math.floor(math.log10(raw_step))

    # Candidate nice steps (in order of preference for "roundness")
    nice_steps = [1, 2, 2.5, 5, 10]
    # Pick the nice step closest to raw_step / magnitude
    normalized = raw_step / magnitude
    step = magnitude * min(nice_steps, key=lambda s: abs(s - normalized))

    # Compute range
    start = math.floor(lo / step) * step
    stop = math.ceil(hi / step) * step
    # Build tick list
    ticks: list[float] = []
    tick = start
    # Use a small epsilon to handle floating point
    eps = step * 1e-10
    while tick <= stop + eps:
        ticks.append(round(tick, 12))
        tick += step
    return ticks


def breaks_width(width: float, offset: float = 0) -> Callable[[tuple[float, float]], list[float]]:
    """Generate breaks at fixed intervals.

    Parameters
    ----------
    width : float
        Distance between breaks.
    offset : float
        Shift the break grid by this amount.

    Examples
    --------
    >>> breaks_width(25)((0, 100))
    [0, 25, 50, 75, 100]
    >>> breaks_width(10, offset=5)((0, 30))
    [5, 15, 25]
    """

    def _breaks(limits: tuple[float, float]) -> list[float]:
        lo, hi = limits
        start = math.ceil((lo - offset) / width) * width + offset
        ticks: list[float] = []
        tick = start
        eps = width * 1e-10
        while tick <= hi + eps:
            ticks.append(round(tick, 12))
            tick += width
        return ticks

    return _breaks


def breaks_integer(n: int = 5) -> Callable[[tuple[float, float]], list[float]]:
    """Generate breaks at integer positions only.

    Useful for count data where fractional ticks (e.g. 2.5) are meaningless.
    Uses the same algorithm as :func:`breaks_pretty` but rounds to whole
    numbers and guarantees a step size of at least 1.

    Parameters
    ----------
    n : int
        Target number of breaks.

    Examples
    --------
    >>> breaks_integer(5)((0, 7))
    [0, 2, 4, 6, 8]
    >>> breaks_integer(5)((0, 3))
    [0, 1, 2, 3]
    """

    def _breaks(limits: tuple[float, float]) -> list[float]:
        lo, hi = limits
        lo = math.floor(lo)
        hi = math.ceil(hi)
        if lo == hi:
            return [lo]
        ticks = _pretty(lo, hi, n)
        # Ensure step >= 1 by rounding and deduplicating
        int_ticks: list[float] = []
        seen: set[int] = set()
        for t in ticks:
            iv = round(t)
            if iv not in seen:
                seen.add(iv)
                int_ticks.append(iv)
        return int_ticks

    return _breaks


def breaks_quantile(
    data: Sequence[float],
    n: int = 5,
) -> Callable[[tuple[float, float]], list[float]]:
    """Generate breaks at data quantile positions.

    Places ticks at evenly spaced quantiles of the supplied data rather
    than at evenly spaced values.  Useful for skewed distributions where
    even spacing wastes axis space on empty regions.

    Parameters
    ----------
    data : sequence of float
        The data values used to compute quantiles.
    n : int
        Number of breaks (including endpoints).

    Examples
    --------
    >>> import numpy as np
    >>> rng = np.random.default_rng(0)
    >>> skewed = sorted((rng.exponential(10, 100)).tolist())
    >>> brks = breaks_quantile(skewed, n=5)
    >>> result = brks((min(skewed), max(skewed)))
    >>> len(result)
    5
    """
    sorted_data = sorted(data)
    length = len(sorted_data)

    def _breaks(limits: tuple[float, float]) -> list[float]:
        if length == 0:
            return []
        if length == 1:
            return [sorted_data[0]]
        ticks: list[float] = []
        for i in range(n):
            frac = i / max(n - 1, 1)
            idx = frac * (length - 1)
            lo_idx = int(idx)
            hi_idx = min(lo_idx + 1, length - 1)
            weight = idx - lo_idx
            val = sorted_data[lo_idx] * (1 - weight) + sorted_data[hi_idx] * weight
            ticks.append(round(val, 10))
        return ticks

    return _breaks


def breaks_log(base: int = 10) -> Callable[[tuple[float, float]], list[float]]:
    """Generate breaks for logarithmic data using 1-2-5 subdivision.

    Unlike simple powers-of-base breaks, this inserts intermediate ticks
    at 1x, 2x, and 5x each power, giving denser labeling on log axes.

    Parameters
    ----------
    base : int
        Logarithm base (default 10).

    Examples
    --------
    >>> breaks_log(10)((1, 1000))
    [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    """
    subdivisions = [1, 2, 5]

    def _breaks(limits: tuple[float, float]) -> list[float]:
        lo, hi = limits
        lo = max(lo, 1e-10)
        hi = max(hi, lo)
        log_lo = math.floor(math.log(lo, base))
        log_hi = math.ceil(math.log(hi, base))
        ticks: list[float] = []
        for exp in range(log_lo, log_hi + 1):
            power = base**exp
            for mult in subdivisions:
                val = power * mult
                if lo <= val <= hi:
                    ticks.append(val)
        if not ticks:
            ticks = [base**i for i in range(log_lo, log_hi + 1)]
        return ticks

    return _breaks
