"""StatDotplot — bin x and assign stack positions."""

from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatDotplot:
    """Bin continuous x and assign stacked y positions within each bin."""

    required_aes: frozenset[str] = frozenset({"x"})

    def __init__(self, bins: int = 30) -> None:
        self.bins = bins

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        x_values = frame.get_column("x").to_list()
        xmin, xmax = min(x_values), max(x_values)

        edges = np.linspace(xmin, xmax, self.bins + 1)
        centers = ((edges[:-1] + edges[1:]) / 2).tolist()

        # Assign each point to a bin and stack
        result_x: list[float] = []
        result_y: list[int] = []
        bin_counts: dict[int, int] = {}

        for xv in x_values:
            bin_idx = int(np.searchsorted(edges[1:], xv, side="right"))
            bin_idx = min(bin_idx, len(centers) - 1)
            stack_pos = bin_counts.get(bin_idx, 0)
            bin_counts[bin_idx] = stack_pos + 1
            result_x.append(centers[bin_idx])
            result_y.append(stack_pos)

        result_dict = {"x": result_x, "y": result_y}

        return nw.to_native(nw.from_dict(result_dict, backend=nw.get_native_namespace(frame)))
