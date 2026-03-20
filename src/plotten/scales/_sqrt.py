from __future__ import annotations

from plotten.scales._position import ScaleContinuous


class ScaleSqrt(ScaleContinuous):
    """Square root scale for position aesthetics."""

    __slots__ = ()

    def __init__(self, aesthetic: str = "x", **kwargs) -> None:
        super().__init__(aesthetic, **kwargs)

    def get_limits(self) -> tuple[float, float]:
        lo, hi = super().get_limits()
        return (max(lo, 0), hi)


def scale_x_sqrt(**kwargs) -> ScaleSqrt:
    """Set x-axis to a square-root scale.

    Parameters
    ----------
    **kwargs
        Passed to the underlying continuous scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_x_sqrt
    >>> df = pd.DataFrame({"x": [0, 4, 16], "y": [1, 2, 3]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_sqrt()
    Plot(...)
    """
    return ScaleSqrt(aesthetic="x", **kwargs)


def scale_y_sqrt(**kwargs) -> ScaleSqrt:
    """Set y-axis to a square-root scale.

    Parameters
    ----------
    **kwargs
        Passed to the underlying continuous scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_y_sqrt
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [0, 4, 16]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_sqrt()
    Plot(...)
    """
    return ScaleSqrt(aesthetic="y", **kwargs)
