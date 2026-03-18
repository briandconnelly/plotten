"""Step plots and rug marks for time series and distribution visualization."""

import polars as pl

from plotten import aes, geom_point, geom_rug, geom_step, ggplot, labs

# Step plot — good for showing discrete changes over time
step_df = pl.DataFrame(
    {
        "day": list(range(1, 11)),
        "price": [10.0, 10.0, 12.5, 12.5, 11.0, 15.0, 15.0, 13.5, 16.0, 16.0],
    }
)

step_plot = (
    ggplot(step_df, aes(x="day", y="price"))
    + geom_step(color="steelblue", size=1.5)
    + geom_point(color="steelblue", size=30)
    + labs(title="Stock Price (Step Plot)", x="Trading Day", y="Price ($)")
)

step_plot.save("examples/output/step_plot.png", dpi=200)

# Scatter with rug marks showing marginal distributions
scatter_df = pl.DataFrame(
    {
        "height": [
            160,
            165,
            168,
            170,
            172,
            175,
            178,
            180,
            182,
            185,
            163,
            167,
            171,
            174,
            177,
            179,
            183,
            186,
            169,
            176,
        ],
        "weight": [
            55,
            60,
            63,
            68,
            70,
            75,
            78,
            82,
            85,
            90,
            57,
            62,
            66,
            71,
            73,
            80,
            84,
            88,
            65,
            76,
        ],
    }
)

rug_plot = (
    ggplot(scatter_df, aes(x="height", y="weight"))
    + geom_point(size=40, alpha=0.7, color="#E74C3C")
    + geom_rug(sides="bl", alpha=0.4, color="#2C3E50")
    + labs(
        title="Height vs Weight with Rug Marks",
        x="Height (cm)",
        y="Weight (kg)",
    )
)

rug_plot.save("examples/output/scatter_with_rug.png", dpi=200)
