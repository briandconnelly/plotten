"""Deduplicating observations with stat_unique()."""

import numpy as np
import polars as pl

from plotten import aes, geom_point, ggplot, labs, stat_unique, theme, theme_minimal

rng = np.random.default_rng(42)

# Create data with heavy duplication on a grid
xs = np.repeat([1, 2, 3, 4, 5], 20).tolist()
ys = np.tile([1, 2, 3, 4, 5], 20).tolist()

df = pl.DataFrame({"x": xs, "y": ys})

# All 100 points plotted — overlapping makes it look like 25
all_points = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=5, alpha=0.15, color="steelblue")
    + labs(
        title="All 100 Points",
        subtitle="Heavy overlap hides the true count",
    )
    + theme_minimal()
    + theme(title_size=13)
)

# Deduplicated — only 25 unique positions drawn
unique_points = (
    ggplot(df, aes(x="x", y="y"))
    + stat_unique(size=5, color="steelblue")
    + labs(
        title="stat_unique()",
        subtitle="25 unique positions, each drawn once",
    )
    + theme_minimal()
    + theme(title_size=13)
)

grid = all_points | unique_points
grid.save("examples/output/stat_unique.png", dpi=200)
