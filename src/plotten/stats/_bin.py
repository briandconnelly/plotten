from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatBin:
    """Bin continuous x into intervals and count per bin.

    Computed Variables
    ------------------
    count
        Number of observations in each bin.
    density
        Density estimate (count / total / bin width), integrates to 1.
    width
        Width of each bin.
    """

    required_aes: frozenset[str] = frozenset({"x"})

    def __init__(self, bins: int = 30) -> None:
        self.bins = bins

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        x_values = frame.get_column("x").to_list()
        xmin, xmax = min(x_values), max(x_values)

        edges = np.linspace(xmin, xmax, self.bins + 1)
        counts, _ = np.histogram(x_values, bins=edges)
        centers = ((edges[:-1] + edges[1:]) / 2).tolist()

        counts_list = counts.tolist()
        total = sum(counts_list)
        widths = (edges[1:] - edges[:-1]).tolist()
        density = [
            c / (total * w) if total > 0 and w > 0 else 0.0
            for c, w in zip(counts_list, widths, strict=True)
        ]

        result_dict = {
            "x": centers,
            "y": counts_list,
            "count": counts_list,
            "density": density,
            "width": widths,
        }

        return nw.to_native(nw.from_dict(result_dict, backend=nw.get_native_namespace(frame)))
