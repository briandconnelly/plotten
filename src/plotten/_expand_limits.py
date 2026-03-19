"""expand_limits() — ensure axes include specific values."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExpandLimits:
    """Sentinel values that position scales must include."""

    x: tuple[float, ...] = ()
    y: tuple[float, ...] = ()


def expand_limits(
    x: float | list[float] | None = None,
    y: float | list[float] | None = None,
) -> ExpandLimits:
    """Ensure axis includes specific values without hard-setting limits.

    Returns an ``ExpandLimits`` object to be added to a plot via ``+``.
    """
    x_vals: tuple[float, ...] = ()
    y_vals: tuple[float, ...] = ()
    if x is not None:
        x_vals = tuple(x) if isinstance(x, list) else (x,)
    if y is not None:
        y_vals = tuple(y) if isinstance(y, list) else (y,)
    return ExpandLimits(x=x_vals, y=y_vals)
