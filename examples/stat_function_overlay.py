"""Overlaying mathematical functions on scatter data with stat_function."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    stat_function,
    theme_minimal,
)

# Noisy quadratic data with a true-function overlay
rng = np.random.default_rng(7)
x = np.linspace(-3, 3, 80)
y = x**2 + rng.normal(0, 1.5, 80)

df = pl.DataFrame({"x": x.tolist(), "y": y.tolist()})

quadratic = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.4, size=2)
    + stat_function(fun=lambda t: t**2, color="red", linewidth=2)
    + labs(title="Quadratic Fit", subtitle="y = x² overlaid on noisy data", x="x", y="y")
    + theme_minimal()
)

# Multiple functions on the same plot — no data needed
trig = (
    ggplot()
    + stat_function(fun=np.sin, xlim=(0, 2 * np.pi), color="#E91E63", linewidth=1.5)
    + stat_function(fun=np.cos, xlim=(0, 2 * np.pi), color="#2196F3", linewidth=1.5)
    + stat_function(
        fun=lambda t: np.sin(t) * np.cos(t),
        xlim=(0, 2 * np.pi),
        color="#4CAF50",
        linewidth=1.5,
    )
    + labs(
        title="Trigonometric Functions",
        subtitle="sin (pink), cos (blue), sin·cos (green)",
        x="θ",
        y="f(θ)",
    )
    + theme_minimal()
)

grid = quadratic | trig
grid.save("examples/output/stat_function_overlay.png", dpi=200, width=14, height=5)
