"""Pretty breaks for clean, human-readable tick positions."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    breaks_pretty,
    geom_point,
    ggplot,
    labs,
    scale_x_continuous,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

rng = np.random.default_rng(42)

df = pl.DataFrame(
    {
        "x": rng.uniform(0.3, 97.2, 80).tolist(),
        "y": rng.uniform(0.1, 4.7, 80).tolist(),
    }
)

# Default matplotlib breaks vs breaks_pretty
default = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5, color="#636363")
    + labs(title="Default Breaks", x="Value", y="Score")
    + theme_minimal()
)

pretty = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5, color="#2171B5")
    + scale_x_continuous(breaks=breaks_pretty(5))
    + scale_y_continuous(breaks=breaks_pretty(5))
    + labs(title="breaks_pretty(5)", x="Value", y="Score")
    + theme_minimal()
)

dense = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5, color="#E6550D")
    + scale_x_continuous(breaks=breaks_pretty(10))
    + scale_y_continuous(breaks=breaks_pretty(10))
    + labs(title="breaks_pretty(10)", x="Value", y="Score")
    + theme_minimal()
)

sparse = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.5, color="#31A354")
    + scale_x_continuous(breaks=breaks_pretty(3))
    + scale_y_continuous(breaks=breaks_pretty(3))
    + labs(title="breaks_pretty(3)", x="Value", y="Score")
    + theme_minimal()
)

grid = plot_grid(default, pretty, dense, sparse, ncol=2)
grid.save("examples/output/breaks_pretty.png", dpi=200)
