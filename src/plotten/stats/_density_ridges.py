"""Density computation for ridge plots."""

from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatDensityRidges:
    """Compute density for each group, offset vertically by group index."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        bandwidth: float | None = None,
        n_points: int = 128,
        bw_adjust: float = 1.0,
    ) -> None:
        self.bandwidth = bandwidth
        self.n_points = n_points
        self.bw_adjust = bw_adjust

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        x_vals = frame.get_column("x").to_list()
        y_groups = frame.get_column("y").to_list()

        unique_groups = sorted(set(y_groups), key=lambda g: str(g))
        group_map = {g: i for i, g in enumerate(unique_groups)}

        result_x: list[float] = []
        result_ymin: list[float] = []
        result_ymax: list[float] = []
        result_group: list = []

        for group in unique_groups:
            group_x = np.array(
                [x for x, g in zip(x_vals, y_groups, strict=True) if g == group],
                dtype=float,
            )
            if len(group_x) < 2:
                continue

            baseline = float(group_map[group])

            # KDE using simple Gaussian kernel
            x_grid = np.linspace(group_x.min(), group_x.max(), self.n_points)
            density = self._kde(group_x, x_grid)

            # Scale density to a reasonable height (max ~0.8 of gap between groups)
            max_d = density.max()
            if max_d > 0:
                density = density / max_d * 0.8

            result_x.extend(x_grid.tolist())
            result_ymin.extend([baseline] * len(x_grid))
            result_ymax.extend((baseline + density).tolist())
            result_group.extend([group] * len(x_grid))

        result = {
            "x": result_x,
            "ymin": result_ymin,
            "ymax": result_ymax,
            "group": result_group,
        }
        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))

    def _kde(self, data: np.ndarray, x_grid: np.ndarray) -> np.ndarray:
        """Simple Gaussian KDE."""
        n = len(data)
        if self.bandwidth is not None:
            bw = self.bandwidth
        else:
            # Silverman's rule of thumb
            std = np.std(data, ddof=1) if n > 1 else 1.0
            bw = 1.06 * std * n ** (-0.2)
            bw = max(bw, 1e-6)

        bw *= self.bw_adjust

        density = np.zeros_like(x_grid)
        for xi in data:
            density += np.exp(-0.5 * ((x_grid - xi) / bw) ** 2)
        density /= n * bw * np.sqrt(2 * np.pi)
        return density
