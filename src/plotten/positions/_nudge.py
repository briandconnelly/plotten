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
    return PositionNudge(x=x, y=y)
