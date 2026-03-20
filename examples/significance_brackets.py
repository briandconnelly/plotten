"""Significance brackets with geom_signif() — statistical comparisons on box plots."""

import random

import polars as pl

from plotten import (
    aes,
    geom_boxplot,
    geom_jitter,
    ggplot,
    labs,
    theme,
    theme_minimal,
)
from plotten.geoms import geom_signif

random.seed(42)

# --- Example 1: Two-group comparison ---
two_group = pl.DataFrame(
    {
        "group": ["Control"] * 30 + ["Treatment"] * 30,
        "score": [random.gauss(50, 10) for _ in range(30)]
        + [random.gauss(58, 10) for _ in range(30)],
    }
)

p1 = (
    ggplot(two_group, aes(x="group", y="score"))
    + geom_boxplot(fill="#74A9CF", alpha=0.7)
    + geom_jitter(width=0.15, alpha=0.3, size=8)
    + geom_signif(comparisons=[("Control", "Treatment")])
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Two-Group Comparison", y="Score")
)

p1.save("examples/output/signif_two_group.png", dpi=200)

# --- Example 2: Multiple comparisons with Bonferroni correction ---
multi_group = pl.DataFrame(
    {
        "treatment": ["Placebo"] * 25 + ["Low Dose"] * 25 + ["High Dose"] * 25,
        "response": (
            [random.gauss(10, 3) for _ in range(25)]
            + [random.gauss(14, 3) for _ in range(25)]
            + [random.gauss(20, 4) for _ in range(25)]
        ),
    }
)

p2 = (
    ggplot(multi_group, aes(x="treatment", y="response"))
    + geom_boxplot(fill="#B2DF8A", alpha=0.7)
    + geom_signif(
        comparisons=[("Placebo", "Low Dose"), ("Placebo", "High Dose"), ("Low Dose", "High Dose")],
        p_adjust="bonferroni",
        step_increase=0.12,
    )
    + theme_minimal()
    + theme(title_size=14)
    + labs(
        title="Dose Response — Bonferroni-corrected p-values",
        x="Treatment Group",
        y="Response",
    )
)

p2.save("examples/output/signif_multi_group.png", dpi=200)

# --- Example 3: Numeric p-value display ---
p3 = (
    ggplot(two_group, aes(x="group", y="score"))
    + geom_boxplot(fill="#FD8D3C", alpha=0.7)
    + geom_signif(
        comparisons=[("Control", "Treatment")],
        text_format="p-value",
    )
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Numeric p-value Display", y="Score")
)

p3.save("examples/output/signif_pvalue_format.png", dpi=200)

print("Saved 3 significance bracket examples to examples/output/")
