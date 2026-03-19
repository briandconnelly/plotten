"""Polynomial regression with equation overlay."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    stat_poly_eq,
    theme_minimal,
)

rng = np.random.default_rng(42)
x = np.linspace(0, 10, 80)
y = 0.5 * x**2 - 3 * x + 10 + rng.normal(0, 3, len(x))
df = pd.DataFrame({"x": x, "y": y})

p = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5)
    + geom_smooth(method="poly", degree=2, color="red")
    + stat_poly_eq(degree=2)
    + labs(
        title="Polynomial Regression",
        subtitle="Quadratic fit with R\u00b2 annotation",
        x="Predictor",
        y="Response",
    )
    + theme_minimal()
)

p.save("examples/output/polynomial_smooth.png", width=8, height=6)
