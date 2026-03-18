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
    return CoordEqual(**kwargs)


def coord_fixed(ratio: float = 1, **kwargs: Any) -> CoordFixed:
    return CoordFixed(ratio=ratio, **kwargs)
