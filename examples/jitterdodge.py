"""Grouped scatter with position_jitterdodge showing individual observations."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_boxplot,
    geom_point,
    ggplot,
    labs,
    position_jitterdodge,
    scale_color_manual,
    scale_fill_manual,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)

treatments = []
timepoints = []
values = []

for treatment, base in [("Drug A", 12), ("Drug B", 15), ("Placebo", 10)]:
    for tp in ["Week 0", "Week 4", "Week 8"]:
        n = 20
        offset = {"Week 0": 0, "Week 4": 3, "Week 8": 6}[tp]
        vals = rng.normal(base + offset, 2.5, n)
        treatments.extend([treatment] * n)
        timepoints.extend([tp] * n)
        values.extend(vals.tolist())

df = pl.DataFrame({"treatment": treatments, "timepoint": timepoints, "value": values})

colors = {"Drug A": "#42A5F5", "Drug B": "#66BB6A", "Placebo": "#BDBDBD"}

plot = (
    ggplot(df, aes(x="timepoint", y="value", color="treatment", fill="treatment"))
    + geom_boxplot(alpha=0.2, outlier_shape=None)
    + geom_point(
        position=position_jitterdodge(dodge_width=0.75, jitter_width=0.15, seed=42),
        size=20,
        alpha=0.6,
    )
    + scale_color_manual(values=colors)
    + scale_fill_manual(values=colors)
    + labs(
        title="Treatment Response Over Time",
        subtitle="Points jittered within dodge groups to show individual observations",
        x="Timepoint",
        y="Response Value",
        color="Treatment",
        fill="Treatment",
    )
    + theme_minimal()
    + theme(title_size=16)
)

plot.save("examples/output/jitterdodge.png", dpi=200)
