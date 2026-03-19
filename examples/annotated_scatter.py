"""Scatter plot with reference lines and text annotations."""

import polars as pl

from plotten import (
    aes,
    annotate,
    geom_hline,
    geom_point,
    geom_vline,
    ggplot,
    labs,
    scale_color_manual,
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
    + annotate("text", x=8.5, y=3.5, label="Threshold", color="gray", size=9)
    + scale_color_manual(values={"A": "#E91E63", "B": "#00BCD4"})
    + labs(
        title="Cluster Analysis",
        subtitle="Dashed lines show decision boundaries",
        x="Feature 1",
        y="Feature 2",
        color="Cluster",
    )
)

plot.save("examples/output/annotated_scatter.png", dpi=200)
