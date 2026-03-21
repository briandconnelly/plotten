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
    geom_label_repel,
    geom_point,
    geom_smooth,
    geom_text_repel,
    ggplot,
    labs,
    plot_annotation,
    scale_color_brewer,
    theme,
    theme_bw,
    theme_minimal,
)
from plotten.datasets import load_dataset

OUT = "docs/images"

# ── Hero ─────────────────────────────────────────────────────────────────────

mpg = load_dataset("mpg")

hero = (
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.7)
    + geom_smooth(method="ols")
    + scale_color_brewer(palette="Set2")
    + labs(
        title="Engine displacement vs. highway MPG",
        x="Displacement (L)",
        y="Highway MPG",
        color="Vehicle class",
    )
    + theme_minimal()
)
hero.save(f"{OUT}/hero.png", width=8, height=5, dpi=150)
print(f"Saved {OUT}/hero.png")

# ── geom_text_repel ───────────────────────────────────────────────────────────

repel_df = pl.DataFrame(
    {
        "x": [1.0, 1.2, 1.1, 3.0, 3.1, 5.0, 5.2, 5.1, 7.0, 7.1],
        "y": [2.0, 2.1, 1.9, 4.0, 4.2, 3.0, 3.1, 2.8, 5.0, 5.1],
        "name": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon",
                  "Zeta", "Eta", "Theta", "Iota", "Kappa"],
    }
)

repel = (
    ggplot(repel_df, aes(x="x", y="y"))
    + geom_point(size=30, color="#2c3e50")
    + geom_label_repel(label="name", fill="lightyellow", color="#34495e",
                       size=8, segment_color="#95a5a6")
    + theme_minimal()
    + labs(title="geom_label_repel — boxed labels with connectors", x="X", y="Y")
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
        title="Density histogram via after_stat(\"density\")",
        x="Value",
        y="Density",
    )
    + theme_minimal()
)
computed.save(f"{OUT}/computed_aesthetics.png", width=6, height=4, dpi=150)
print(f"Saved {OUT}/computed_aesthetics.png")

# ── Faceted scatter ───────────────────────────────────────────────────────────

study_df = pl.DataFrame(
    {
        "study_hours": [1, 2, 3, 4, 5, 6, 7, 8] * 3,
        "score": [
            45, 52, 58, 65, 70, 78, 82, 90,
            50, 55, 62, 68, 75, 80, 88, 95,
            40, 48, 55, 60, 64, 72, 76, 85,
        ],
        "subject": ["Math"] * 8 + ["Science"] * 8 + ["English"] * 8,
    }
)

faceted = (
    ggplot(study_df, aes(x="study_hours", y="score"))
    + geom_point(size=40, alpha=0.7)
    + geom_smooth(method="ols", se=True)
    + facet_wrap("subject", ncol=3)
    + theme_bw()
    + theme(strip_background="#E8EAF6", strip_text_color="#283593")
    + labs(
        title="Study hours vs. test scores",
        subtitle="Faceted by subject",
        x="Hours studied per day",
        y="Test score",
    )
)
faceted.save(f"{OUT}/faceted_scatter.png", width=9, height=7, dpi=150)
print(f"Saved {OUT}/faceted_scatter.png")

# ── Ridge plot ────────────────────────────────────────────────────────────────

ridge = (
    ggplot(mpg, aes(x="hwy", y="class"))
    + geom_density_ridges(alpha=0.7, fill="#4C72B0")
    + labs(
        title="Highway MPG by vehicle class",
        subtitle="Ridge plot — one distribution per class",
        x="Highway MPG",
        y=None,
    )
    + theme_minimal()
    + theme(axis_text_y_size=11)
)
ridge.save(f"{OUT}/ridge_plot.png", width=8, height=5, dpi=150)
print(f"Saved {OUT}/ridge_plot.png")

# ── Composition ───────────────────────────────────────────────────────────────

p1 = (
    ggplot(mpg, aes(x="displ", y="hwy", color="class"))
    + geom_point(alpha=0.6)
    + scale_color_brewer(palette="Set2")
    + labs(title="Displacement vs MPG", x="Displacement (L)", y="Highway MPG")
    + theme_minimal()
)

p2 = (
    ggplot(mpg, aes(x="hwy"))
    + geom_histogram(bins=20, alpha=0.8, color="#3F51B5")
    + labs(title="Highway MPG distribution", x="Highway MPG", y="Count")
    + theme_minimal()
)

composition = (p1 | p2) + plot_annotation(
    title="plotten — composable plots",
    tag_levels="A",
)
composition.save(f"{OUT}/composition.png", width=12, height=5, dpi=150)
print(f"Saved {OUT}/composition.png")
