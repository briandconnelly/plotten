"""Polygon geom for drawing shapes."""

import polars as pl

from plotten import aes, geom_polygon, ggplot, labs, theme_minimal

# Draw a simple star shape using two overlapping triangles
df = pl.DataFrame(
    {
        "x": [
            0.0,
            1.0,
            0.5,
            0.0,
            1.0,
            0.5,
        ],
        "y": [
            0.0,
            0.0,
            0.87,
            0.58,
            0.58,
            -0.29,
        ],
        "shape": ["up", "up", "up", "down", "down", "down"],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y", group="shape"))
    + geom_polygon(fill="#FFD700", color="#B8860B", alpha=0.7)
    + labs(title="Polygon Geom", subtitle="Two triangles drawn with geom_polygon")
    + theme_minimal()
)

plot.save("examples/output/polygon_map.png", dpi=200)
