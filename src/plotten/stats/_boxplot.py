from __future__ import annotations

from typing import Any

import narwhals as nw
import numpy as np

from plotten.stats._base import StatBase


class StatBoxplot(StatBase):
    """Compute boxplot summary statistics grouped by x."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_vals = frame.get_column("x").to_list()
        y_vals = frame.get_column("y").to_list()

        # Group by x
        groups: dict[Any, list[float]] = {}
        for xv, yv in zip(x_vals, y_vals):
            groups.setdefault(xv, []).append(float(yv))

        result: dict[str, list] = {
            "x": [],
            "ymin": [],
            "lower": [],
            "middle": [],
            "upper": [],
            "ymax": [],
            "outliers_y": [],
        }

        for x_key in sorted(groups):
            vals = np.array(groups[x_key])
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

        # Return in same backend as input
        if "polars" in str(type(df)):
            import polars as pl

            return pl.DataFrame(result)
        else:
            import pandas as pd

            return pd.DataFrame(result)
