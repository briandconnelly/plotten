"""Demonstrate all viridis palette options."""

import polars as pl

from plotten import aes, geom_point, ggplot, labs, scale_color_viridis

df = pl.DataFrame(
    {
        "x": list(range(50)),
        "y": [i * 0.5 + (i % 7) for i in range(50)],
        "value": [float(i) for i in range(50)],
    }
)

plot = (
    ggplot(df, aes(x="x", y="y", color="value"))
    + geom_point(size=60)
    + scale_color_viridis(option="plasma")
    + labs(title="Viridis Plasma Palette", color="Value")
)

plot.save("examples/output/viridis_scales.png", dpi=200)
