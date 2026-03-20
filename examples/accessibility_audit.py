"""Accessibility audit — check colorblind safety, contrast, and font sizes."""

import polars as pl

from plotten import (
    accessibility_report,
    aes,
    geom_point,
    ggplot,
    labs,
    scale_color_manual,
    theme,
    theme_minimal,
)

# --- Example 1: A plot with problematic red/green palette ---

df = pl.DataFrame(
    {
        "x": [1, 2, 3, 4, 5, 6],
        "y": [3, 5, 2, 7, 4, 6],
        "group": ["A", "A", "A", "B", "B", "B"],
    }
)

bad_plot = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=80)
    + scale_color_manual(values={"A": "#907040", "B": "#509040"})  # brown vs green
    + theme_minimal()
    + labs(title="Brown vs Green — confusable under protanopia")
)

print("=== Audit: red/green palette ===")
report = accessibility_report(bad_plot)
print(report)
print()

# --- Example 2: Low contrast + tiny fonts ---

low_contrast_plot = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=80)
    + scale_color_manual(values={"A": "#3498db", "B": "#e67e22"})
    + theme_minimal()
    + theme(
        title_color="#cccccc",  # Light gray title on white — low contrast
        title_size=5,  # Extremely small
        tick_size=4,  # Too small
    )
    + labs(title="Hard to read")
)

print("=== Audit: low contrast + tiny fonts ===")
report2 = accessibility_report(low_contrast_plot)
print(report2)
print()

# --- Example 3: A well-designed plot ---

good_plot = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point(size=80)
    + scale_color_manual(values={"A": "#0072B2", "B": "#D55E00"})  # colorblind-safe
    + theme_minimal()
    + labs(title="Colorblind-safe palette")
)

print("=== Audit: colorblind-safe palette ===")
report3 = accessibility_report(good_plot)
print(report3)
