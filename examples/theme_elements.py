"""Theme element system for fine-grained plot control using theme()."""

import polars as pl

from plotten import (
    aes,
    element_blank,
    element_line,
    element_text,
    geom_point,
    ggplot,
    labs,
    theme,
    theme_bw,
)
from plotten._composition import plot_grid

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [3, 7, 4, 8, 5, 9, 6, 10],
    }
)

# Use theme() convenience function instead of Theme() constructor
p1 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#2171B5")
    + labs(title="Custom Title Styling")
    + theme(
        plot_title=element_text(size=20, color="#2171B5"),
        panel_grid_major=element_line(color="#DEEBF7", size=1.0),
        panel_grid_minor=element_blank(),
        panel_background="#F7FBFF",
    )
)

p2 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#E6550D")
    + labs(title="Suppressed Grid")
    + theme_bw()
    + theme(
        plot_title=element_text(size=20, color="#E6550D"),
        panel_grid_major=element_blank(),
        panel_grid_minor=element_blank(),
        panel_background="#FFF5EB",
    )
)

grid = plot_grid(p1, p2)
grid.save("examples/output/theme_elements.png", dpi=200)
