"""Showcase all annotation features: arrow styles, curved arrows, text boxes, brackets."""

import polars as pl

from plotten import aes, annotate, arrow, geom_line, geom_point, ggplot, labs, theme, theme_minimal

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [2, 4, 3, 7, 5, 8, 6, 9],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_line(color="#cccccc", size=1)
    + geom_point(size=50, color="#2171B5")
    # Curved arrow from point 1 to point 4 (the jump)
    + annotate(
        "curve",
        x=2,
        y=4.3,
        xend=4,
        yend=6.7,
        curvature=0.4,
        arrow=arrow(style="closed", size=1.5),
        color="#E6550D",
    )
    # Text box labeling the peak
    + annotate(
        "text",
        x=8,
        y=9.7,
        label="Peak value",
        box_fill="#FFF9C4",
        box_color="#F9A825",
        box_pad=0.4,
        size=9,
    )
    # Text box with no border
    + annotate(
        "text",
        x=3,
        y=2.2,
        label="Local min",
        box_fill="#E3F2FD",
        size=8,
    )
    # Bracket over the rising section
    + annotate(
        "bracket",
        xmin=4,
        xmax=8,
        y=1.2,
        label="Growth phase",
        color="#31A354",
    )
    # Bracket pointing down over the dip
    + annotate(
        "bracket",
        xmin=2,
        xmax=3,
        y=8,
        label="Dip",
        direction="down",
        color="#E6550D",
    )
    # Simple segment with open arrow
    + annotate(
        "segment",
        x=6.5,
        y=9,
        xend=7.8,
        yend=9,
        arrow=arrow(style="open"),
        color="#777777",
    )
    # Straight segment with fancy arrow style
    + annotate(
        "segment",
        x=1,
        y=8.5,
        xend=1,
        yend=7.3,
        arrow=arrow(style="closed"),
        color="#9C27B0",
    )
    + theme_minimal()
    + theme(title_size=16)
    + labs(
        title="Annotation Showcase",
        subtitle="Curved arrows, text boxes, brackets, and arrow styles",
        x="Time",
        y="Value",
    )
)

plot.save("examples/output/annotation_showcase.png", dpi=200)
