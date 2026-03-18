"""Empirical CDF comparing two distributions."""

import numpy as np
import polars as pl

from plotten import aes, ggplot, labs, stat_ecdf, theme_minimal

np.random.seed(42)
n = 100

df = pl.DataFrame(
    {
        "score": np.concatenate(
            [
                np.random.normal(70, 10, n),
                np.random.normal(80, 8, n),
            ]
        ).tolist(),
        "group": ["Before Training"] * n + ["After Training"] * n,
    }
)

plot = (
    ggplot(df, aes(x="score", color="group"))
    + stat_ecdf()
    + labs(
        title="Cumulative Distribution of Test Scores",
        subtitle="ECDF shows the shift after training intervention",
        x="Score",
        y="Cumulative Proportion",
        color="Group",
    )
    + theme_minimal()
)

plot.save("examples/output/ecdf_plot.png", dpi=200)
