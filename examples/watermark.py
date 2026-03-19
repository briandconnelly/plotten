"""Draft watermark overlay on a scatter plot."""

import polars as pl

from plotten import aes, geom_point, geom_smooth, ggplot, labs, theme_minimal, watermark

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y": [2.1, 4.0, 5.8, 8.2, 10.1, 11.9, 14.3, 15.8, 18.0, 20.2],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60, color="#2171B5", alpha=0.8)
    + geom_smooth(method="ols", se=True, color="#E6550D")
    + watermark("DRAFT", alpha=0.15, fontsize=60, rotation=35)
    + theme_minimal()
    + labs(
        title="Preliminary Results",
        subtitle="Data subject to revision",
        x="Predictor",
        y="Response",
    )
)

plot.save("examples/output/watermark.png", dpi=200)
