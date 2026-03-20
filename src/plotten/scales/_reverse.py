from __future__ import annotations

from plotten.scales._position import ScaleContinuous


class ScaleReverse(ScaleContinuous):
    """Reversed scale for position aesthetics."""

    def __init__(self, aesthetic: str = "x", **kwargs) -> None:
        super().__init__(aesthetic, **kwargs)

    def get_limits(self) -> tuple[float, float]:
        lo, hi = super().get_limits()
        return (hi, lo)


def scale_x_reverse(**kwargs) -> ScaleReverse:
    """Set x-axis to a reversed continuous scale.

    Parameters
    ----------
    **kwargs
        Passed to the underlying continuous scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_x_reverse
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_x_reverse()
    Plot(...)
    """
    return ScaleReverse(aesthetic="x", **kwargs)


def scale_y_reverse(**kwargs) -> ScaleReverse:
    """Set y-axis to a reversed continuous scale.

    Parameters
    ----------
    **kwargs
        Passed to the underlying continuous scale (e.g. ``breaks``, ``limits``).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, scale_y_reverse
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + scale_y_reverse()
    Plot(...)
    """
    return ScaleReverse(aesthetic="y", **kwargs)
