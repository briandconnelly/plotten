"""Out-of-bounds handling and rescaling utilities."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def rescale(
    x: Sequence[float],
    to: tuple[float, float] = (0.0, 1.0),
    from_: tuple[float, float] | None = None,
) -> list[float]:
    """Rescale values to a new range.

    Parameters
    ----------
    x : sequence of float
        Values to rescale.
    to : tuple
        Target ``(min, max)`` range (default ``(0, 1)``).
    from\\_ : tuple, optional
        Source ``(min, max)`` range. Defaults to ``(min(x), max(x))``.

    Examples
    --------
    >>> rescale([0, 5, 10])
    [0.0, 0.5, 1.0]
    >>> rescale([0, 5, 10], to=(0, 100))
    [0.0, 50.0, 100.0]
    """
    vals = list(x)
    if not vals:
        return []
    if from_ is None:
        lo = min(vals)
        hi = max(vals)
    else:
        lo, hi = from_
    span = hi - lo
    if span == 0:
        mid = (to[0] + to[1]) / 2
        return [mid] * len(vals)
    to_span = to[1] - to[0]
    return [(v - lo) / span * to_span + to[0] for v in vals]


def rescale_mid(
    x: Sequence[float],
    to: tuple[float, float] = (0.0, 1.0),
    from_: tuple[float, float] | None = None,
    mid: float = 0.0,
) -> list[float]:
    """Rescale values with a fixed midpoint.

    Useful for diverging scales where zero (or another midpoint) should
    map to the centre of the output range.

    Parameters
    ----------
    x : sequence of float
        Values to rescale.
    to : tuple
        Target ``(min, max)`` range.
    from\\_ : tuple, optional
        Source ``(min, max)`` range. Defaults to ``(min(x), max(x))``.
    mid : float
        Value that maps to the midpoint of *to*.

    Examples
    --------
    >>> rescale_mid([-2, 0, 4], mid=0)
    [0.25, 0.5, 1.0]
    """
    vals = list(x)
    if not vals:
        return []
    if from_ is None:
        lo = min(vals)
        hi = max(vals)
    else:
        lo, hi = from_
    to_mid = (to[0] + to[1]) / 2
    result: list[float] = []
    for v in vals:
        if v <= mid:
            span = mid - lo
            if span == 0:
                result.append(to_mid)
            else:
                result.append(to[0] + (v - lo) / span * (to_mid - to[0]))
        else:
            span = hi - mid
            if span == 0:
                result.append(to_mid)
            else:
                result.append(to_mid + (v - mid) / span * (to[1] - to_mid))
    return result


def squish(
    x: Sequence[float],
    limits: tuple[float, float] = (0.0, 1.0),
) -> list[float]:
    """Clamp values to a range (squish out-of-bounds values to the nearest limit).

    Parameters
    ----------
    x : sequence of float
        Values to squish.
    limits : tuple
        ``(min, max)`` bounds.

    Examples
    --------
    >>> squish([-1, 0.5, 2], limits=(0, 1))
    [0, 0.5, 1]
    """
    lo, hi = limits
    return [max(lo, min(v, hi)) for v in x]


def censor(
    x: Sequence[float | None],
    limits: tuple[float, float] = (0.0, 1.0),
    only_finite: bool = True,
) -> list[float | None]:
    """Replace out-of-bounds values with ``None``.

    Parameters
    ----------
    x : sequence of float
        Values to censor.
    limits : tuple
        ``(min, max)`` bounds.
    only_finite : bool
        If ``True`` (default), infinite values are also censored.

    Examples
    --------
    >>> censor([-1, 0.5, 2], limits=(0, 1))
    [None, 0.5, None]
    """
    lo, hi = limits
    result: list[float | None] = []
    for v in x:
        if v is None or (only_finite and not math.isfinite(v)) or v < lo or v > hi:
            result.append(None)
        else:
            result.append(v)
    return result


def oob_squish(
    limits: tuple[float, float] = (0.0, 1.0),
) -> Callable[[list[float]], list[float]]:
    """Return an out-of-bounds handler that squishes values to the range.

    Intended for use as an ``oob`` parameter on scales.

    Examples
    --------
    >>> handler = oob_squish(limits=(0, 10))
    >>> handler([-5, 3, 15])
    [0, 3, 10]
    """

    def _handler(x: list[float]) -> list[float]:
        return squish(x, limits=limits)

    return _handler


def oob_censor(
    limits: tuple[float, float] = (0.0, 1.0),
) -> Callable[[list[float]], list[float | None]]:
    """Return an out-of-bounds handler that censors values outside the range.

    Intended for use as an ``oob`` parameter on scales.

    Examples
    --------
    >>> handler = oob_censor(limits=(0, 10))
    >>> handler([-5, 3, 15])
    [None, 3, None]
    """

    def _handler(x: list[float]) -> list[float | None]:
        return censor(x, limits=limits)

    return _handler


def oob_keep() -> Callable[[list[float]], list[float]]:
    """Return an out-of-bounds handler that keeps all values unchanged.

    Examples
    --------
    >>> handler = oob_keep()
    >>> handler([-5, 3, 15])
    [-5, 3, 15]
    """
    return lambda x: list(x)


def expand_range(
    limits: tuple[float, float],
    mul: float = 0.0,
    add: float = 0.0,
) -> tuple[float, float]:
    """Expand a numeric range by a multiplicative and additive amount.

    Parameters
    ----------
    limits : tuple
        ``(min, max)`` range to expand.
    mul : float
        Multiplicative expansion factor (default 0).
    add : float
        Additive expansion amount (default 0).

    Examples
    --------
    >>> expand_range((0, 10), mul=0.1)
    (-1.0, 11.0)
    >>> expand_range((0, 10), add=2)
    (-2, 12)
    """
    lo, hi = limits
    span = hi - lo
    return (lo - span * mul - add, hi + span * mul + add)


def zero_range(limits: tuple[float, float], tol: float = 1e-6) -> bool:
    """Check if a range has (approximately) zero width.

    Parameters
    ----------
    limits : tuple
        ``(min, max)`` range.
    tol : float
        Relative tolerance.

    Examples
    --------
    >>> zero_range((0, 0))
    True
    >>> zero_range((0, 1))
    False
    >>> zero_range((1, 1 + 1e-8))
    True
    """
    lo, hi = limits
    if lo == hi:
        return True
    return abs(hi - lo) < tol * max(abs(lo), abs(hi), 1.0)
