"""Line chart with a confidence ribbon."""

import polars as pl

from plotten import aes, geom_line, geom_ribbon, ggplot, labs, theme_dark

months = list(range(1, 13))
temps = [2, 4, 9, 14, 19, 23, 25, 24, 20, 14, 8, 3]
lo = [t - 3 for t in temps]
hi = [t + 3 for t in temps]

df = pl.DataFrame(
    {
        "month": months,
        "temp": temps,
        "temp_lo": lo,
        "temp_hi": hi,
    }
)

plot = (
    ggplot(df, aes(x="month", y="temp"))
    + geom_ribbon(ymin="temp_lo", ymax="temp_hi", alpha=0.25, color="#64B5F6")
    + geom_line(color="#1565C0", size=2)
    + labs(
        title="Average Monthly Temperature",
        subtitle="Shaded band shows typical range",
        x="Month",
        y="Temperature (\u00b0C)",
    )
    + theme_dark()
)

plot.save("examples/output/line_with_ribbon.png", dpi=200)
