"""Comparing scale_size_area() vs scale_radius() sizing."""

import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_radius,
    scale_size_area,
    theme,
    theme_minimal,
    ylim,
)

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5],
        "y": [1, 1, 1, 1, 1],
        "value": [0, 25, 50, 75, 100],
    }
)

# scale_size_area: area proportional to value, 0 always maps to 0
area = (
    ggplot(df, aes(x="x", y="y", size="value"))
    + geom_point(alpha=0.5, color="steelblue")
    + scale_size_area(max_size=600)
    + ylim(0, 2)
    + labs(
        title="scale_size_area()",
        subtitle="Area proportional to value; 0 maps to size 0",
    )
    + theme_minimal()
    + theme(legend_position="none")
)

# scale_radius: radius proportional to value (linear mapping)
radius = (
    ggplot(df, aes(x="x", y="y", size="value"))
    + geom_point(alpha=0.5, color="coral")
    + scale_radius(range=(1, 600))
    + ylim(0, 2)
    + labs(
        title="scale_radius()",
        subtitle="Radius proportional to value (linear mapping)",
    )
    + theme_minimal()
    + theme(legend_position="none")
)

grid = area | radius
grid.save("examples/output/scale_radius.png", dpi=200)
