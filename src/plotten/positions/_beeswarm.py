from __future__ import annotations

from collections import defaultdict


class PositionBeeswarm:
    """Arrange points to avoid overlap using a beeswarm layout."""

    def __init__(
        self,
        spacing: float = 0.05,
        side: str = "both",
        seed: int | None = None,
    ) -> None:
        self.spacing = spacing
        self.side = side
        self.seed = seed

    def adjust(self, data: dict, params: dict) -> dict:
        if "x" not in data or "y" not in data:
            return data

        xs = list(data["x"])
        ys = list(data["y"])
        n = len(xs)
        if n <= 1:
            return data

        # Group indices by discrete x value
        groups: dict[float, list[int]] = defaultdict(list)
        for i, xv in enumerate(xs):
            groups[xv].append(i)

        new_xs = list(xs)

        for indices in groups.values():
            if len(indices) <= 1:
                continue

            # Sort by y within group
            indices_sorted = sorted(indices, key=lambda i: ys[i])

            # Place points one by one, offsetting x to avoid vertical overlap
            placed: list[tuple[float, float]] = []  # (x_offset, y) of placed points

            for idx in indices_sorted:
                y_val = ys[idx]
                offset = 0.0

                # Find the best non-overlapping offset
                if placed:
                    offset = self._find_offset(y_val, placed)

                placed.append((offset, y_val))
                new_xs[idx] = xs[idx] + offset

        result = dict(data)
        result["x"] = new_xs
        return result

    def _find_offset(self, y: float, placed: list[tuple[float, float]]) -> float:
        """Find the smallest x offset that avoids overlap with all placed points."""
        spacing = self.spacing

        # Check if zero offset works
        if all(abs(y - py) >= spacing for _, py in placed):
            return 0.0

        # Try increasingly large offsets, alternating sides
        for step in range(1, len(placed) + 1):
            offset = step * spacing

            if self.side != "right":
                left = -offset
                if all((left - px) ** 2 + (y - py) ** 2 >= spacing**2 for px, py in placed):
                    return left

            if self.side != "left":
                right = offset
                if all((right - px) ** 2 + (y - py) ** 2 >= spacing**2 for px, py in placed):
                    return right

        # Fallback: use the next available slot
        max_offset = max(abs(px) for px, _ in placed) + spacing
        if self.side == "left":
            return -max_offset
        return max_offset


def position_beeswarm(
    spacing: float = 0.05,
    side: str = "both",
    seed: int | None = None,
) -> PositionBeeswarm:
    """Arrange points in a beeswarm layout to avoid overlap.

    Parameters
    ----------
    spacing : float
        Minimum distance between points (controls density).
    side : str
        Which side to expand towards: ``"both"``, ``"left"``, or ``"right"``.
    seed : int or None
        Random seed for reproducibility.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.positions import position_beeswarm
    >>> df = pd.DataFrame({"g": ["a"] * 5 + ["b"] * 5, "val": list(range(10))})
    >>> ggplot(df, aes(x="g", y="val")) + geom_point(position=position_beeswarm())
    """
    return PositionBeeswarm(spacing=spacing, side=side, seed=seed)
