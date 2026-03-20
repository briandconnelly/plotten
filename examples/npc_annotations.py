"""NPC annotations -- place annotations in normalized panel coordinates (0-1)."""

import polars as pl

from plotten import (
    aes,
    annotate,
    geom_point,
    geom_smooth,
    ggplot,
    labs,
    theme_minimal,
)

# Scatter plot with annotations that stay fixed regardless of data range
df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y": [2.1, 4.3, 3.8, 7.2, 6.5, 8.1, 7.9, 9.5, 10.2, 11.8],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=50, color="#2171B5")
    + geom_smooth(method="ols", color="#E6550D", size=1)
    # NPC text in top-left corner — always at 5%, 95% of panel
    + annotate(
        "text",
        x=0.05,
        y=0.95,
        label="R² = 0.94",
        coord="npc",
        ha="left",
        va="top",
        size=11,
        box_fill="#FFF9C4",
        box_color="#F9A825",
        box_pad=0.3,
    )
    # NPC text in bottom-right
    + annotate(
        "text",
        x=0.95,
        y=0.05,
        label="n = 10",
        coord="npc",
        ha="right",
        va="bottom",
        size=9,
        color="#666666",
    )
    # NPC bracket across the top 60% of the panel
    + annotate(
        "bracket",
        xmin=0.2,
        xmax=0.8,
        y=0.88,
        coord="npc",
        label="Growth region",
        color="#31A354",
    )
    # NPC segment as a divider line at 50% x
    + annotate(
        "segment",
        x=0.5,
        y=0.0,
        xend=0.5,
        yend=0.15,
        coord="npc",
        color="#999999",
        linetype="--",
    )
    + theme_minimal()
    + labs(
        title="NPC Annotations — fixed positions independent of data range",
        x="X",
        y="Y",
    )
)

plot.save("examples/output/npc_annotations.png", dpi=200)
print("Saved npc_annotations.png")
