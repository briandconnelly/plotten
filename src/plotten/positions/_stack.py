from __future__ import annotations


class PositionStack:
    """Stack overlapping objects on top of each other."""

    def adjust(self, data: dict, params: dict) -> dict:
        if "x" not in data or "y" not in data:
            return data

        # Detect groups
        group_key = None
        for key in ("fill", "color", "group"):
            if key in data and isinstance(data[key], list):
                group_key = key
                break

        if group_key is None:
            return data

        xs = data["x"]
        ys = data["y"]
        groups = data[group_key]

        # Accumulate y values per unique x
        cumulative: dict = {}
        new_y = list(ys)
        new_ymin = [0.0] * len(ys)

        for i, (x, y, _g) in enumerate(zip(xs, ys, groups, strict=True)):
            base = cumulative.get(x, 0.0)
            new_ymin[i] = base
            new_y[i] = base + y
            cumulative[x] = base + y

        result = dict(data)
        result["y"] = new_y
        result["ymin"] = new_ymin
        return result


def position_stack() -> PositionStack:
    """Stack overlapping objects on top of each other.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar
    >>> from plotten.positions import position_stack
    >>> df = pd.DataFrame({"x": ["a", "a", "b", "b"], "y": [1, 2, 3, 4], "g": ["m", "n", "m", "n"]})
    >>> ggplot(df, aes(x="x", y="y", fill="g")) + geom_bar(stat="identity", position=position_stack())
    """
    return PositionStack()
