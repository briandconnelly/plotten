"""Using geom_blank() to enforce consistent axis limits across panels."""

import polars as pl

from plotten import (
    aes,
    facet_wrap,
    geom_blank,
    geom_point,
    ggplot,
    labs,
    theme_minimal,
)

# Two groups with very different ranges
df = pl.DataFrame(
    {
        "x": [1, 2, 3, 10, 20, 30],
        "y": [5, 10, 15, 50, 100, 150],
        "group": ["A", "A", "A", "B", "B", "B"],
    }
)

# geom_blank with sentinel data forces axes to include the full range
# even when faceting with free scales
sentinel = pl.DataFrame({"x": [0, 35], "y": [0, 160], "group": ["A", "B"]})

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=3)
    + geom_blank(data=sentinel)
    + facet_wrap("group")
    + labs(
        title="Consistent Axes via geom_blank()",
        subtitle="Invisible sentinel data expands the axis range",
    )
    + theme_minimal()
)

plot.save("examples/output/geom_blank.png", dpi=200)
