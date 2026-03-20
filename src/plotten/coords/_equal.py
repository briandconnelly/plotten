from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class CoordEqual:
    """Equal aspect ratio coordinate system."""

    def __init__(
        self,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
    ) -> None:
        self.xlim = xlim
        self.ylim = ylim

    def transform(self, data: Any, ax: Axes) -> Any:
        ax.set_aspect("equal")
        if self.xlim is not None:
            ax.set_xlim(self.xlim)
        if self.ylim is not None:
            ax.set_ylim(self.ylim)
        return data


class CoordFixed:
    """Fixed aspect ratio coordinate system."""

    def __init__(
        self,
        ratio: float = 1,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
    ) -> None:
        self.ratio = ratio
        self.xlim = xlim
        self.ylim = ylim

    def transform(self, data: Any, ax: Axes) -> Any:
        ax.set_aspect(self.ratio)
        if self.xlim is not None:
            ax.set_xlim(self.xlim)
        if self.ylim is not None:
            ax.set_ylim(self.ylim)
        return data


def coord_equal(**kwargs: Any) -> CoordEqual:
    """Set an equal aspect ratio so one unit on x equals one unit on y.

    Parameters
    ----------
    xlim : tuple of float or None
        Optional ``(min, max)`` limits for the x-axis.
    ylim : tuple of float or None
        Optional ``(min, max)`` limits for the y-axis.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.coords import coord_equal
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + coord_equal()
    """
    return CoordEqual(**kwargs)


def coord_fixed(ratio: float = 1, **kwargs: Any) -> CoordFixed:
    """Set a fixed aspect ratio for the coordinate system.

    Parameters
    ----------
    ratio : float
        The y/x aspect ratio. A value of 2 means one unit on y is twice as
        long as one unit on x.
    xlim : tuple of float or None
        Optional ``(min, max)`` limits for the x-axis.
    ylim : tuple of float or None
        Optional ``(min, max)`` limits for the y-axis.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.coords import coord_fixed
    >>> df = pd.DataFrame({"x": [0, 1, 2], "y": [0, 10, 20]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + coord_fixed(ratio=5)
    """
    return CoordFixed(ratio=ratio, **kwargs)
