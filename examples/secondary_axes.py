"""Dual-axis plot using sec_axis for temperature conversion."""

import polars as pl

from plotten import (
    aes,
    geom_line,
    geom_point,
    ggplot,
    labs,
    scale_y_continuous,
    sec_axis,
    theme_bw,
)

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# Average temperatures in °C for a temperate city
temps_c = [-2, 0, 5, 11, 17, 21, 24, 23, 18, 12, 5, 0]

df = pl.DataFrame({"month": list(range(12)), "temp_c": temps_c})

plot = (
    ggplot(df, aes(x="month", y="temp_c"))
    + geom_line(color="#E91E63", linewidth=2)
    + geom_point(color="#E91E63", size=5)
    + scale_y_continuous(
        sec_axis=sec_axis(
            trans=lambda c: c * 9 / 5 + 32,
            inverse=lambda f: (f - 32) * 5 / 9,
            name="Temperature (°F)",
        ),
    )
    + labs(
        title="Average Monthly Temperature",
        subtitle="Primary axis in Celsius, secondary in Fahrenheit",
        x="Month",
        y="Temperature (°C)",
    )
    + theme_bw()
)

plot.save("examples/output/secondary_axes.png", dpi=200)
