"""Coordinate transformations — visual axis warping."""

import numpy as np
import pandas as pd

from plotten import (
    aes,
    coord_trans,
    geom_point,
    ggplot,
    labs,
    plot_annotation,
    plot_grid,
    theme_minimal,
)

rng = np.random.default_rng(42)
df = pd.DataFrame(
    {
        "x": rng.uniform(1, 100, 150),
        "y": rng.uniform(1, 1000, 150),
    }
)

p1 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.4)
    + coord_trans()
    + labs(title="Identity (no transform)")
    + theme_minimal()
)

p2 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.4)
    + coord_trans(x="sqrt", y="log10")
    + labs(title="sqrt(x), log10(y)")
    + theme_minimal()
)

p3 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(alpha=0.4)
    + coord_trans(y="sqrt")
    + labs(title="sqrt(y)")
    + theme_minimal()
)

grid = plot_grid(p1, p2, p3, ncol=3) + plot_annotation(title="Coordinate Transformations")
grid.save("examples/output/coord_transform.png", width=15, height=5)
