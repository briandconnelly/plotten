"""Demonstrate theme() incremental overrides."""

import polars as pl

from plotten import aes, geom_point, ggplot, labs, theme, theme_minimal

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5],
        "y": [2, 4, 3, 5, 4],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_point(size=60)
    + theme_minimal()
    + theme(title_size=20, axis_text_x_rotation=45, title_color="#2c3e50")
    + labs(title="Theme Composition", x="X Axis", y="Y Axis")
)

plot.save("examples/output/theme_composition.png", dpi=200)
