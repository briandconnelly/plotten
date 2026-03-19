from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class CoordPolar:
    """Polar coordinate system."""

    def __init__(
        self,
        theta: str = "x",
        start: float = 0,
        direction: int = 1,
    ) -> None:
        self.theta = theta
        self.start = start
        self.direction = direction

    def transform(self, data: Any, ax: Axes) -> Any:
        """Apply polar coordinate settings to the axes."""
        ax.set_theta_offset(self.start)
        ax.set_theta_direction(self.direction)
        return data


def coord_polar(theta: str = "x", start: float = 0, direction: int = 1) -> CoordPolar:
    """Create a polar coordinate system."""
    return CoordPolar(theta=theta, start=start, direction=direction)
