"""Histogram and density curve showing distribution of values."""

import numpy as np
import polars as pl

from plotten import aes, geom_histogram, ggplot, labs, theme_minimal

rng = np.random.default_rng(42)
values = np.concatenate([rng.normal(170, 8, 200), rng.normal(180, 10, 150)])

df = pl.DataFrame({"height": values.tolist()})

plot = (
    ggplot(df, aes(x="height"))
    + geom_histogram(bins=25, alpha=0.7, color="#3F51B5")
    + labs(
        title="Distribution of Heights",
        subtitle="Bimodal distribution from two populations",
        x="Height (cm)",
        y="Count",
    )
    + theme_minimal()
)

plot.save("examples/output/histogram.png", dpi=200)
