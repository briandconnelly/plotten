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
    """Create a Cartesian coordinate system with visual-only zoom."""
    return CoordCartesian(xlim=xlim, ylim=ylim, expand=expand, clip=clip)
