"""Scatter plot with annotations using text boxes, curved arrows, and brackets."""

import polars as pl

from plotten import (
    aes,
    annotate,
    arrow,
    geom_hline,
    geom_point,
    geom_vline,
    ggplot,
    labs,
    scale_color_manual,
    theme,
    theme_minimal,
)

df = pl.DataFrame(
    {
        "x": [1.2, 2.5, 3.1, 4.8, 5.5, 6.2, 7.0, 8.3, 3.8, 6.8, 2.0, 9.0, 4.5, 7.5],
        "y": [3.5, 5.0, 4.2, 7.8, 6.5, 8.1, 7.0, 9.2, 5.5, 8.8, 4.0, 9.5, 6.0, 7.2],
        "group": [
            "A",
            "A",
            "A",
            "B",
            "B",
            "B",
            "B",
            "B",
            "A",
            "B",
            "A",
            "B",
            "A",
            "B",
        ],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=60, alpha=0.8)
    + geom_hline(yintercept=6.5, linestyle="dashed", color="gray", alpha=0.6)
    + geom_vline(xintercept=5.0, linestyle="dashed", color="gray", alpha=0.6)
    # Text box annotation instead of plain text
    + annotate(
        "text",
        x=8.5,
        y=3.5,
        label="Threshold",
        box_fill="#f0f0f0",
        box_color="#999999",
        box_pad=0.3,
        color="gray",
        size=9,
    )
    # Curved arrow pointing to the outlier
    + annotate(
        "curve",
        x=7.5,
        y=10.5,
        xend=9,
        yend=9.7,
        curvature=-0.3,
        arrow=arrow(style="closed"),
        color="#E91E63",
    )
    + annotate(
        "text",
        x=7.5,
        y=10.8,
        label="Outlier",
        box_fill="#FCE4EC",
        size=8,
        color="#E91E63",
    )
    # Bracket over cluster B region
    + annotate(
        "bracket",
        xmin=4.5,
        xmax=9.0,
        y=3.0,
        label="Cluster B",
        color="#00BCD4",
    )
    + scale_color_manual(values={"A": "#E91E63", "B": "#00BCD4"})
    + theme_minimal()
    + theme(title_size=16)
    + labs(
        title="Cluster Analysis",
        subtitle="Annotated with curved arrows, text boxes, and brackets",
        x="Feature 1",
        y="Feature 2",
        color="Cluster",
    )
)

plot.save("examples/output/annotated_scatter.png", dpi=200)
