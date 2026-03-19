"""Segment and arrow geoms demonstrating multiple arrow styles."""

import polars as pl

from plotten import arrow, geom_point, geom_segment, ggplot, labs, theme, theme_minimal
from plotten._composition import plot_grid

# Network graph with closed arrows
nodes = pl.DataFrame(
    {
        "x": [0.0, 1.0, 2.0, 1.0, 0.5, 1.5],
        "y": [0.0, 1.0, 0.0, -1.0, 0.5, 0.5],
    }
)

edges = pl.DataFrame(
    {
        "x": [0.0, 0.0, 1.0, 1.0, 1.0, 0.5],
        "y": [0.0, 0.0, 1.0, 1.0, -1.0, 0.5],
        "xend": [1.0, 0.5, 2.0, 1.5, 2.0, 1.5],
        "yend": [1.0, 0.5, 0.0, 0.5, 0.0, 0.5],
    }
)

p1 = (
    ggplot()
    + geom_segment(
        data=edges,
        x="x",
        y="y",
        xend="xend",
        yend="yend",
        arrow=arrow(style="closed", size=1.5),
        size=1.2,
        color="#37474F",
    )
    + geom_point(data=nodes, x="x", y="y", size=120, color="#1E88E5", alpha=0.9)
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Closed Arrows", x="", y="")
)

# Same graph with open arrows (thinner, more subtle)
p2 = (
    ggplot()
    + geom_segment(
        data=edges,
        x="x",
        y="y",
        xend="xend",
        yend="yend",
        arrow=arrow(style="open"),
        size=0.8,
        color="#78909C",
    )
    + geom_point(data=nodes, x="x", y="y", size=120, color="#43A047", alpha=0.9)
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Open Arrows", x="", y="")
)

# Plain segments (no arrows)
p3 = (
    ggplot()
    + geom_segment(
        data=edges,
        x="x",
        y="y",
        xend="xend",
        yend="yend",
        size=1.5,
        color="#B0BEC5",
    )
    + geom_point(data=nodes, x="x", y="y", size=120, color="#E53935", alpha=0.9)
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Plain Segments", x="", y="")
)

grid = plot_grid(p1, p2, p3)
grid.save("examples/output/segments_and_arrows.png", dpi=200)
