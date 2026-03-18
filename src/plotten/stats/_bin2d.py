from __future__ import annotations

from typing import Any

import narwhals as nw
import numpy as np


class StatBin2d:
    """Bin x and y into a 2D grid, output bin centers and counts."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(self, bins: int | tuple[int, int] = 30) -> None:
        self._bins = bins

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_vals = np.array(frame.get_column("x").to_list(), dtype=float)
        y_vals = np.array(frame.get_column("y").to_list(), dtype=float)

        counts, x_edges, y_edges = np.histogram2d(x_vals, y_vals, bins=self._bins)

        # Compute bin centers
        x_centers = (x_edges[:-1] + x_edges[1:]) / 2
        y_centers = (y_edges[:-1] + y_edges[1:]) / 2

        # Build output: one row per non-zero bin
        result_x: list[float] = []
        result_y: list[float] = []
        result_fill: list[float] = []

        for i in range(len(x_centers)):
            for j in range(len(y_centers)):
                if counts[i, j] > 0:
                    result_x.append(float(x_centers[i]))
                    result_y.append(float(y_centers[j]))
                    result_fill.append(float(counts[i, j]))

        result = {
            "x": result_x,
            "y": result_y,
            "fill": result_fill,
        }

        if "polars" in str(type(df)):
            import polars as pl

            return pl.DataFrame(result)
        else:
            import pandas as pd

            return pd.DataFrame(result)
