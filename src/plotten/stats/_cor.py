"""Compute correlation coefficient and p-value for annotation overlay."""

from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatCor:
    """Compute Pearson or Spearman correlation as annotation text."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(
        self,
        method: str = "pearson",
        label_x: float = 0.1,
        label_y: float = 0.9,
        digits: int = 2,
    ) -> None:
        if method not in ("pearson", "spearman"):
            msg = f"method must be 'pearson' or 'spearman', got {method!r}"
            raise ValueError(msg)
        self.method = method
        self.label_x = label_x
        self.label_y = label_y
        self.digits = digits

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        x = np.array(frame.get_column("x").to_list(), dtype=float)
        y = np.array(frame.get_column("y").to_list(), dtype=float)

        r, p = self._correlate(x, y)
        label = self._format_label(r, p)

        # Position in data coordinates (fraction of range)
        x_range = x.max() - x.min()
        y_range = y.max() - y.min()
        text_x = x.min() + self.label_x * x_range
        text_y = y.min() + self.label_y * y_range

        result = {
            "x": [text_x],
            "y": [text_y],
            "label": [label],
        }
        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))

    def _correlate(self, x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
        """Compute correlation coefficient and p-value."""
        try:
            from scipy import stats as scipy_stats
        except ImportError:
            return self._correlate_fallback(x, y)

        if self.method == "pearson":
            result = scipy_stats.pearsonr(x, y)
        else:
            result = scipy_stats.spearmanr(x, y)
        return float(result.statistic), float(result.pvalue)

    def _correlate_fallback(self, x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
        """Pure-numpy Pearson fallback (no p-value for Spearman without scipy)."""
        if self.method == "spearman":
            # Rank-transform then compute Pearson on ranks
            x = _rank(x)
            y = _rank(y)

        n = len(x)
        if n < 3:
            return 0.0, 1.0

        r = float(np.corrcoef(x, y)[0, 1])

        # Two-sided p-value via t-distribution approximation
        if abs(r) >= 1.0:
            p = 0.0
        else:
            t_stat = r * np.sqrt((n - 2) / (1 - r**2))
            # Approximate p-value using normal distribution for large n
            p = float(2.0 * _t_sf(abs(t_stat), n - 2))

        return r, p

    def _format_label(self, r: float, p: float) -> str:
        r_str = f"{r:.{self.digits}f}"
        if p < 0.001:
            p_str = "p < 0.001"
        else:
            p_str = f"p = {p:.{self.digits + 1}f}"
        prefix = "R" if self.method == "pearson" else "rho"
        return f"{prefix} = {r_str}, {p_str}"


def _rank(a: np.ndarray) -> np.ndarray:
    """Compute fractional ranks (average ties)."""
    order = a.argsort()
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(a) + 1, dtype=float)
    # Handle ties by averaging
    sorted_a = a[order]
    i = 0
    while i < len(sorted_a):
        j = i
        while j < len(sorted_a) and sorted_a[j] == sorted_a[i]:
            j += 1
        if j > i + 1:
            avg_rank = np.mean(np.arange(i + 1, j + 1, dtype=float))
            for k in range(i, j):
                ranks[order[k]] = avg_rank
        i = j
    return ranks


def _t_sf(t: float, df: int) -> float:
    """Survival function for t-distribution (approximate via beta regularized).

    Uses the relationship between the t-distribution CDF and the
    regularized incomplete beta function, approximated numerically.
    """
    # For large df, use normal approximation
    if df > 100:
        from math import erfc, sqrt

        return 0.5 * erfc(t / sqrt(2))

    # Beta incomplete function approximation via continued fraction
    x = df / (df + t**2)
    a = df / 2.0
    b = 0.5
    return 0.5 * _betai(a, b, x)


def _betai(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function I_x(a, b)."""
    from math import exp, lgamma, log

    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0

    ln_beta = lgamma(a) + lgamma(b) - lgamma(a + b)
    front = exp(log(x) * a + log(1.0 - x) * b - ln_beta)

    # Use continued fraction
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for incomplete beta function."""
    max_iter = 200
    eps = 3.0e-12
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        # Even step
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        # Odd step
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h
