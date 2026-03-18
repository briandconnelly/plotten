from __future__ import annotations

from typing import Any

import narwhals as nw
import numpy as np


class StatECDF:
    """Compute empirical cumulative distribution function."""

    required_aes: frozenset[str] = frozenset({"x"})

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_vals = frame.get_column("x").to_list()
        x_arr = np.array(x_vals, dtype=float)
        sorted_x = np.sort(x_arr)
        n = len(sorted_x)
        y = np.arange(1, n + 1) / n

        result = {
            "x": sorted_x.tolist(),
            "y": y.tolist(),
        }

        if "polars" in str(type(df)):
            import polars as pl

            return pl.DataFrame(result)
        else:
            import pandas as pd

            return pd.DataFrame(result)
