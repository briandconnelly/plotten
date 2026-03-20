"""Convenience functions for setting axis limits."""

from __future__ import annotations

from plotten.scales._position import ScaleContinuous


def xlim(lo: float, hi: float) -> ScaleContinuous:
    """Set x-axis limits.

    Shorthand for ``scale_x_continuous(limits=(lo, hi))``.

    Parameters
    ----------
    lo : float
        Lower limit.
    hi : float
        Upper limit.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, xlim
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + xlim(0, 5)
    Plot(...)
    """
    return ScaleContinuous(aesthetic="x", limits=(lo, hi))


def ylim(lo: float, hi: float) -> ScaleContinuous:
    """Set y-axis limits.

    Shorthand for ``scale_y_continuous(limits=(lo, hi))``.

    Parameters
    ----------
    lo : float
        Lower limit.
    hi : float
        Upper limit.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, ylim
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + ylim(0, 10)
    Plot(...)
    """
    return ScaleContinuous(aesthetic="y", limits=(lo, hi))
