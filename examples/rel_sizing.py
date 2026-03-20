"""Relative sizing with rel() — scalable theme font sizes."""

import polars as pl

from plotten import (
    aes,
    element_text,
    geom_point,
    ggplot,
    labs,
    rel,
    theme,
    theme_minimal,
)

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [3, 7, 4, 8, 5, 9, 6, 10],
    }
)

# rel() makes sizes relative to the parent/default size.
# rel(1.5) = 150% of default, rel(0.8) = 80% of default.
# This makes themes composable — change the base size and everything scales.

# Example 1: Large title, small axis labels relative to defaults
p1 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#2171B5")
    + theme_minimal()
    + theme(
        plot_title=element_text(size=rel(1.8), color="#2171B5", weight="bold"),
        axis_title_x=element_text(size=rel(1.2)),
        axis_title_y=element_text(size=rel(1.2)),
        axis_text_x=element_text(size=rel(0.8)),
        axis_text_y=element_text(size=rel(0.8)),
    )
    + labs(title="rel(1.8) Title", x="rel(1.2) X Axis", y="rel(1.2) Y Axis")
)

# Example 2: Uniform scaling — everything at 70% of default
p2 = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#E6550D")
    + theme_minimal()
    + theme(
        plot_title=element_text(size=rel(0.7)),
        axis_title_x=element_text(size=rel(0.7)),
        axis_title_y=element_text(size=rel(0.7)),
        axis_text_x=element_text(size=rel(0.7)),
        axis_text_y=element_text(size=rel(0.7)),
    )
    + labs(title="Everything at rel(0.7)", x="Compact X", y="Compact Y")
)

grid = p1 | p2
grid.save("examples/output/rel_sizing.png", dpi=200)
print("Saved rel_sizing.png")
