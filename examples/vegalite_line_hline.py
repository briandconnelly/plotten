"""Line chart with reference lines, exported as Vega-Lite HTML."""

import polars as pl

from plotten import aes, geom_hline, geom_line, geom_point, ggplot, labs, theme_minimal, to_html

months = list(range(1, 13))

df = pl.DataFrame(
    {
        "month": months,
        "temperature": [2, 4, 9, 14, 19, 23, 26, 25, 20, 14, 8, 3],
    }
)

plot = (
    ggplot(df, aes(x="month", y="temperature"))
    + geom_line(size=2)
    + geom_point(size=40)
    + geom_hline(yintercept=0, color="#D32F2F")
    + theme_minimal()
    + labs(
        title="Monthly Average Temperature",
        subtitle="Red dashed line marks freezing point",
        x="Month",
        y="Temperature (\u00b0C)",
    )
)

html = to_html(plot)
with open("examples/output/vegalite_line_hline.html", "w") as f:
    f.write(html)

print("Wrote examples/output/vegalite_line_hline.html")
