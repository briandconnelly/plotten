from __future__ import annotations


class PositionDodge:
    """Dodge overlapping objects side-by-side."""

    def __init__(self, width: float = 0.9) -> None:
        self.width = width

    def adjust(self, data: dict, params: dict) -> dict:
        if "x" not in data:
            return data

        # Detect groups from fill, color, or group
        group_key = None
        for key in ("fill", "color", "group"):
            if key in data and isinstance(data[key], list):
                group_key = key
                break

        if group_key is None:
            return data

        groups = data[group_key]
        unique_groups = sorted(set(groups))
        n_groups = len(unique_groups)

        if n_groups <= 1:
            return data

        group_width = self.width / n_groups

        # Build per-x-position group counts for centering
        x_vals = data["x"]
        x_groups: dict[object, set] = {}
        for x_val, g in zip(x_vals, groups, strict=True):
            x_groups.setdefault(x_val, set()).add(g)

        new_x = []
        for x_val, g in zip(x_vals, groups, strict=True):
            local_groups = sorted(x_groups[x_val])
            local_n = len(local_groups)
            local_idx = local_groups.index(g)
            offset = (local_idx - (local_n - 1) / 2) * group_width
            new_x.append(x_val + offset)

        result = dict(data)
        result["x"] = new_x
        params["width"] = group_width
        return result


def position_dodge(width: float = 0.9) -> PositionDodge:
    """Dodge overlapping objects side-by-side.

    Parameters
    ----------
    width : float
        Total width allocated for all dodged elements at each x position.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_bar
    >>> from plotten.positions import position_dodge
    >>> df = pd.DataFrame({"x": ["a", "a", "b", "b"], "y": [1, 2, 3, 4], "g": ["m", "n", "m", "n"]})
    >>> ggplot(df, aes(x="x", y="y", fill="g")) + geom_bar(stat="identity", position=position_dodge())
    """
    return PositionDodge(width=width)
