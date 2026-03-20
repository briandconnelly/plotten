"""Automatic number formatting that adapts to magnitude."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_col,
    geom_point,
    ggplot,
    label_number_auto,
    label_si,
    labs,
    scale_x_continuous,
    scale_y_continuous,
    theme_minimal,
)
from plotten._composition import plot_grid

# --- label_number_auto: "just make it look good" ---

# Mixed-magnitude data that's hard to format with a single formatter
df_mixed = pl.DataFrame(
    {
        "metric": ["Error Rate", "Latency", "Cache Hit", "Daily Users", "Revenue"],
        "value": [0.003, 2.45, 847, 52_000, 3_200_000],
    }
)

p_auto = (
    ggplot(df_mixed, aes(x="metric", y="value"))
    + geom_col(fill="#2171B5", alpha=0.8)
    + scale_y_continuous(labels=label_number_auto())
    + labs(
        title="label_number_auto()",
        subtitle="Adapts format to each tick's magnitude",
        x="",
        y="Value",
    )
    + theme_minimal()
)

# Compare auto vs SI for large values
rng = np.random.default_rng(42)
df_scatter = pl.DataFrame(
    {
        "population": (rng.uniform(50_000, 10_000_000, 40)).tolist(),
        "gdp": (rng.uniform(1_000_000, 5_000_000_000, 40)).tolist(),
    }
)

p_si = (
    ggplot(df_scatter, aes(x="population", y="gdp"))
    + geom_point(alpha=0.6, color="#E6550D")
    + scale_x_continuous(labels=label_si())
    + scale_y_continuous(labels=label_si())
    + labs(title="label_si()", x="Population", y="GDP")
    + theme_minimal()
)

p_auto_scatter = (
    ggplot(df_scatter, aes(x="population", y="gdp"))
    + geom_point(alpha=0.6, color="#31A354")
    + scale_x_continuous(labels=label_number_auto())
    + scale_y_continuous(labels=label_number_auto())
    + labs(title="label_number_auto()", x="Population", y="GDP")
    + theme_minimal()
)

# Small values
df_small = pl.DataFrame(
    {
        "experiment": ["A", "B", "C", "D", "E"],
        "effect_size": [0.002, 0.015, 0.14, 0.85, 3.2],
    }
)

p_small = (
    ggplot(df_small, aes(x="experiment", y="effect_size"))
    + geom_col(fill="#756BB1", alpha=0.8)
    + scale_y_continuous(labels=label_number_auto())
    + labs(
        title="Small Values",
        subtitle="Decimals and scientific notation",
        x="",
        y="Effect Size",
    )
    + theme_minimal()
)

grid = plot_grid(p_auto, p_small, p_si, p_auto_scatter, ncol=2)
grid.save("examples/output/label_number_auto.png", dpi=200)
