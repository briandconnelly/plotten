from __future__ import annotations

from typing import Any

import narwhals as nw
import numpy as np


class StatQuantile:
    """Compute quantile regression lines.

    For each quantile, fits a simple linear quantile regression by
    minimising the weighted absolute deviation (check loss).
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        quantiles: list[float] | None = None,
        n_points: int = 100,
    ) -> None:
        self.quantiles = quantiles if quantiles is not None else [0.25, 0.5, 0.75]
        self.n_points = n_points

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x_raw = np.array(frame.get_column("x").to_list(), dtype=float)
        y_raw = np.array(frame.get_column("y").to_list(), dtype=float)

        x_pred = np.linspace(x_raw.min(), x_raw.max(), self.n_points)

        all_x: list[float] = []
        all_y: list[float] = []
        all_group: list[float] = []

        for q in self.quantiles:
            slope, intercept = self._quantile_regression(x_raw, y_raw, q)
            y_pred = slope * x_pred + intercept
            all_x.extend(x_pred.tolist())
            all_y.extend(y_pred.tolist())
            all_group.extend([q] * self.n_points)

        result = {
            "x": all_x,
            "y": all_y,
            "group": all_group,
        }

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))

    @staticmethod
    def _quantile_regression(
        x: np.ndarray, y: np.ndarray, q: float, max_iter: int = 50
    ) -> tuple[float, float]:
        """Fit a linear quantile regression using iteratively reweighted least squares.

        Minimises the check (pinball) loss: rho_q(r) = r*(q - I(r<0)).
        Uses IRLS with the check loss weights.
        """
        # Initial OLS fit
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        ss_xx = np.sum((x - x_mean) ** 2)
        if ss_xx == 0:
            return 0.0, float(np.percentile(y, q * 100))

        slope = float(np.sum((x - x_mean) * (y - y_mean)) / ss_xx)
        intercept = float(y_mean - slope * x_mean)

        # IRLS iterations
        eps = 1e-6
        for _ in range(max_iter):
            residuals = y - (slope * x + intercept)
            weights = np.where(residuals > 0, q, 1 - q) / np.maximum(np.abs(residuals), eps)

            w_sum = np.sum(weights)
            wx_mean = np.sum(weights * x) / w_sum
            wy_mean = np.sum(weights * y) / w_sum

            ss_wxx = np.sum(weights * (x - wx_mean) ** 2)
            if ss_wxx < eps:
                break
            new_slope = float(np.sum(weights * (x - wx_mean) * (y - wy_mean)) / ss_wxx)
            new_intercept = float(wy_mean - new_slope * wx_mean)

            if abs(new_slope - slope) < eps and abs(new_intercept - intercept) < eps:
                slope, intercept = new_slope, new_intercept
                break
            slope, intercept = new_slope, new_intercept

        return slope, intercept
