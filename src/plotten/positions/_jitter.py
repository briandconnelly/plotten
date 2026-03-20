from __future__ import annotations

import random


class PositionJitter:
    """Add random noise to x and/or y positions."""

    def __init__(self, width: float = 0.4, height: float = 0.0, seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self.seed = seed

    def adjust(self, data: dict, params: dict) -> dict:
        rng = random.Random(self.seed)

        result = dict(data)
        if "x" in data and self.width > 0:
            result["x"] = [v + rng.uniform(-self.width / 2, self.width / 2) for v in data["x"]]
        if "y" in data and self.height > 0:
            result["y"] = [v + rng.uniform(-self.height / 2, self.height / 2) for v in data["y"]]
        return result


def position_jitter(
    width: float = 0.4, height: float = 0.0, seed: int | None = None
) -> PositionJitter:
    """Add random noise to point positions to reduce overplotting.

    Parameters
    ----------
    width : float
        Amount of horizontal jitter (total spread, not half-range).
    height : float
        Amount of vertical jitter.
    seed : int or None
        Random seed for reproducibility.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.positions import position_jitter
    >>> df = pd.DataFrame({"g": ["a", "a", "b", "b"], "val": [1, 2, 3, 4]})
    >>> ggplot(df, aes(x="g", y="val")) + geom_point(position=position_jitter(width=0.2))
    """
    return PositionJitter(width=width, height=height, seed=seed)
