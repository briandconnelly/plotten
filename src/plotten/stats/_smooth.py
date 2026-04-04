from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np

from plotten._enums import SmoothMethod


class StatSmooth:
    """Compute a smooth fit line with optional confidence interval.

    Computed Variables
    ------------------
    y
        Fitted values along the smooth line.
    ymin
        Lower bound of the confidence interval.
    ymax
        Upper bound of the confidence interval.
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        method: str = "loess",
        span: float = 0.75,
        se: bool = True,
        n_points: int = 80,
        degree: int = 2,
    ) -> None:
        self.method = method
        self.span = span
        self.se = se
        self.n_points = n_points
        self.degree = degree

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        x_raw = frame.get_column("x").cast(nw.Float64).to_numpy()
        y_raw = frame.get_column("y").cast(nw.Float64).to_numpy()

        # Sort by x
        order = np.argsort(x_raw)
        x_sorted = x_raw[order]
        y_sorted = y_raw[order]

        x_pred = np.linspace(x_sorted.min(), x_sorted.max(), self.n_points)

        match self.method:
            case SmoothMethod.OLS | "lm":
                y_pred, ymin, ymax = self._ols(x_sorted, y_sorted, x_pred)
            case SmoothMethod.LOESS:
                y_pred, ymin, ymax = self._loess(x_sorted, y_sorted, x_pred)
            case SmoothMethod.MOVING_AVERAGE:
                y_pred, ymin, ymax = self._moving_average(x_sorted, y_sorted, x_pred)
            case SmoothMethod.POLY:
                y_pred, ymin, ymax = self._poly(x_sorted, y_sorted, x_pred)
            case _:
                from plotten._validation import StatError

                msg = (
                    f"Unknown smoothing method: {self.method!r}. "
                    f"Valid methods: 'ols' (or 'lm'), 'loess', 'moving_average', 'poly'."
                )
                raise StatError(msg)

        if not self.se:
            ymin = y_pred.copy()
            ymax = y_pred.copy()

        result = {
            "x": x_pred.tolist(),
            "y": y_pred.tolist(),
            "ymin": ymin.tolist(),
            "ymax": ymax.tolist(),
        }

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))

    def _ols(
        self, x: np.ndarray, y: np.ndarray, x_pred: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        coeffs = np.polyfit(x, y, 1)
        y_pred = np.polyval(coeffs, x_pred)
        # SE from residuals
        residuals = y - np.polyval(coeffs, x)
        se = np.sqrt(np.sum(residuals**2) / (len(y) - 2))
        x_mean = np.mean(x)
        x_ss = np.sum((x - x_mean) ** 2)
        se_pred = se * np.sqrt(1 / len(y) + (x_pred - x_mean) ** 2 / x_ss)
        ymin = y_pred - 1.96 * se_pred
        ymax = y_pred + 1.96 * se_pred
        return y_pred, ymin, ymax

    def _loess(
        self, x: np.ndarray, y: np.ndarray, x_pred: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        try:
            from scipy.interpolate import UnivariateSpline
        except ImportError:
            msg = "LOESS smoothing requires scipy. Install it with: uv add plotten[scipy]"
            raise ImportError(msg) from None

        # Use a smoothing spline as LOESS approximation
        # s parameter controls smoothness — higher = smoother
        n = len(x)
        s_param = n * self.span
        spline = UnivariateSpline(x, y, s=s_param)
        y_pred = spline(x_pred)

        # Estimate SE from residuals
        residuals = y - spline(x)
        se = np.sqrt(np.mean(residuals**2))
        ymin = y_pred - 1.96 * se
        ymax = y_pred + 1.96 * se
        return y_pred, ymin, ymax

    def _moving_average(
        self, x: np.ndarray, y: np.ndarray, x_pred: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        window = max(1, int(self.span * len(y)))
        # For each x_pred point, find nearest window of data
        y_pred = np.empty_like(x_pred)
        for i, xp in enumerate(x_pred):
            dists = np.abs(x - xp)
            nearest_idx = np.argsort(dists)[:window]
            y_pred[i] = np.mean(y[nearest_idx])

        ymin = y_pred.copy()
        ymax = y_pred.copy()
        return y_pred, ymin, ymax

    def _poly(
        self, x: np.ndarray, y: np.ndarray, x_pred: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        coeffs = np.polyfit(x, y, self.degree)
        y_pred = np.polyval(coeffs, x_pred)
        # SE from residuals
        residuals = y - np.polyval(coeffs, x)
        n = len(y)
        p = self.degree + 1
        se = np.sqrt(np.sum(residuals**2) / max(n - p, 1))
        x_mean = np.mean(x)
        x_ss = np.sum((x - x_mean) ** 2)
        se_pred = se * np.sqrt(1 / n + (x_pred - x_mean) ** 2 / x_ss)
        ymin = y_pred - 1.96 * se_pred
        ymax = y_pred + 1.96 * se_pred
        return y_pred, ymin, ymax
