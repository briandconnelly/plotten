"""Rectangle geom for highlighting regions on a plot."""

import polars as pl

from plotten import geom_point, geom_rect, ggplot, labs

# Scatter plot with highlighted rectangular regions
points_df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 3, 5, 7, 2, 8],
        "y": [3, 5, 4, 8, 6, 9, 7, 10, 8, 12, 6, 7, 9, 4, 11],
    }
)

regions_df = pl.DataFrame(
    {
        "xmin": [1.5, 5.5],
        "xmax": [4.5, 8.5],
        "ymin": [2.5, 6.5],
        "ymax": [6.5, 10.5],
    }
)

plot = (
    ggplot()
    + geom_rect(
        data=regions_df,
        xmin="xmin",
        xmax="xmax",
        ymin="ymin",
        ymax="ymax",
        fill="#3498DB",
        alpha=0.15,
        color="#2980B9",
    )
    + geom_point(data=points_df, x="x", y="y", size=50, color="#E74C3C", alpha=0.8)
    + labs(
        title="Scatter Plot with Highlighted Regions",
        x="X",
        y="Y",
    )
)

plot.save("examples/output/rect_regions.png", dpi=200)
