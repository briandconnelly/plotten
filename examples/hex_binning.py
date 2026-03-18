"""Hexagonal binning for large scatter data."""

import numpy as np
import polars as pl

from plotten import aes, geom_hex, ggplot, labs, theme_minimal

np.random.seed(42)
n = 5000

x = np.concatenate([np.random.normal(0, 1, n), np.random.normal(3, 0.5, n // 2)])
y = np.concatenate([np.random.normal(0, 1, n), np.random.normal(3, 0.5, n // 2)])

df = pl.DataFrame({"x": x.tolist(), "y": y.tolist()})

plot = (
    ggplot(df, aes(x="x", y="y"))
    + geom_hex(bins=25, cmap="YlOrRd")
    + labs(
        title="Hexagonal Binning",
        subtitle="Reveals density structure in 7,500 points",
        x="X",
        y="Y",
    )
    + theme_minimal()
)

plot.save("examples/output/hex_binning.png", dpi=200)
