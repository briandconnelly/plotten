"""Reversed and sqrt scales."""

import polars as pl

from plotten import (
    aes,
    geom_point,
    ggplot,
    labs,
    scale_x_reverse,
    scale_y_sqrt,
    theme_bw,
)
from plotten._composition import plot_grid

df = pl.DataFrame(
    {
        "depth_m": [10, 50, 100, 200, 500, 1000, 2000, 4000],
        "temperature_c": [22.0, 18.0, 12.0, 8.0, 4.5, 3.0, 2.0, 1.5],
    }
)

p1 = (
    ggplot(df, aes(x="depth_m", y="temperature_c"))
    + geom_point(size=60, color="#0571B0")
    + scale_x_reverse()
    + labs(
        title="Ocean Temperature Profile",
        subtitle="X axis reversed: surface on the right",
        x="Depth (m)",
        y="Temperature (\u00b0C)",
    )
    + theme_bw()
)

df2 = pl.DataFrame(
    {
        "area_km2": [1, 10, 100, 500, 1000, 5000, 10000, 50000],
        "species": [5, 15, 45, 90, 130, 250, 340, 550],
    }
)

p2 = (
    ggplot(df2, aes(x="area_km2", y="species"))
    + geom_point(size=60, color="#CA0020")
    + scale_y_sqrt()
    + labs(
        title="Species-Area Relationship",
        subtitle="Y axis uses square root scale",
        x="Island Area (km\u00b2)",
        y="Number of Species",
    )
    + theme_bw()
)

grid = plot_grid(p1, p2)
grid.save("examples/output/reversed_scales.png", dpi=200)
