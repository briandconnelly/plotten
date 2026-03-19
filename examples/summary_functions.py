"""Comparing stat_summary with different built-in summary functions."""

import numpy as np
import polars as pl

from plotten import (
    aes,
    ggplot,
    labs,
    stat_summary,
    theme,
    theme_minimal,
)

rng = np.random.default_rng(42)

groups = ["A", "B", "C", "D"]
records: dict[str, list] = {"group": [], "value": []}

for g in groups:
    n = 40
    base = {"A": 10, "B": 15, "C": 12, "D": 18}[g]
    spread = {"A": 2, "B": 4, "C": 3, "D": 5}[g]
    records["group"].extend([g] * n)
    records["value"].extend(rng.normal(base, spread, n).tolist())

df = pl.DataFrame(records)

# --- Panel 1: default mean +/- SE ---
p1 = (
    ggplot(df, aes(x="group", y="value"))
    + stat_summary()
    + labs(title="mean +/- SE (default)")
    + theme_minimal()
    + theme(title_size=14)
)
p1.save("examples/output/summary_mean_se.png", dpi=200)

# --- Panel 2: median_hilow (median + IQR) ---
p2 = (
    ggplot(df, aes(x="group", y="value"))
    + stat_summary(fun_data="median_hilow")
    + labs(title="median_hilow (median + IQR)")
    + theme_minimal()
    + theme(title_size=14)
)
p2.save("examples/output/summary_median_hilow.png", dpi=200)

# --- Panel 3: mean_range (mean + full range) ---
p3 = (
    ggplot(df, aes(x="group", y="value"))
    + stat_summary(fun_data="mean_range")
    + labs(title="mean_range (mean + min/max)")
    + theme_minimal()
    + theme(title_size=14)
)
p3.save("examples/output/summary_mean_range.png", dpi=200)
