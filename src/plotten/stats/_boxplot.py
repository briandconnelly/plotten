from __future__ import annotations

from typing import Any, cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatBoxplot:
    """Compute boxplot summary statistics grouped by x."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))

        # Get unique x values sorted via narwhals
        unique_x = frame.select(nw.col("x")).unique().sort("x").get_column("x").to_list()

        result: dict[str, list[Any]] = {
            "x": [],
            "ymin": [],
            "lower": [],
            "middle": [],
            "upper": [],
            "ymax": [],
            "outliers_y": [],
        }

        for x_key in unique_x:
            group = frame.filter(nw.col("x") == x_key)
            vals = np.array(group.get_column("y").to_list(), dtype=float)

            q1 = float(np.percentile(vals, 25))
            median = float(np.percentile(vals, 50))
            q3 = float(np.percentile(vals, 75))
            iqr = q3 - q1
            whisker_lo = float(vals[vals >= q1 - 1.5 * iqr].min())
            whisker_hi = float(vals[vals <= q3 + 1.5 * iqr].max())
            outliers = vals[(vals < q1 - 1.5 * iqr) | (vals > q3 + 1.5 * iqr)]

            result["x"].append(x_key)
            result["ymin"].append(whisker_lo)
            result["lower"].append(q1)
            result["middle"].append(median)
            result["upper"].append(q3)
            result["ymax"].append(whisker_hi)
            result["outliers_y"].append(outliers.tolist())

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
