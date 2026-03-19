"""Frequency polygon overlaid on histogram with color grouping."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    geom_freqpoly,
    geom_histogram,
    ggplot,
    labs,
    scale_color_manual,
    scale_fill_manual,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)

species_a = rng.normal(50, 8, 300)
species_b = rng.normal(65, 10, 250)

df = pl.DataFrame(
    {
        "weight": [*species_a.tolist(), *species_b.tolist()],
        "species": ["Adelie"] * 300 + ["Gentoo"] * 250,
    }
)

colors = {"Adelie": "#E57373", "Gentoo": "#64B5F6"}

plot = (
    ggplot(df, aes(x="weight", fill="species", color="species"))
    + geom_histogram(bins=30, alpha=0.35)
    + geom_freqpoly(bins=30, size=1.4)
    + scale_fill_manual(values=colors)
    + scale_color_manual(values=colors)
    + labs(
        title="Body Weight Distribution by Species",
        subtitle="Frequency polygon overlaid on histogram",
        x="Weight (g)",
        y="Count",
        fill="Species",
        color="Species",
    )
    + theme_minimal()
    + theme(title_size=16)
)

plot.save("examples/output/freqpoly.png", dpi=200)
