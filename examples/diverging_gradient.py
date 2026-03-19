"""Diverging gradient scale using scale_color_gradient2 and scale_color_gradientn."""

# Data with values centered around zero — diverging from a midpoint
import random

import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_color_gradient2,
    scale_color_gradientn,
    theme_minimal,
)

random.seed(123)
n = 100
xs = [random.gauss(0, 3) for _ in range(n)]
ys = [random.gauss(0, 3) for _ in range(n)]
vals = [x + y + random.gauss(0, 1) for x, y in zip(xs, ys, strict=True)]

df = pl.DataFrame({"x": xs, "y": ys, "value": vals})

# Diverging gradient2: blue-white-red with midpoint at 0
p1 = (
    ggplot(df, aes(x="x", y="y", color="value"))
    + geom_point(size=50, alpha=0.8)
    + scale_color_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)
    + theme_minimal()
    + labs(
        title="scale_color_gradient2",
        subtitle="Blue-White-Red diverging at 0",
        x="X",
        y="Y",
        color="Value",
    )
)

# Multi-stop gradientn: rainbow-like
p2 = (
    ggplot(df, aes(x="x", y="y", color="value"))
    + geom_point(size=50, alpha=0.8)
    + scale_color_gradientn(colors=["#440154", "#31688E", "#35B779", "#FDE725"])
    + theme_minimal()
    + labs(
        title="scale_color_gradientn",
        subtitle="Four-stop viridis-like gradient",
        x="X",
        y="Y",
        color="Value",
    )
)

grid = p1 | p2
grid.save("examples/output/diverging_gradient.png", dpi=200, width=14, height=6)
