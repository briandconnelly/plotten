from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class CoordFlip:
    """Flip x and y axes."""

    def __init__(
        self,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
    ) -> None:
        self.xlim = xlim
        self.ylim = ylim

    def transform(self, data: Any, ax: Axes) -> Any:
        return data


def coord_flip(
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
) -> CoordFlip:
    """Create a flipped coordinate system."""
    return CoordFlip(xlim=xlim, ylim=ylim)
