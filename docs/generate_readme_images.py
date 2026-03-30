"""Generate images used in README.md.

Run from the project root:
    uv run python docs/generate_readme_images.py
"""

from __future__ import annotations

import numpy as np
import polars as pl

from plotten import (
    aes,
    after_stat,
    facet_wrap,
    geom_density_ridges,
    geom_histogram,
    geom_point,
    geom_smooth,
    geom_text_repel,
    ggplot,
    labs,
)
from plotten.datasets import load_dataset

OUT = "docs/images"

# ── Hero ─────────────────────────────────────────────────────────────────────

mpg = load_dataset("mpg")

hero = (
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.7)
    + geom_smooth(method="ols")
    + labs(
        title="Engine displacement vs. highway MPG",
        subtitle="Seven vehicle classes, model years 1999-2008",
        caption="Source: ggplot2::mpg",
        x="Displacement (L)",
        y="Highway MPG",
    )
)
hero.save(f"{OUT}/hero.png", width=8, height=5, dpi=150)
print(f"Saved {OUT}/hero.png")

# ── geom_text_repel ───────────────────────────────────────────────────────────

repel_df = pl.DataFrame(
    {
        "x": [1.0, 1.2, 1.1, 3.0, 3.1, 5.0, 5.2, 5.1, 7.0, 7.1],
        "y": [2.0, 2.1, 1.9, 4.0, 4.2, 3.0, 3.1, 2.8, 5.0, 5.1],
        "name": [
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Epsilon",
            "Zeta",
            "Eta",
            "Theta",
            "Iota",
            "Kappa",
        ],
    }
)

repel = (
    ggplot(repel_df, aes(x="x", y="y", label="name"))
    + geom_point(size=30, color="#2c3e50")
    + geom_text_repel()
    + labs(title="geom_text_repel — automatic label placement", x="X", y="Y")
)
repel.save(f"{OUT}/label_repel.png", width=6, height=4, dpi=150)
print(f"Saved {OUT}/label_repel.png")

# ── Computed aesthetics ───────────────────────────────────────────────────────

rng = np.random.default_rng(42)
values = rng.standard_normal(500).tolist()
hist_df = pl.DataFrame({"x": values})

computed = (
    ggplot(hist_df, aes(x="x", y=after_stat("density")))
    + geom_histogram(bins=25, alpha=0.8, color="#3F51B5")
    + labs(
        title='Density histogram via after_stat("density")',
        x="Value",
        y="Density",
    )
)
computed.save(f"{OUT}/computed_aesthetics.png", width=6, height=4, dpi=150)
print(f"Saved {OUT}/computed_aesthetics.png")

# ── Faceted scatter ───────────────────────────────────────────────────────────

faceted = (
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(mapping=aes(color="drv"), alpha=0.6)
    + geom_smooth(method="loess")
    + facet_wrap("class", ncol=3)
)
faceted.save(f"{OUT}/faceted_scatter.png", width=9, height=7, dpi=150)
print(f"Saved {OUT}/faceted_scatter.png")

# ── Ridge plot ────────────────────────────────────────────────────────────────

ridge = ggplot(mpg, aes(x="hwy", y="class")) + geom_density_ridges(alpha=0.8)
ridge.save(f"{OUT}/ridge_plot.png", width=8, height=5, dpi=150)
print(f"Saved {OUT}/ridge_plot.png")

# ── Composition ───────────────────────────────────────────────────────────────

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.6)
    + labs(title="Displacement vs MPG", x="Displacement (L)", y="Highway MPG")
)

p2 = (
    ggplot(mpg, aes(x="hwy"))
    + geom_histogram(bins=20, alpha=0.8, color="#3F51B5")
    + labs(title="Highway MPG distribution", x="Highway MPG", y="Count")
)

composition = p1 | p2
composition.save(f"{OUT}/composition.png", width=12, height=5, dpi=150)
print(f"Saved {OUT}/composition.png")
