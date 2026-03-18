from __future__ import annotations

from typing import Any

import narwhals as nw
import numpy as np

from plotten.stats._base import StatBase


class StatBin(StatBase):
    """Bin continuous x into intervals and count per bin."""

    required_aes: frozenset[str] = frozenset({"x"})

    def __init__(self, bins: int = 30) -> None:
        self.bins = bins

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_values = frame.get_column("x").to_list()
        xmin, xmax = min(x_values), max(x_values)

        edges = np.linspace(xmin, xmax, self.bins + 1)
        counts, _ = np.histogram(x_values, bins=edges)
        centers = ((edges[:-1] + edges[1:]) / 2).tolist()

        native = nw.to_native(frame)
        result_dict = {"x": centers, "y": counts.tolist()}

        # Build result in same backend as input
        result = nw.from_native(native).__class__.__module__
        if "polars" in str(type(native)):
            import polars as pl
            return pl.DataFrame(result_dict)
        else:
            import pandas as pd
            return pd.DataFrame(result_dict)
