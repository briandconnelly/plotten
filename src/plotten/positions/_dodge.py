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

        group_index = {g: i for i, g in enumerate(unique_groups)}
        group_width = self.width / n_groups

        new_x = []
        for x_val, g in zip(data["x"], groups, strict=True):
            idx = group_index[g]
            offset = (idx - (n_groups - 1) / 2) * group_width
            new_x.append(x_val + offset)

        result = dict(data)
        result["x"] = new_x
        params["width"] = group_width
        return result


def position_dodge(width: float = 0.9) -> PositionDodge:
    return PositionDodge(width=width)
