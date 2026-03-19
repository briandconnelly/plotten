from __future__ import annotations

from typing import Any


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

    def transform(self, data: Any, ax: Any) -> Any:
        """Apply polar coordinate settings to the axes."""
        ax.set_theta_offset(self.start)
        ax.set_theta_direction(self.direction)
        return data

    def transform_data(self, data: dict[str, Any], scales: dict) -> dict[str, Any]:
        """Convert x/y data to theta/r for polar coordinates.

        For discrete theta scales, map category indices to evenly-spaced angles.
        For continuous theta data, pass values through as-is (matplotlib polar
        projection treats x as theta in radians natively).
        When theta="y", swap x and y so matplotlib gets theta in x and r in y.
        """
        import numpy as np

        data = dict(data)
        theta_aes = self.theta

        theta_vals = data.get(theta_aes)
        if theta_vals is None:
            return data

        theta_vals = np.asarray(theta_vals, dtype=float)

        # Discrete: map category indices to evenly-spaced angles around the circle
        from plotten.scales._position import ScaleDiscrete

        if theta_aes in scales and isinstance(scales[theta_aes], ScaleDiscrete):
            n = len(scales[theta_aes]._levels)
            if n > 0:
                theta_vals = theta_vals * 2 * np.pi / n
            data[theta_aes] = theta_vals.tolist()

        # When theta="y", polar projection expects theta=x, r=y — swap
        if theta_aes == "y" and "x" in data and "y" in data:
            data["x"], data["y"] = data["y"], data["x"]

        return data


def coord_polar(theta: str = "x", start: float = 0, direction: int = 1) -> CoordPolar:
    """Create a polar coordinate system."""
    return CoordPolar(theta=theta, start=start, direction=direction)
