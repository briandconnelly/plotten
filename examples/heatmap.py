"""Tile plot (heatmap) with annotations."""

import polars as pl

from plotten import aes, geom_tile, ggplot, labs, scale_fill_viridis, theme, theme_minimal

days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
hours = ["9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm"]

grid_days = [d for d in days for _ in hours]
grid_hours = hours * len(days)
activity = [
    # Mon
    12,
    25,
    45,
    30,
    18,
    42,
    55,
    35,
    # Tue
    15,
    30,
    50,
    28,
    20,
    48,
    60,
    40,
    # Wed
    10,
    22,
    40,
    35,
    25,
    38,
    52,
    30,
    # Thu
    18,
    35,
    55,
    32,
    22,
    50,
    65,
    45,
    # Fri
    8,
    18,
    35,
    25,
    15,
    30,
    42,
    20,
]

df = pl.DataFrame(
    {
        "day": grid_days,
        "hour": grid_hours,
        "activity": activity,
    }
)

plot = (
    ggplot(df, aes(x="day", y="hour", color="activity", label="activity"))
    + geom_tile(text_size=8)
    + scale_fill_viridis(option="magma")
    + theme_minimal()
    + theme(title_size=16, strip_text_size=11)
    + labs(
        title="Weekly Activity Heatmap",
        subtitle="Using viridis magma palette",
        x="Day",
        y="Hour",
        color="Activity",
    )
)

plot.save("examples/output/heatmap.png", dpi=200)
