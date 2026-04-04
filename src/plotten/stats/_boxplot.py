from __future__ import annotations

from typing import Any, cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatBoxplot:
    """Compute boxplot summary statistics grouped by x.

    Computed Variables
    ------------------
    ymin
        Lower whisker (smallest value within 1.5 * IQR of Q1).
    lower
        First quartile (Q1 / 25th percentile).
    middle
        Median (Q2 / 50th percentile).
    upper
        Third quartile (Q3 / 75th percentile).
    ymax
        Upper whisker (largest value within 1.5 * IQR of Q3).
    outliers_y
        Values beyond the whiskers.
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))

        result: dict[str, list[Any]] = {
            "x": [],
            "ymin": [],
            "lower": [],
            "middle": [],
            "upper": [],
            "ymax": [],
            "outliers_y": [],
        }

        for (x_key,), group in sorted(frame.group_by("x"), key=lambda t: str(t[0])):
            vals = group.get_column("y").cast(nw.Float64).to_numpy()

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
