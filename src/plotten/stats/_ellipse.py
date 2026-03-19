"""Confidence ellipse for bivariate data."""

from __future__ import annotations

from typing import Any

import narwhals as nw
import numpy as np


class StatEllipse:
    """Compute a confidence ellipse for x, y data.

    Uses the Pearson correlation and chi-squared distribution to compute
    the ellipse boundary at a given confidence level.
    """

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(self, level: float = 0.95, segments: int = 51) -> None:
        self.level = level
        self.segments = segments

    def compute(self, df: Any) -> Any:
        frame = nw.from_native(df)
        x = np.array(frame.get_column("x").to_list(), dtype=float)
        y = np.array(frame.get_column("y").to_list(), dtype=float)

        if len(x) < 3:
            # Not enough data for an ellipse
            result = {"x": [], "y": []}
            return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))

        # Compute covariance matrix
        cov = np.cov(x, y)
        mean_x, mean_y = np.mean(x), np.mean(y)

        # Eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov)

        # Chi-squared critical value for 2 degrees of freedom
        from scipy.stats import chi2

        chi2_val = chi2.ppf(self.level, 2)

        # Ellipse radii
        radii = np.sqrt(eigenvalues * chi2_val)

        # Generate ellipse points
        theta = np.linspace(0, 2 * np.pi, self.segments)
        ellipse = np.column_stack([np.cos(theta), np.sin(theta)])

        # Scale and rotate
        ellipse = ellipse * radii
        ellipse = ellipse @ eigenvectors.T

        # Translate to mean
        ex = (ellipse[:, 0] + mean_x).tolist()
        ey = (ellipse[:, 1] + mean_y).tolist()

        result = {"x": ex, "y": ey}
        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
