"""Demonstrate dotplot vs histogram comparison."""

import polars as pl

from plotten import aes, geom_dotplot, ggplot, labs

df = pl.DataFrame(
    {
        "x": [1.0, 1.2, 1.5, 2.0, 2.1, 2.3, 2.4, 2.5, 3.0, 3.1, 3.5, 4.0],
    }
)

plot = (
    ggplot(df, aes(x="x"))
    + geom_dotplot(bins=8, size=80, alpha=0.8)
    + labs(title="Dotplot — Stacked Dots", x="Value", y="Stack Position")
)

plot.save("examples/output/dotplot.png", dpi=200)
