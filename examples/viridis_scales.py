"""Demonstrate all five viridis palette options side by side."""

import polars as pl

from plotten import aes, geom_point, ggplot, labs, scale_color_viridis, theme, theme_minimal

n = 40
df = pl.DataFrame(
    {
        "x": list(range(n)),
        "y": [i * 0.5 + (i % 7) for i in range(n)],
        "value": [float(i) for i in range(n)],
    }
)

palettes = ["viridis", "magma", "inferno", "plasma", "cividis"]
plots = []

for name in palettes:
    p = (
        ggplot(df, aes(x="x", y="y", color="value"))
        + geom_point(size=50)
        + scale_color_viridis(option=name)
        + theme_minimal()
        + theme(title_size=14, title_color="#333333")
        + labs(title=name.capitalize(), color="Value")
    )
    plots.append(p)

# 3 on top, 2 on bottom
top_row = plots[0] | plots[1] | plots[2]
bottom_row = plots[3] | plots[4]
grid = top_row / bottom_row
grid.save("examples/output/viridis_scales.png", dpi=200)
