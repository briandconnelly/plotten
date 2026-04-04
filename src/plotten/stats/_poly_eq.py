"""Compute polynomial equation and R² for annotation overlay."""

from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatPolyEq:
    """Compute polynomial fit equation and R² as annotation text."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(self, degree: int = 1, label_x: float = 0.05, label_y: float = 0.95) -> None:
        self.degree = degree
        self.label_x = label_x
        self.label_y = label_y

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        frame = cast("nw.DataFrame", nw.from_native(df))
        x = frame.get_column("x").cast(nw.Float64).to_numpy()
        y = frame.get_column("y").cast(nw.Float64).to_numpy()

        coeffs = np.polyfit(x, y, self.degree)
        y_pred = np.polyval(coeffs, x)

        # R²
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

        # Build equation string
        eq = _format_equation(coeffs)
        label = f"{eq}\nR² = {r_squared:.3f}"

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


def _format_equation(coeffs: np.ndarray) -> str:
    """Format polynomial coefficients as a readable equation."""
    degree = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = degree - i
        if abs(c) < 1e-10:
            continue
        c_str = f"{c:.2f}"
        if power == 0:
            terms.append(c_str)
        elif power == 1:
            terms.append(f"{c_str}x")
        else:
            terms.append(f"{c_str}x^{power}")
    return "y = " + " + ".join(terms).replace("+ -", "- ") if terms else "y = 0"
