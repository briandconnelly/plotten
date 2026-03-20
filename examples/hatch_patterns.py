"""Hatch patterns -- accessible fill patterns for print and colorblind readers."""

import random

import polars as pl

from plotten import (
    aes,
    geom_col,
    geom_density,
    ggplot,
    labs,
    theme,
    theme_minimal,
)

# --- Example 1: Bars with hatch patterns for print-friendly reading ---
quarterly = pl.DataFrame({"quarter": ["Q1", "Q2", "Q3", "Q4"], "revenue": [120, 145, 160, 180]})

p1 = (
    ggplot(quarterly, aes(x="quarter", y="revenue"))
    + geom_col(fill="#2196F3", hatch="//", alpha=0.9)
    + theme_minimal()
    + theme(title_size=14)
    + labs(
        title="Quarterly Revenue -- readable even in grayscale",
        x="Quarter",
        y="Revenue ($K)",
    )
)

p1.save("examples/output/hatch_grouped_bar.png", dpi=200)

# --- Example 2: Stacked bar with hatch distinguishing segments ---
survey = pl.DataFrame(
    {
        "group": ["Control", "Treatment"],
        "agree": [45, 38],
        "neutral": [20, 25],
        "disagree": [10, 12],
    }
)

p2 = (
    ggplot()
    + geom_col(data=survey, x="group", y="agree", fill="#4CAF50", hatch="//")
    + geom_col(data=survey, x="group", y="neutral", fill="#FFC107", hatch="..")
    + geom_col(data=survey, x="group", y="disagree", fill="#F44336", hatch="xx")
    + theme_minimal()
    + theme(title_size=14)
    + labs(title="Survey Results with Hatch Patterns", x="Group", y="Count")
)

p2.save("examples/output/hatch_stacked_bar.png", dpi=200)

# --- Example 3: Overlapping densities with hatch for clarity ---
random.seed(42)

df_a = pl.DataFrame({"value": [random.gauss(5, 1.5) for _ in range(200)]})
df_b = pl.DataFrame({"value": [random.gauss(7, 1.5) for _ in range(200)]})

p3 = (
    ggplot()
    + geom_density(data=df_a, x="value", color="#3498db", alpha=0.4, hatch="//")
    + geom_density(data=df_b, x="value", color="#e74c3c", alpha=0.4, hatch="\\\\")
    + theme_minimal()
    + theme(title_size=14)
    + labs(
        title="Overlapping Densities -- hatch distinguishes groups in B&W",
        x="Value",
        y="Density",
    )
)

p3.save("examples/output/hatch_density.png", dpi=200)

print("Saved 3 hatch pattern examples to examples/output/")
