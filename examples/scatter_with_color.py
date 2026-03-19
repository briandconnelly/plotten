"""Scatter plot with continuous color mapping and custom labels."""

import polars as pl

from plotten import aes, geom_point, ggplot, labs, scale_color_continuous

df = pl.DataFrame(
    {
        "engine_size": [1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 5.7, 6.2, 2.0, 2.4, 3.6, 4.6, 1.8],
        "horsepower": [130, 155, 182, 220, 268, 300, 390, 420, 460, 148, 175, 260, 345, 140],
        "mpg": [32, 29, 26, 22, 19, 17, 14, 13, 11, 30, 27, 20, 15, 31],
    }
)

plot = (
    ggplot(df, aes(x="engine_size", y="horsepower", color="mpg"))
    + geom_point(size=80, alpha=0.8)
    + scale_color_continuous(cmap="RdYlGn")
    + labs(
        title="Engine Size vs Horsepower",
        subtitle="Color shows fuel efficiency (MPG)",
        caption="Source: synthetic automotive dataset",
        x="Engine Displacement (L)",
        y="Horsepower",
        color="MPG",
    )
)

plot.save("examples/output/scatter_with_color.png", dpi=200)
