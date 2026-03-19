"""Showcase curved arrows, brackets, text boxes, and arrow styles."""

import polars as pl

from plotten import aes, annotate, arrow, geom_point, ggplot, labs

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5],
        "y": [2, 4, 3, 5, 4],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60)
    + annotate("curve", x=1, y=2, xend=3, yend=3, curvature=0.4, arrow=arrow(style="closed"))
    + annotate("text", x=4, y=5.3, label="Peak", box_fill="lightyellow", box_color="gray")
    + annotate("bracket", xmin=2, xmax=4, y=1.5, label="Middle Group")
    + annotate("segment", x=4.5, y=4.5, xend=5, yend=4, arrow=arrow(style="open"))
    + labs(title="Annotation Showcase", x="X", y="Y")
)

plot.save("examples/output/annotation_showcase.png", dpi=200)
