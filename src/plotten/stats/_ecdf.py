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

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
