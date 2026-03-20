"""Integer-only breaks for count data."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    breaks_integer,
    geom_col,
    geom_point,
    ggplot,
    labs,
    scale_x_continuous,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# Count data where fractional ticks are meaningless
rng = np.random.default_rng(42)

df_counts = pl.DataFrame(
    {
        "category": ["A", "B", "C", "D", "E"],
        "count": [2, 5, 3, 7, 1],
    }
)

# Default breaks may produce fractional ticks like 1.5, 2.5
p_default = (
    ggplot(df_counts, aes(x="category", y="count"))
    + geom_col(fill="#636363", alpha=0.8)
    + labs(title="Default Breaks", subtitle="May show 1.5, 2.5, ...", x="Category", y="Count")
    + theme_minimal()
)

# breaks_integer ensures whole numbers only
p_integer = (
    ggplot(df_counts, aes(x="category", y="count"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + scale_y_continuous(breaks=breaks_integer(5))
    + labs(title="breaks_integer(5)", subtitle="Only whole numbers", x="Category", y="Count")
    + theme_minimal()
)

# Scatter plot with integer axes
df_discrete = pl.DataFrame(
    {
        "bedrooms": rng.integers(1, 6, 60).tolist(),
        "bathrooms": rng.integers(1, 4, 60).tolist(),
    }
)

p_scatter_default = (
    ggplot(df_discrete, aes(x="bedrooms", y="bathrooms"))
    + geom_point(alpha=0.5, color="#636363", size=40)
    + labs(title="Default Breaks", x="Bedrooms", y="Bathrooms")
    + theme_minimal()
)

p_scatter_int = (
    ggplot(df_discrete, aes(x="bedrooms", y="bathrooms"))
    + geom_point(alpha=0.5, color="#E6550D", size=40)
    + scale_x_continuous(breaks=breaks_integer())
    + scale_y_continuous(breaks=breaks_integer())
    + labs(title="breaks_integer()", x="Bedrooms", y="Bathrooms")
    + theme_minimal()
)

grid = plot_grid(p_default, p_integer, p_scatter_default, p_scatter_int, ncol=2)
grid.save("examples/output/breaks_integer.png", dpi=200)
