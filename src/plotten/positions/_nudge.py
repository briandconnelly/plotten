from __future__ import annotations


class PositionNudge:
    """Shift all x and/or y values by a fixed amount."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y

    def adjust(self, data: dict, params: dict) -> dict:
        result = dict(data)
        if "x" in data and self.x != 0:
            result["x"] = [v + self.x for v in data["x"]]
        if "y" in data and self.y != 0:
            result["y"] = [v + self.y for v in data["y"]]
        return result


def position_nudge(x: float = 0, y: float = 0) -> PositionNudge:
    """Shift all positions by a fixed offset.

    Parameters
    ----------
    x : float
        Horizontal offset to add to each x value.
    y : float
        Vertical offset to add to each y value.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_point, geom_text
    >>> from plotten.positions import position_nudge
    >>> df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6], "lab": ["a", "b", "c"]})
    >>> (ggplot(df, aes(x="x", y="y"))
    ...  + geom_point()
    ...  + geom_text(aes(label="lab"), position=position_nudge(y=0.3)))
    """
    return PositionNudge(x=x, y=y)
