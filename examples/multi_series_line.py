"""Multi-series line chart using automatic group splitting."""

import polars as pl

from plotten import aes, geom_line, ggplot, labs, scale_color_discrete

months = list(range(1, 13))

df = pl.DataFrame(
    {
        "month": months * 3,
        "revenue": [
            12,
            14,
            18,
            22,
            28,
            35,
            38,
            36,
            30,
            24,
            18,
            15,
            8,
            10,
            14,
            18,
            24,
            30,
            33,
            31,
            26,
            20,
            14,
            10,
            5,
            6,
            9,
            12,
            16,
            20,
            22,
            21,
            18,
            13,
            8,
            6,
        ],
        "region": ["North"] * 12 + ["Central"] * 12 + ["South"] * 12,
    }
)

plot = (
    ggplot(df, aes(x="month", y="revenue", color="region"))
    + geom_line(size=2)
    + scale_color_discrete()
    + labs(
        title="Monthly Revenue by Region",
        subtitle="Each region automatically rendered as a separate line",
        x="Month",
        y="Revenue ($k)",
        color="Region",
    )
)

plot.save("examples/output/multi_series_line.png", dpi=200)
