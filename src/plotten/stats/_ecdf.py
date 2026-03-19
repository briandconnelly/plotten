from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatECDF:
    """Compute empirical cumulative distribution function."""

    required_aes: frozenset[str] = frozenset({"x"})

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))

        # Sort x using narwhals, extract as numpy for precise ECDF computation
        sorted_frame = frame.select(nw.col("x").cast(nw.Float64)).sort("x")
        sorted_x = sorted_frame.get_column("x").to_list()
        n = len(sorted_x)
        y = (np.arange(1, n + 1) / n).tolist()

        result = nw.from_dict(
            {"x": sorted_x, "y": y},
            backend=nw.get_native_namespace(frame),
        )
        return nw.to_native(result)
