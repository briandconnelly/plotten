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
        x_col = frame.get_column("x")
        xmin, xmax = x_col.min(), x_col.max()

        edges = np.linspace(xmin, xmax, self.bins + 1)
        counts, _ = np.histogram(x_col.to_numpy(), bins=edges)
        centers = (edges[:-1] + edges[1:]) / 2
        widths = edges[1:] - edges[:-1]
        total = int(counts.sum())
        density = np.where((total > 0) & (widths > 0), counts / (total * widths), 0.0)

        result_dict = {
            "x": centers,
            "y": counts,
            "count": counts,
            "density": density,
            "width": widths,
        }

        return nw.to_native(nw.from_dict(result_dict, backend=nw.get_native_namespace(frame)))
