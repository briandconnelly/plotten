from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatQQ:
    """Compute theoretical vs sample quantiles for a QQ plot."""

    required_aes: frozenset[str] = frozenset({"x"})

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        try:
            from scipy.stats import norm
        except ImportError:
            msg = "geom_qq() requires scipy. Install it with: uv add scipy"
            raise ImportError(msg) from None

        frame = cast("nw.DataFrame", nw.from_native(df))
        sample = np.sort(frame.get_column("x").cast(nw.Float64).to_numpy())
        n = len(sample)

        # Theoretical quantiles using plotting positions
        probs = (np.arange(1, n + 1) - 0.5) / n
        theoretical = norm.ppf(probs)

        result = {
            "x": theoretical.tolist(),
            "y": sample.tolist(),
        }

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))


class StatQQLine:
    """Compute the reference line for a QQ plot (through Q1 and Q3)."""

    required_aes: frozenset[str] = frozenset({"x"})

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        try:
            from scipy.stats import norm
        except ImportError:
            msg = "geom_qq_line() requires scipy. Install it with: uv add scipy"
            raise ImportError(msg) from None

        frame = cast("nw.DataFrame", nw.from_native(df))
        sample = frame.get_column("x").cast(nw.Float64).to_numpy()

        q25, q75 = np.percentile(sample, [25, 75])
        theoretical_q25 = norm.ppf(0.25)
        theoretical_q75 = norm.ppf(0.75)

        slope = (q75 - q25) / (theoretical_q75 - theoretical_q25)
        intercept = q25 - slope * theoretical_q25

        # Generate line endpoints spanning the data range
        n = len(sample)
        probs = (np.arange(1, n + 1) - 0.5) / n
        x_range = [float(norm.ppf(probs[0])), float(norm.ppf(probs[-1]))]
        y_range = [slope * x_range[0] + intercept, slope * x_range[1] + intercept]

        result = {
            "x": x_range,
            "y": y_range,
        }

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
