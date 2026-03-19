from __future__ import annotations

from typing import Any, cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatDensity:
    """Compute kernel density estimate."""

    required_aes: frozenset[str] = frozenset({"x"})

    def __init__(self, n_points: int = 200) -> None:
        self._n_points = n_points

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        from scipy.stats import gaussian_kde

        frame = cast("nw.DataFrame", nw.from_native(df))
        x_vals = frame.get_column("x").to_list()
        x_arr = np.array(x_vals, dtype=float)

        has_color = "color" in frame.columns
        if has_color:
            color_vals = frame.get_column("color").to_list()
            # Group by color
            groups: dict[Any, list[float]] = {}
            for xv, cv in zip(x_arr, color_vals, strict=True):
                groups.setdefault(cv, []).append(float(xv))

            # Shared x grid across all groups
            global_min = float(x_arr.min())
            global_max = float(x_arr.max())
            pad = (global_max - global_min) * 0.1
            x_grid = np.linspace(global_min - pad, global_max + pad, self._n_points)

            result_x: list[float] = []
            result_y: list[float] = []
            result_color: list[Any] = []

            for group_label in sorted(groups):
                vals = np.array(groups[group_label])
                kde = gaussian_kde(vals)
                density = kde(x_grid)
                result_x.extend(x_grid.tolist())
                result_y.extend(density.tolist())
                result_color.extend([group_label] * len(x_grid))

            result: dict[str, list] = {
                "x": result_x,
                "y": result_y,
                "color": result_color,
            }
        else:
            x_min = float(x_arr.min())
            x_max = float(x_arr.max())
            pad = (x_max - x_min) * 0.1
            x_grid = np.linspace(x_min - pad, x_max + pad, self._n_points)
            kde = gaussian_kde(x_arr)
            density = kde(x_grid)
            result = {
                "x": x_grid.tolist(),
                "y": density.tolist(),
            }

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
