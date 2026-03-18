from __future__ import annotations


class PositionFill:
    """Stack and normalize to [0, 1]."""

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

        # First pass: compute totals per x
        totals: dict = {}
        for x, y in zip(xs, ys, strict=True):
            totals[x] = totals.get(x, 0.0) + y

        # Second pass: stack and normalize
        cumulative: dict = {}
        new_y = list(ys)
        new_ymin = [0.0] * len(ys)

        for i, (x, y, _g) in enumerate(zip(xs, ys, groups, strict=True)):
            total = totals[x] if totals[x] != 0 else 1.0
            base = cumulative.get(x, 0.0)
            new_ymin[i] = base / total
            new_y[i] = (base + y) / total
            cumulative[x] = base + y

        result = dict(data)
        result["y"] = new_y
        result["ymin"] = new_ymin
        return result


def position_fill() -> PositionFill:
    return PositionFill()
