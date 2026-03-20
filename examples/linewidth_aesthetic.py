"""Linewidth aesthetic — independent control of line width and point size."""

import polars as pl

from plotten import (
    aes,
    geom_line,
    geom_point,
    ggplot,
    labs,
    scale_linewidth_continuous,
    theme_minimal,
)

# Time series where line thickness encodes confidence level
df = pl.DataFrame(
    {
        "month": list(range(1, 13)) * 3,
        "revenue": [
            10,
            12,
            15,
            14,
            18,
            22,
            25,
            23,
            20,
            19,
            24,
            28,
            8,
            9,
            11,
            13,
            12,
            15,
            17,
            16,
            14,
            13,
            16,
            19,
            5,
            6,
            7,
            8,
            10,
            11,
            13,
            12,
            11,
            10,
            12,
            14,
        ],
        "confidence": [
            0.9,
            0.85,
            0.8,
            0.82,
            0.88,
            0.92,
            0.95,
            0.93,
            0.87,
            0.84,
            0.9,
            0.94,
            0.7,
            0.72,
            0.75,
            0.78,
            0.74,
            0.8,
            0.83,
            0.81,
            0.76,
            0.73,
            0.79,
            0.82,
            0.6,
            0.62,
            0.65,
            0.68,
            0.7,
            0.72,
            0.75,
            0.73,
            0.7,
            0.67,
            0.71,
            0.74,
        ],
        "product": ["Widget A"] * 12 + ["Widget B"] * 12 + ["Widget C"] * 12,
    }
)

# linewidth maps to confidence (thicker = more confident)
plot = (
    ggplot(df, aes(x="month", y="revenue", color="product"))
    + geom_line(linewidth="confidence", alpha=0.8)
    + geom_point(size=20, alpha=0.7)
    + scale_linewidth_continuous(range=(0.5, 3.5))
    + theme_minimal()
    + labs(
        title="Revenue by Product — linewidth encodes confidence",
        x="Month",
        y="Revenue ($K)",
    )
)

plot.save("examples/output/linewidth_aesthetic.png", dpi=200)
print("Saved linewidth_aesthetic.png")
