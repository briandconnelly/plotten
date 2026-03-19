"""Dotplot vs histogram comparison showing the same data two ways."""

import numpy as np
import polars as pl

from plotten import aes, geom_dotplot, geom_histogram, ggplot, labs, theme, theme_minimal

rng = np.random.default_rng(42)
values = np.concatenate([rng.normal(3, 0.5, 40), rng.normal(5, 0.8, 30)]).tolist()

df = pl.DataFrame({"x": values})

p1 = (
    ggplot(df, aes(x="x"))
    + geom_dotplot(bins=20, size=40, alpha=0.7, color="#2171B5")
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Dotplot", subtitle="Each dot is one observation", x="Value", y="Stack Position")
)

p2 = (
    ggplot(df, aes(x="x"))
    + geom_histogram(bins=20, alpha=0.7, color="#2171B5")
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Histogram", subtitle="Same data, binned into bars", x="Value", y="Count")
)

grid = p1 | p2
grid.save("examples/output/dotplot.png", dpi=200)
