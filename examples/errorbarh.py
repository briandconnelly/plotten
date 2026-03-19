"""Horizontal error bars showing mean estimates with confidence intervals."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_errorbarh,
    geom_point,
    ggplot,
    labs,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)

categories = ["Treatment A", "Treatment B", "Treatment C", "Placebo"]
means = [7.2, 5.8, 6.5, 3.1]
ci_widths = [1.1, 0.9, 1.4, 0.7]

df = pl.DataFrame(
    {
        "category": categories,
        "mean": means,
        "xmin": [m - w for m, w in zip(means, ci_widths, strict=True)],
        "xmax": [m + w for m, w in zip(means, ci_widths, strict=True)],
    }
)

plot = (
    ggplot(df, aes(y="category", x="mean", xmin="xmin", xmax="xmax"))
    + geom_errorbarh(height=0.3, color="#37474F", linewidth=1.2)
    + geom_point(size=60, color="#E53935")
    + labs(
        title="Treatment Effect Estimates",
        subtitle="Horizontal error bars show 95% confidence intervals",
        x="Effect Size",
        y="",
    )
    + theme_minimal()
    + theme(title_size=16)
)

plot.save("examples/output/errorbarh.png", dpi=200)
