from __future__ import annotations

from typing import cast

import narwhals as nw
import narwhals.typing
import numpy as np


class StatViolin:
    """Compute mirrored KDE per group for violin plots."""

    required_aes: frozenset[str] = frozenset({"x", "y"})

    def __init__(self, n_points: int = 100) -> None:
        self._n_points = n_points

    def compute(self, df: nw.typing.IntoFrame) -> nw.typing.Frame:
        from scipy.stats import gaussian_kde

        frame = cast("nw.DataFrame", nw.from_native(df))

        result: dict[str, list] = {
            "x": [],
            "y_grid": [],
            "density": [],
            "y_min": [],
            "y_max": [],
        }

        for (x_key,), group in sorted(frame.group_by("x"), key=lambda t: str(t[0])):
            vals = group.get_column("y").cast(nw.Float64).to_numpy()
            if len(vals) < 2:
                # Need at least 2 points for KDE
                result["x"].append(x_key)
                result["y_grid"].append(vals.tolist())
                result["density"].append([0.4])
                result["y_min"].append(float(vals.min()))
                result["y_max"].append(float(vals.max()))
                continue

            kde = gaussian_kde(vals)
            y_min = float(vals.min())
            y_max = float(vals.max())
            pad = (y_max - y_min) * 0.05
            y_grid = np.linspace(y_min - pad, y_max + pad, self._n_points)
            density = kde(y_grid)

            # Normalize so max half-width = 0.4
            max_density = density.max()
            if max_density > 0:
                density = density / max_density * 0.4

            result["x"].append(x_key)
            result["y_grid"].append(y_grid.tolist())
            result["density"].append(density.tolist())
            result["y_min"].append(y_min)
            result["y_max"].append(y_max)

        return nw.to_native(nw.from_dict(result, backend=nw.get_native_namespace(frame)))
