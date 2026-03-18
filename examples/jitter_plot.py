"""Jitter plot for visualizing overlapping categorical data."""

import random

import polars as pl

from plotten import aes, geom_jitter, ggplot, labs

random.seed(42)
groups = ["Control", "Treatment A", "Treatment B"] * 20
values = (
    [random.gauss(5, 1) for _ in range(20)]
    + [random.gauss(7, 1.2) for _ in range(20)]
    + [random.gauss(6, 0.8) for _ in range(20)]
)

df = pl.DataFrame({"group": groups, "score": values})

plot = (
    ggplot(df, aes(x="group", y="score"))
    + geom_jitter(width=0.2, height=0, seed=42, size=40, alpha=0.6, color="steelblue")
    + labs(
        title="Experiment Results",
        subtitle="Jittered points reveal distribution within groups",
        x="Group",
        y="Score",
    )
)

plot.save("examples/output/jitter_plot.png", dpi=200)
