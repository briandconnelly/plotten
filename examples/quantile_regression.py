"""Quantile regression lines on scatter data."""

# Generate scatter data with heteroscedastic noise
import random

import polars as pl

from plotten import aes, geom_point, geom_quantile, ggplot, labs, theme_minimal

random.seed(42)
n = 80
xs = [i * 0.25 for i in range(n)]
ys = [2 + 0.5 * x + random.gauss(0, 0.5 + 0.3 * x) for x in xs]

df = pl.DataFrame({"x": xs, "y": ys})

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=20, alpha=0.4, color="#666666")
    + geom_quantile(quantiles=[0.1, 0.25, 0.5, 0.75, 0.9], alpha=0.8)
    + theme_minimal()
    + labs(
        title="Quantile Regression",
        subtitle="Lines at 10th, 25th, 50th, 75th, and 90th percentiles",
        x="X",
        y="Y",
    )
)

plot.save("examples/output/quantile_regression.png", dpi=200)
