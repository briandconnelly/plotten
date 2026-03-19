"""Controlling axis padding with the expand parameter."""

import polars as pl

from plotten import (
    aes,
    geom_bar,
    geom_point,
    ggplot,
    labs,
    scale_x_continuous,
    scale_x_discrete,
    scale_y_continuous,
    theme_minimal,
)

# Continuous scale: expand=(mult, add) controls padding around data range
df = pl.DataFrame({"x": [1, 2, 3, 4, 5], "y": [10, 25, 18, 30, 22]})

tight = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=4)
    + scale_x_continuous(expand=(0, 0))
    + scale_y_continuous(expand=(0, 0))
    + labs(title="No Padding", subtitle="expand=(0, 0)")
    + theme_minimal()
)

spacious = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=4)
    + scale_x_continuous(expand=(0.1, 1))
    + scale_y_continuous(expand=(0.1, 2))
    + labs(title="Extra Padding", subtitle="expand=(0.1, 1) / (0.1, 2)")
    + theme_minimal()
)

# Discrete scale: default expand=(0, 0.6) gives bar-friendly spacing
categories = pl.DataFrame({"category": ["A", "B", "C", "D"], "value": [30, 50, 20, 45]})

default_discrete = (
    ggplot(categories, aes(x="category", y="value"))
    + geom_bar()
    + labs(title="Default Discrete", subtitle="expand=(0, 0.6)")
    + theme_minimal()
)

wide_discrete = (
    ggplot(categories, aes(x="category", y="value"))
    + geom_bar()
    + scale_x_discrete(expand=(0, 1.2))
    + labs(title="Wider Discrete", subtitle="expand=(0, 1.2)")
    + theme_minimal()
)

grid = (tight | spacious) / (default_discrete | wide_discrete)
grid.save("examples/output/expand_scales.png", dpi=200)
