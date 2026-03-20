from __future__ import annotations


class PositionDodge2:
    """Dodge overlapping objects side-by-side with padding between groups."""

    def __init__(self, width: float = 0.9, padding: float = 0.1) -> None:
        self.width = width
        self.padding = padding

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

        group_index = {g: i for i, g in enumerate(unique_groups)}
        # Each element gets width * (1 - padding) / n_groups
        element_width = self.width * (1 - self.padding) / n_groups
        # Total span occupied by all elements (without outer gaps)
        total_span = element_width * n_groups

        new_x = []
        for x_val, g in zip(data["x"], groups, strict=True):
            idx = group_index[g]
            offset = (idx - (n_groups - 1) / 2) * (total_span / n_groups)
            new_x.append(x_val + offset)

        result = dict(data)
        result["x"] = new_x
        params["width"] = element_width
        return result


def position_dodge2(width: float = 0.9, padding: float = 0.1) -> PositionDodge2:
    """Dodge overlapping objects side-by-side with padding between groups.

    Parameters
    ----------
    width : float
        Total width allocated for all dodged elements at each x position.
    padding : float
        Fraction of the element width reserved as padding between groups.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotten import ggplot, aes, geom_boxplot
    >>> from plotten.positions import position_dodge2
    >>> df = pd.DataFrame({"x": ["a", "a", "b", "b"], "y": [1, 2, 3, 4], "g": ["m", "n", "m", "n"]})
    >>> ggplot(df, aes(x="x", y="y", fill="g")) + geom_boxplot(position=position_dodge2(padding=0.2))
    """
    return PositionDodge2(width=width, padding=padding)
