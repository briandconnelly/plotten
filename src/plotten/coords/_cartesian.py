from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class CoordCartesian:
    """Cartesian coordinate system with optional axis limits."""

    def __init__(
        self,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        expand: tuple[float, float] | None = None,
        clip: bool = True,
    ) -> None:
        self.xlim = xlim
        self.ylim = ylim
        self.expand = expand
        self.clip = clip

    def transform(self, data: Any, ax: Axes) -> Any:
        """Apply coordinate limits to the axes."""
        if self.xlim is not None:
            ax.set_xlim(self.xlim)
        if self.ylim is not None:
            ax.set_ylim(self.ylim)
        return data


def coord_cartesian(
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    expand: tuple[float, float] | None = None,
    clip: bool = True,
) -> CoordCartesian:
    """Zoom into a Cartesian plot without clipping the underlying data.

    Parameters
    ----------
    xlim : tuple of float or None
        Visual ``(min, max)`` limits for the x-axis.
    ylim : tuple of float or None
        Visual ``(min, max)`` limits for the y-axis.
    expand : tuple of float or None
        Multiplicative and additive expansion constants.
    clip : bool
        Whether to clip drawing to the panel area.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.coords import coord_cartesian
    >>> df = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point() + coord_cartesian(xlim=(1, 3))
    """
    return CoordCartesian(xlim=xlim, ylim=ylim, expand=expand, clip=clip)
