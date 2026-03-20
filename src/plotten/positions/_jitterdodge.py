from __future__ import annotations

import random


class PositionJitterDodge:
    """Simultaneously dodge and jitter — useful for grouped scatter plots."""

    def __init__(
        self,
        dodge_width: float = 0.75,
        jitter_width: float = 0.1,
        jitter_height: float = 0.0,
        seed: int | None = None,
    ) -> None:
        self.dodge_width = dodge_width
        self.jitter_width = jitter_width
        self.jitter_height = jitter_height
        self.seed = seed

    def adjust(self, data: dict, params: dict) -> dict:
        if "x" not in data:
            return data

        # Detect groups from fill, color, or group
        group_key = None
        for key in ("fill", "color", "group"):
            if key in data and isinstance(data[key], list):
                group_key = key
                break

        rng = random.Random(self.seed)
        result = dict(data)

        if group_key is not None:
            groups = data[group_key]
            unique_groups = sorted(set(groups))
            n_groups = len(unique_groups)

            if n_groups > 1:
                group_index = {g: i for i, g in enumerate(unique_groups)}
                group_width = self.dodge_width / n_groups

                new_x = []
                for x_val, g in zip(data["x"], groups, strict=True):
                    idx = group_index[g]
                    dodge_offset = (idx - (n_groups - 1) / 2) * group_width
                    jitter_offset = (
                        rng.uniform(-self.jitter_width / 2, self.jitter_width / 2)
                        if self.jitter_width > 0
                        else 0.0
                    )
                    new_x.append(x_val + dodge_offset + jitter_offset)

                result["x"] = new_x
                params["width"] = group_width
            else:
                # Single group: only apply jitter to x
                if self.jitter_width > 0:
                    result["x"] = [
                        v + rng.uniform(-self.jitter_width / 2, self.jitter_width / 2)
                        for v in data["x"]
                    ]
        else:
            # No grouping: only apply jitter to x
            if self.jitter_width > 0:
                result["x"] = [
                    v + rng.uniform(-self.jitter_width / 2, self.jitter_width / 2)
                    for v in data["x"]
                ]

        # Apply jitter to y
        if "y" in data and self.jitter_height > 0:
            result["y"] = [
                v + rng.uniform(-self.jitter_height / 2, self.jitter_height / 2) for v in data["y"]
            ]

        return result


def position_jitterdodge(
    dodge_width: float = 0.75,
    jitter_width: float = 0.1,
    jitter_height: float = 0.0,
    seed: int | None = None,
) -> PositionJitterDodge:
    """Simultaneously dodge and jitter points for grouped scatter plots.

    Parameters
    ----------
    dodge_width : float
        Total width for dodging groups.
    jitter_width : float
        Amount of horizontal jitter applied after dodging.
    jitter_height : float
        Amount of vertical jitter.
    seed : int or None
        Random seed for reproducibility.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.positions import position_jitterdodge
    >>> df = pd.DataFrame({"x": ["a", "a", "b", "b"], "y": [1, 2, 3, 4], "g": ["m", "n", "m", "n"]})
    >>> ggplot(df, aes(x="x", y="y", color="g")) + geom_point(position=position_jitterdodge())
    """
    return PositionJitterDodge(
        dodge_width=dodge_width,
        jitter_width=jitter_width,
        jitter_height=jitter_height,
        seed=seed,
    )
