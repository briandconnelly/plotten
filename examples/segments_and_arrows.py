"""Segment and arrow geoms for network-style and annotation plots."""

import polars as pl

from plotten import geom_point, geom_segment, ggplot, labs

# Network-style plot with arrows
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

plot = (
    ggplot()
    + geom_segment(data=edges, x="x", y="y", xend="xend", yend="yend", arrow=True, size=1.2)
    + geom_point(data=nodes, x="x", y="y", size=120, color="steelblue", alpha=0.9)
    + labs(title="Network Graph with Arrows", x="", y="")
)

plot.save("examples/output/segments_and_arrows.png", dpi=200)
