from __future__ import annotations

from typing import Any, cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatDensity:
    """Compute kernel density estimate.

    Computed Variables
    ------------------
    y
        Density estimate at each x position.
    """

    required_aes: frozenset[str] = frozenset({"x"})

    def __init__(
        self,
        n_points: int = 200,
        bw_method: str | float | None = None,
        bw_adjust: float = 1.0,
    ) -> None:
        self._n_points = n_points
        self._bw_method = bw_method
        self._bw_adjust = bw_adjust

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        from scipy.stats import gaussian_kde

        frame = cast("nw.DataFrame", nw.from_native(df))
        x_arr = frame.get_column("x").cast(nw.Float64).to_numpy()

        has_color = "color" in frame.columns
        if has_color:
            # Shared x grid across all groups
            global_min = float(x_arr.min())
            global_max = float(x_arr.max())
            pad = (global_max - global_min) * 0.1
            x_grid = np.linspace(global_min - pad, global_max + pad, self._n_points)

            result_x: list[float] = []
            result_y: list[float] = []
            result_color: list[Any] = []

            for (group_label,), group in sorted(frame.group_by("color"), key=lambda t: str(t[0])):
                vals = group.get_column("x").cast(nw.Float64).to_numpy()
                kde = gaussian_kde(vals, bw_method=self._bw_method)
                if self._bw_adjust != 1.0:
                    kde.set_bandwidth(kde.factor * self._bw_adjust)
                density = kde(x_grid)
                result_x.extend(x_grid.tolist())
                result_y.extend(density.tolist())
                result_color.extend([group_label] * len(x_grid))

            result_dict: dict[str, Any] = {
                "x": result_x,
                "y": result_y,
                "color": result_color,
            }
        else:
            x_min = float(x_arr.min())
            x_max = float(x_arr.max())
            pad = (x_max - x_min) * 0.1
            x_grid = np.linspace(x_min - pad, x_max + pad, self._n_points)
            kde = gaussian_kde(x_arr, bw_method=self._bw_method)
            if self._bw_adjust != 1.0:
                kde.set_bandwidth(kde.factor * self._bw_adjust)
            density = kde(x_grid)
            result_dict = {
                "x": x_grid.tolist(),
                "y": density.tolist(),
            }

        return nw.to_native(nw.from_dict(result_dict, backend=nw.get_native_namespace(frame)))
