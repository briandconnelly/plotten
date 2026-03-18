"""Plot composition using | and / operators, plot_grid, and annotations."""

import polars as pl

from plotten import (
    aes,
    geom_bar,
    geom_histogram,
    geom_point,
    ggplot,
    labs,
    plot_annotation,
    plot_grid,
    scale_color_continuous,
)

# Create sample datasets
scatter_df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y": [2.1, 4.3, 3.2, 5.8, 7.1, 6.5, 8.9, 9.2, 10.1, 11.5],
        "size": [10, 20, 15, 25, 30, 22, 35, 40, 28, 45],
    }
)

hist_df = pl.DataFrame({"values": [1, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10] * 3})

bar_df = pl.DataFrame({"category": ["A", "B", "C", "D", "A", "B", "C", "A", "B", "A"]})

# Individual plots
p1 = (
    ggplot(scatter_df, aes(x="x", y="y", color="size"))
    + geom_point(size=60)
    + scale_color_continuous(cmap="viridis")
    + labs(title="Scatter", x="X", y="Y")
)

p2 = ggplot(hist_df, aes(x="values")) + geom_histogram(bins=8) + labs(title="Histogram", x="Value")

p3 = ggplot(bar_df, aes(x="category")) + geom_bar() + labs(title="Bar Chart", x="Category")

# Side-by-side with | operator
grid_h = p1 | p2
grid_h.save("examples/output/composition_horizontal.png", dpi=200)

# Stacked with / operator
grid_v = p1 / p2
grid_v.save("examples/output/composition_vertical.png", dpi=200)

# Nested: two on top, one on bottom
grid_nested = (p1 | p2) / p3
grid_nested.save("examples/output/composition_nested.png", dpi=200)

# plot_grid with annotation
grid_annotated = plot_grid(p1, p2, p3, ncol=2) + plot_annotation(
    title="Dashboard Overview",
    subtitle="Three different chart types",
    caption="Source: sample data",
    tag_levels="A",
)
grid_annotated.save("examples/output/composition_annotated.png", dpi=200)
