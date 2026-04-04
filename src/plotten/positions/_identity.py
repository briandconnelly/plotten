from __future__ import annotations


class PositionIdentity:
    """No position adjustment — returns data unchanged."""

    def __repr__(self) -> str:
        return "PositionIdentity()"

    def adjust(self, data: dict, params: dict) -> dict:
        return data


def position_identity() -> PositionIdentity:
    """Keep data positions unchanged (the default for most geoms).

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point
    >>> from plotten.positions import position_identity
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    >>> ggplot(df, aes(x="x", y="y")) + geom_point(position=position_identity())
    """
    return PositionIdentity()
